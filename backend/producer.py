import os
import time

from dotenv import load_dotenv
import pika
import uuid

load_dotenv()

RABBIT_USER = os.getenv("RABBIT_USER")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")


def get_rabbitmq_channel_with_retries():
    while True:
        try:
            print("attempting to connect to rabbit")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host="waiver_watcher_rabbitmq",
                    credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD),
                )
            )
            return connection.channel()
        except Exception:
            time.sleep(2)


channel = get_rabbitmq_channel_with_retries()
channel.queue_declare(queue="update_statistics", durable=True)


def send_message_to_data_collector():
    job_id = str(uuid.uuid4())
    channel.basic_publish(
        exchange="",
        routing_key="update_statistics",
        body=job_id,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    print(job_id)
    return job_id


if __name__ == "__main__":
    send_message_to_data_collector()
