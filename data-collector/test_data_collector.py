import base64
import os
from unittest.mock import MagicMock, patch
import uuid

from dotenv import load_dotenv
from consumer import callback
from collector import (
    create_job,
    get_fantasy_stats,
    mark_job_complete,
    save_data_to_database,
    update_statistics,
)

load_dotenv()

API_KEY = os.getenv("API_KEY")
FANTASY_STATS_API_URL = "https://api.mysportsfeeds.com/v2.1/pull/nfl/2026-2027-regular/week/1/dfs_projections.json"

test_fantasy_stats = {
    "lastUpdatedOn": "2026-08-05T22:51:26.795Z",
    "projections": [
        {
            "player": {
                "id": 13349,
                "firstName": "Patrick",
                "lastName": "Mahomes",
                "position": "QB",
                "jerseyNumber": 15,
            },
            "team": {"id": 73, "abbreviation": "KC"},
            "game": {
                "id": 163556,
                "startTime": "2026-09-15T00:15:00.000Z",
                "awayTeamAbbreviation": "DEN",
                "homeTeamAbbreviation": "KC",
            },
            "fantasyPoints": [
                {"source": "DraftKings", "points": 13.039999961853027},
                {"source": "FanDuel", "points": 13.039999961853027},
                {"source": "FantasyDraft", "points": 13.039999961853027},
                {"source": "Yahoo", "points": 13.039999961853027},
            ],
        }
    ],
    "references": None,
}


def test_callback():
    testTag = "testtag"
    ch = MagicMock()
    method = MagicMock()
    method.delivery_tag = testTag

    with patch("consumer.update_statistics") as mock_update, patch(
        "consumer.get_db_connection_with_retries"
    ) as mock_db:
        mock_db_connection = MagicMock()
        mock_db.return_value = mock_db_connection

        jobId = str(uuid.uuid4()).encode()

        callback(ch, method, None, jobId)

        mock_db.assert_called_once()
        mock_update.assert_called_once_with(jobId.decode(), mock_db_connection)
        ch.basic_ack.assert_called_once_with(delivery_tag=testTag)


def test_create_job():
    jobId = str(uuid.uuid4()).encode()
    connection = MagicMock()

    create_job(jobId, connection)

    sql = "INSERT INTO jobs (job_id, status) VALUES (%s, %s)"
    connection.cursor().execute.assert_called_once_with(sql, (jobId, "executing"))
    connection.commit.assert_called_once()


def test_mark_job_complete():
    jobId = str(uuid.uuid4()).encode()
    connection = MagicMock()

    mark_job_complete(jobId, connection)

    sql = "UPDATE jobs SET status = %s WHERE job_id = %s"
    connection.cursor().execute.assert_called_once_with(sql, ("complete", jobId))
    connection.commit.assert_called_once()


def test_save_data_to_database():
    row_to_insert = [(13349, "Patrick", "Mahomes", "QB", "KC", 13.039999961853027)]
    connection = MagicMock()

    with patch("collector.execute_values") as mock_execute_values:
        save_data_to_database(test_fantasy_stats, connection)

        delete_sql = "DELETE FROM player_projections WHERE 1=1"
        connection.cursor().execute.assert_called_once_with(delete_sql)

        insert_sql = """
        INSERT INTO player_projections (
            id,
            first_name,
            last_name,
            position,
            team,
            projected_points
        ) VALUES %s
    """
        mock_execute_values.assert_called_once_with(
            connection.cursor(), insert_sql, row_to_insert
        )

        assert connection.commit.call_count == 2


def test_get_fantasy_stats():
    with patch("collector.requests.get") as mock_get_request:
        mock_json_return_value = MagicMock()
        mock_json_return_value.json.return_value = test_fantasy_stats
        mock_get_request.return_value = mock_json_return_value

        result = get_fantasy_stats()

        credentials = base64.b64encode(f"{API_KEY}:MYSPORTSFEEDS".encode()).decode(
            "utf-8"
        )
        mock_get_request.assert_called_once_with(
            FANTASY_STATS_API_URL,
            params={"position": "qb"},
            headers={"Authorization": "Basic " + credentials},
        )
        assert result == test_fantasy_stats


def test_update_statistics() -> None:
    with patch("collector.create_job") as mock_create_job, patch(
        "collector.get_fantasy_stats"
    ) as mock_get_fantasy_stats, patch(
        "collector.save_data_to_database"
    ) as mock_save_data_to_database, patch(
        "collector.mark_job_complete"
    ) as mock_mark_job_complete:
        jobId = str(uuid.uuid4())
        connection = MagicMock()

        update_statistics(jobId, connection)

        mock_create_job.assert_called_once_with(jobId, connection)
        mock_get_fantasy_stats.assert_called_once()
        mock_save_data_to_database.assert_called_once_with(
            mock_get_fantasy_stats.return_value, connection
        )
        mock_mark_job_complete.assert_called_once_with(jobId, connection)
