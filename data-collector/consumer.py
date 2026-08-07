import os
import time

from dotenv import load_dotenv
import pika
from collector import update_statistics

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


def callback(ch, method, properties, body):
    job_id = body.decode()
    update_statistics(job_id)
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
