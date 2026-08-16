import os
import time

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
