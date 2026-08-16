import json
import os
import time
import uuid

from dotenv import load_dotenv
import pika
import psycopg2

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
RABBIT_USER = os.getenv("RABBIT_USER")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")


def get_db_connection_with_retries():
    while True:
        try:
            print("attempting to connect to db")
            connection = psycopg2.connect(
                # host="localhost",
                host="waiver_watcher_postgres",
                port=5432,
                database="waiver_watcher",
                user=DB_USER,
                password=DB_PASSWORD,
            )
            print("connected to db")
            return connection
        except:
            time.sleep(2)


def get_rabbitmq_connection_with_retries():
    while True:
        try:
            print("attempting to connect to rabbit")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    # host="localhost",
                    host="waiver_watcher_rabbitmq",
                    credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD),
                )
            )
            print("connected to rabbit")
            return connection
        except Exception:
            time.sleep(2)


def send_message_to_data_collector(connection, position: str, week: str, season: str):
    job_id = str(uuid.uuid4())
    message = json.dumps(
        {"job_id": job_id, "position": position, "week": week, "season": season}
    )

    channel = connection.channel()
    channel.queue_declare(queue="update_statistics", durable=True)
    channel.basic_publish(
        exchange="",
        routing_key="update_statistics",
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )

    print(job_id)
    return job_id
