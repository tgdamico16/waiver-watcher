from functools import partial
import os
import time

from dotenv import load_dotenv
from collector import update_statistics
from util import get_db_connection_with_retries, get_rabbitmq_connection_with_retries

load_dotenv()

RABBIT_USER = os.getenv("RABBIT_USER")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")


def callback(ch, method, properties, body, db_connection):
    try:
        job_id = body.decode()
        update_statistics(job_id, db_connection)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error during callback: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def consume_loop():
    while True:
        try:
            rabbit_connection = get_rabbitmq_connection_with_retries()
            db_connection = get_db_connection_with_retries()
            channel = rabbit_connection.channel()
            channel.queue_declare(queue="update_statistics", durable=True)

            wrapped_callback = partial(callback, db_connection=db_connection)

            channel.basic_consume(
                queue="update_statistics",
                on_message_callback=wrapped_callback,
                auto_ack=False,
            )
            print("Listening...")
            channel.start_consuming()
        except Exception as e:
            print(f"Consumer error: {str(e)}")
            time.sleep(1)


if __name__ == "__main__":
    consume_loop()
