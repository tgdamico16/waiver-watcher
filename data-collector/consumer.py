import os

from dotenv import load_dotenv
import pika
from collector import update_statistics

load_dotenv()

RABBIT_USER = os.getenv("RABBIT_USER")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")


def callback(ch, method, properties, body):
    job_id = body.decode()
    update_statistics(job_id)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
            credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="update_statistics", durable=True)
    channel.basic_consume(
        queue="update_statistics", on_message_callback=callback, auto_ack=True
    )
    print("Listening...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
