import base64
import json
import time
from typing import Dict

import psycopg2
import requests

from psycopg2.extras import execute_values

API_URL = "https://api.open-meteo.com/v1/forecast?latitude=40.015&longitude=-105.2706&hourly=temperature_2m"


def get_db_connection_with_retries():
    while True:
        try:
            print("attempting to connect to db (might take a few seconds)")
            connection = psycopg2.connect(
                host="localhost",
                port=5432,
                database="weather",
                user="username",
                password="password",
            )
            print("connected to db")
            return connection
        except:
            time.sleep(2)


def save_data_to_database(weather_data: Dict) -> None:
    connection = get_db_connection_with_retries()
    query = """
        INSERT INTO temperature (
            recorded_at,
            temperature
        ) VALUES %s
    """
    rows_to_insert = [
        (weather_data["hourly"]["time"][i], weather_data["hourly"]["temperature_2m"][i])
        for i in range(len(weather_data["hourly"]["time"]))
    ]
    print("saving data to database")
    execute_values(connection.cursor(), query, rows_to_insert)
    connection.commit()
    print("data saved to database")


def get_weather_data() -> Dict:
    print("Calling api...")
    response = requests.get(
        API_URL,
    )
    print("API returned")
    return response.json()


def main() -> None:
    weather_data = get_weather_data()
    save_data_to_database(weather_data)


main()
