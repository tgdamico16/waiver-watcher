import base64
import json
import os
import time
from typing import Dict

import uuid
from dotenv import load_dotenv
import requests

import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

API_KEY = os.getenv("API_KEY")
FANTASY_STATS_API_URL = "https://api.mysportsfeeds.com/v2.1/pull/nfl/2026-2027-regular/week/1/dfs_projections.json"


def create_job(job_id: str, connection) -> None:
    print("creating job")
    connection.cursor().execute(
        "INSERT INTO jobs (job_id, status) VALUES (%s, %s)", (job_id, "executing")
    )
    connection.commit()
    print("job created")


def mark_job_complete(job_id: str, connection) -> None:
    print("marking job complete")
    connection.cursor().execute(
        "UPDATE jobs SET status = %s WHERE job_id = %s", ("complete", job_id)
    )
    connection.commit()
    print("marked job complete")


def save_data_to_database(fantasy_stats: Dict, connection) -> None:
    print("deleting existing data...")
    connection.cursor().execute("DELETE FROM player_projections WHERE 1=1")
    connection.commit()
    print("existing data deleted")

    query = """
        INSERT INTO player_projections (
            id,
            first_name,
            last_name,
            position,
            team,
            projected_points
        ) VALUES %s
    """
    rows_to_insert = [
        (
            projection["player"]["id"],
            projection["player"]["firstName"],
            projection["player"]["lastName"],
            projection["player"]["position"],
            projection["team"]["abbreviation"],
            projection["fantasyPoints"][0]["points"],
        )
        for projection in fantasy_stats["projections"]
    ]
    print("saving data to database")
    execute_values(connection.cursor(), query, rows_to_insert)
    connection.commit()
    print("data saved to database")


def get_fantasy_stats() -> Dict:
    credentials = base64.b64encode(f"{API_KEY}:MYSPORTSFEEDS".encode()).decode("utf-8")
    print("Calling api...")
    response = requests.get(
        FANTASY_STATS_API_URL,
        params={"position": "qb"},
        headers={"Authorization": "Basic " + credentials},
    )
    print("API returned")
    return response.json()


def update_statistics(job_id: str, connection) -> None:
    create_job(job_id, connection)
    fantasy_stats = get_fantasy_stats()
    save_data_to_database(fantasy_stats, connection)
    mark_job_complete(job_id, connection)
