import os

from dotenv import load_dotenv
from collector import update_statistics
from util import get_db_connection_with_retries, get_rabbitmq_channel_with_retries

load_dotenv()

RABBIT_USER = os.getenv("RABBIT_USER")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")


def callback(ch, method, properties, body):
    connection = get_db_connection_with_retries()
    job_id = body.decode()
    update_statistics(job_id, connection)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    channel = get_rabbitmq_channel_with_retries()
    channel.queue_declare(queue="update_statistics", durable=True)
    channel.basic_consume(
        queue="update_statistics", on_message_callback=callback, auto_ack=False
    )
    print("Listening...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
