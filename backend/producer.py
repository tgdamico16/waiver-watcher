import os

from dotenv import load_dotenv
import pika
import uuid

load_dotenv()

RABBIT_USER = os.getenv("RABBIT_USER")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")


def get_rabbitmq_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
            credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD),
        )
    )
    return connection.channel()


channel = get_rabbitmq_channel()
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
