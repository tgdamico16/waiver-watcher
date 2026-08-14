from unittest.mock import MagicMock, patch
import uuid

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_update_statistics():
    mock_channel = MagicMock()
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel
    with patch(
        "main.get_rabbitmq_connection_with_retries"
    ) as mock_get_rabbit_connection:
        mock_get_rabbit_connection.return_value = mock_connection

        response = client.get("/update-statistics")

        _, kwargs = mock_channel.basic_publish.call_args
        job_id = kwargs["body"]

        assert response.status_code == 200
        assert response.json() == {"status": "success", "job_id": job_id}


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
