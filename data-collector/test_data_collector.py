from unittest.mock import MagicMock, patch
import uuid
from consumer import callback


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
