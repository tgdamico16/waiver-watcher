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
    app.state.rabbitmq_channel = mock_channel

    response = client.get("/update-statistics")

    _, kwargs = mock_channel.basic_publish.call_args
    job_id = kwargs["body"]

    assert response.status_code == 200
    assert response.json() == {"status": "success", "job_id": job_id}


def test_get_job_status():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("", "complete")
    app.state.postgres_cursor = mock_cursor

    test_job_id = str(uuid.uuid4())
    response = client.get(f"/job-status/{test_job_id}")

    assert response.status_code == 200
    assert response.json() == {"status": "success", "job_status": "complete"}
