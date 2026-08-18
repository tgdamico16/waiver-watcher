from datetime import datetime, timezone
import json
from unittest.mock import MagicMock, patch
import uuid

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_check():
    mock_rabbit_channel = MagicMock()
    mock_rabbit_connection = MagicMock()
    mock_rabbit_connection.channel.return_value = mock_rabbit_channel
    mock_postgres_cursor = MagicMock()
    mock_postgres_connection = MagicMock()
    mock_postgres_connection.cursor.return_value = mock_postgres_cursor
    mock_postgres_cursor.fetchone.return_value = "success"

    position = ""
    week = ""
    season = ""
    with patch(
        "main.get_rabbitmq_connection_with_retries"
    ) as mock_get_rabbit_connection, patch(
        "main.get_db_connection_with_retries"
    ) as mock_get_db_connection:
        mock_get_rabbit_connection.return_value = mock_rabbit_connection
        mock_get_db_connection.return_value = mock_postgres_connection

        response = client.get("/health")

        _, kwargs = mock_rabbit_channel.basic_publish.call_args
        message = json.loads(kwargs["body"])

        assert message["position"] == position
        assert message["week"] == week
        assert message["season"] == season
        assert message["test"] == True

        query = "SELECT * FROM jobs WHERE job_id = %s"
        mock_postgres_cursor.execute.assert_called_once_with(
            query, (message["job_id"],)
        )

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


def test_start_job():
    mock_channel = MagicMock()
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel
    position = "qb"
    week = "1"
    season = "2026-2027-regular"
    with patch(
        "main.get_rabbitmq_connection_with_retries"
    ) as mock_get_rabbit_connection:
        mock_get_rabbit_connection.return_value = mock_connection

        response = client.get(
            f"/start-job?position={position}&week={week}&season={season}"
        )

        _, kwargs = mock_channel.basic_publish.call_args
        message = json.loads(kwargs["body"])

        assert response.status_code == 200
        assert message["position"] == position
        assert message["week"] == week
        assert message["season"] == season
        assert response.json() == {"status": "success", "job_id": message["job_id"]}


def test_get_job_status():
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ("", "complete")
    app.state.postgres_connection = mock_connection

    test_job_id = str(uuid.uuid4())

    with patch("main.get_db_connection_with_retries") as mock_get_db_connection:
        mock_get_db_connection.return_value = mock_connection

        response = client.get(f"/job-status/{test_job_id}")

        assert response.status_code == 200
        assert response.json() == {"status": "success", "job_status": "complete"}


def test_get_top_25_players():
    test_top_25_players_tuple = [
        (
            1,
            "qb",
            "1",
            "2026-2027-regular",
            "Patrick",
            "Mahomes",
            "KC",
            100,
        )
    ]
    test_top_25_players_obj = [
        {
            "first_name": "Patrick",
            "last_name": "Mahomes",
            "team": "KC",
            "projected_points": 100,
        },
    ]
    position = "qb"
    week = "1"
    season = "2026-2027-regular"

    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = test_top_25_players_tuple

    with patch("main.get_db_connection_with_retries") as mock_get_db_connection:
        mock_get_db_connection.return_value = mock_connection

        response = client.get(
            f"/top-25-players?position={position}&week={week}&season={season}"
        )

        assert response.status_code == 200
        assert response.json() == {
            "status": "success",
            "players": test_top_25_players_obj,
        }


def test_get_timestamp():
    test_timestamp = datetime.now(timezone.utc)
    position = "qb"
    week = "1"
    season = "2026-2027-regular"
    query = """
            SELECT updated_at FROM last_updated
            WHERE (
                position = %s AND
                week = %s AND
                season = %s
            )
        """
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (test_timestamp,)
    app.state.postgres_connection = mock_connection

    with patch("main.get_db_connection_with_retries") as mock_get_db_connection:
        mock_get_db_connection.return_value = mock_connection
        response = client.get(
            f"/timestamp?position={position}&week={week}&season={season}"
        )

        mock_cursor.execute.assert_called_once_with(query, (position, week, season))
        assert response.status_code == 200
        assert response.json() == {
            "status": "success",
            "timestamp": test_timestamp.isoformat(),
        }
