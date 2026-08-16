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


def test_get_top_10_players():
    test_top_10_players_tuple = [
        (
            1,
            "Patrick",
            "Mahomes",
            "QB",
            "KC",
            100,
        )
    ]
    test_top_10_players_obj = [
        {
            "id": 1,
            "first_name": "Patrick",
            "last_name": "Mahomes",
            "position": "QB",
            "team": "KC",
            "projected_points": 100,
        },
    ]

    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = test_top_10_players_tuple

    with patch("main.get_db_connection_with_retries") as mock_get_db_connection:
        mock_get_db_connection.return_value = mock_connection

        response = client.get("/top-10-players")

        assert response.status_code == 200
        assert response.json() == {
            "status": "success",
            "players": test_top_10_players_obj,
        }
