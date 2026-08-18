import base64
import json
import os
from unittest.mock import MagicMock, call, patch
import uuid

from dotenv import load_dotenv
from consumer import callback
from collector import (
    create_job,
    delete_existing_data,
    get_fantasy_stats,
    insert_player_data,
    mark_job_complete,
    save_data_to_database,
    update_statistics,
    update_timestamp,
)

load_dotenv()

API_KEY = os.getenv("API_KEY")

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
    jobId = str(uuid.uuid4())
    messageObj = {
        "job_id": jobId,
        "position": "qb",
        "week": "1",
        "season": "2026-2027-regular",
        "test": False,
    }
    body = json.dumps(messageObj).encode()
    db_connection = MagicMock()
    method.delivery_tag = testTag

    with patch("consumer.update_statistics") as mock_update:
        callback(ch, method, None, body, db_connection)

        mock_update.assert_called_once_with(messageObj, db_connection)
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


def test_delete_existing_data():
    position = "qb"
    week = "1"
    season = "2026-2027-regular"
    query = """
        DELETE FROM players
        WHERE (
            position = %s AND
            week = %s AND
            season = %s
        )
    """
    connection = MagicMock()

    delete_existing_data(position, week, season, connection)

    connection.cursor().execute.assert_called_once_with(query, (position, week, season))
    connection.commit.assert_called_once()


def test_insert_player_data():
    position = "qb"
    week = "1"
    season = "2026-2027-regular"
    insert_sql = """
        INSERT INTO players (
            id,
            position,
            week,
            season,
            first_name,
            last_name,
            team,
            projected_points
        ) VALUES %s
    """
    row_to_insert = [
        (
            13349,
            position,
            week,
            season,
            "Patrick",
            "Mahomes",
            "KC",
            13.039999961853027,
        )
    ]
    connection = MagicMock()

    with patch("collector.execute_values") as mock_execute_values:
        insert_player_data(position, week, season, test_fantasy_stats, connection)

        mock_execute_values.assert_called_once_with(
            connection.cursor(), insert_sql, row_to_insert
        )

        connection.commit.assert_called_once()


def test_update_timestamp():
    position = "qb"
    week = "1"
    season = "2026-2027-regular"
    delete_sql = """
        DELETE FROM last_updated
        WHERE (
            position = %s AND
            week = %s AND
            season = %s
        )
    """
    insert_sql = """
        INSERT INTO last_updated (
            position,
            week,
            season,
            updated_at
        ) VALUES (
            %s,
            %s,
            %s,
            %s
        )
    """
    connection = MagicMock()

    with patch("collector.datetime") as mock_datetime:
        update_timestamp(position, week, season, connection)

        assert connection.cursor().execute.call_count == 2
        assert connection.cursor().execute.call_args_list == [
            call(delete_sql, (position, week, season)),
            call(
                insert_sql,
                (position, week, season, mock_datetime.now.return_value),
            ),
        ]

        assert connection.commit.call_count == 2


def test_save_data_to_database() -> None:
    with patch("collector.delete_existing_data") as mock_delete_existing_data, patch(
        "collector.insert_player_data"
    ) as mock_insert_player_data, patch(
        "collector.update_timestamp"
    ) as mock_update_timestamp:
        position = "qb"
        week = "1"
        season = "2026-2027-regular"
        connection = MagicMock()

        save_data_to_database(position, week, season, test_fantasy_stats, connection)

        mock_delete_existing_data.assert_called_once_with(
            position, week, season, connection
        )
        mock_insert_player_data.assert_called_once_with(
            position, week, season, test_fantasy_stats, connection
        )
        mock_update_timestamp.assert_called_once_with(
            position, week, season, connection
        )


def test_get_fantasy_stats():
    position = "qb"
    week = "1"
    season = "2026-2027-regular"
    with patch("collector.requests.get") as mock_get_request:
        mock_json_return_value = MagicMock()
        mock_json_return_value.json.return_value = test_fantasy_stats
        mock_get_request.return_value = mock_json_return_value

        result = get_fantasy_stats(position, week, season)

        credentials = base64.b64encode(f"{API_KEY}:MYSPORTSFEEDS".encode()).decode(
            "utf-8"
        )
        mock_get_request.assert_called_once_with(
            f"https://api.mysportsfeeds.com/v2.1/pull/nfl/{season}/week/{week}/dfs_projections.json",
            params={"position": "qb"},
            headers={"Authorization": "Basic " + credentials},
        )
        assert result == test_fantasy_stats


def test_update_statistics_health_check() -> None:
    with patch("collector.create_job") as mock_create_job, patch(
        "collector.get_fantasy_stats"
    ) as mock_get_fantasy_stats, patch(
        "collector.save_data_to_database"
    ) as mock_save_data_to_database, patch(
        "collector.mark_job_complete"
    ) as mock_mark_job_complete:
        jobId = str(uuid.uuid4())
        message = {
            "job_id": jobId,
            "position": "qb",
            "week": "1",
            "season": "2026-2027-regular",
            "test": False,
        }
        connection = MagicMock()

        update_statistics(message, connection)

        mock_create_job.assert_called_once_with(jobId, connection)
        mock_get_fantasy_stats.assert_called_once_with(
            message["position"], message["week"], message["season"]
        )
        mock_save_data_to_database.assert_called_once_with(
            message["position"],
            message["week"],
            message["season"],
            mock_get_fantasy_stats.return_value,
            connection,
        )
        mock_mark_job_complete.assert_called_once_with(jobId, connection)


def test_update_statistics_health_check() -> None:
    with patch("collector.create_job") as mock_create_job, patch(
        "collector.get_fantasy_stats"
    ) as mock_get_fantasy_stats, patch(
        "collector.save_data_to_database"
    ) as mock_save_data_to_database, patch(
        "collector.mark_job_complete"
    ) as mock_mark_job_complete:
        jobId = str(uuid.uuid4())
        message = {
            "job_id": jobId,
            "position": "",
            "week": "",
            "season": "",
            "test": True,
        }
        connection = MagicMock()

        update_statistics(message, connection)

        mock_create_job.assert_called_once_with(jobId, connection)
        mock_get_fantasy_stats.assert_not_called()
        mock_save_data_to_database.assert_not_called()
        mock_mark_job_complete.assert_called_once_with(jobId, connection)
