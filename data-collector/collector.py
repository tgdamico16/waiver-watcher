import base64
from datetime import datetime, timezone
import json
import os
from typing import Dict

from dotenv import load_dotenv
import requests

from psycopg2.extras import execute_values

load_dotenv()

API_KEY = os.getenv("API_KEY")


def get_api_url(week: str, season: str):
    return f"https://api.mysportsfeeds.com/v2.1/pull/nfl/{season}/week/{week}/dfs_projections.json"


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


def delete_existing_data(position: str, week: str, season: str, connection) -> None:
    print("deleting existing data...")
    query = """
        DELETE FROM players
        WHERE (
            position = %s AND
            week = %s AND
            season = %s
        )
    """
    connection.cursor().execute(query, (position, week, season))
    connection.commit()
    print("existing data deleted")


def insert_player_data(
    position: str, week: str, season: str, fantasy_stats: Dict, connection
):
    query = """
        INSERT INTO players (
            id,
            position,
            week,
            season,
            first_name,
            last_name,
            team,
            projected_points
        ) VALUES %s
    """
    rows_to_insert = [
        (
            projection["player"]["id"],
            position,
            week,
            season,
            projection["player"]["firstName"],
            projection["player"]["lastName"],
            projection["team"]["abbreviation"],
            projection["fantasyPoints"][0]["points"],
        )
        for projection in fantasy_stats["projections"]
    ]
    print("saving data to database")
    execute_values(connection.cursor(), query, rows_to_insert)
    connection.commit()
    print("data saved to database")


def update_timestamp(position: str, week: str, season: str, connection):
    print("Updating timestamp...")
    query = """
        DELETE FROM last_updated
        WHERE (
            position = %s AND
            week = %s AND
            season = %s
        )
    """
    connection.cursor().execute(query, (position, week, season))
    connection.commit()
    query = """
        INSERT INTO last_updated (
            position,
            week,
            season,
            updated_at
        ) VALUES (
            %s,
            %s,
            %s,
            %s
        )
    """
    connection.cursor().execute(
        query, (position, week, season, datetime.now(timezone.utc))
    )
    connection.commit()
    print("existing data deleted")


def save_data_to_database(
    position: str, week: str, season: str, fantasy_stats: Dict, connection
) -> None:
    delete_existing_data(position, week, season, connection)
    insert_player_data(position, week, season, fantasy_stats, connection)
    update_timestamp(position, week, season, connection)


def get_fantasy_stats(position: str, week: str, season: str) -> Dict:
    credentials = base64.b64encode(f"{API_KEY}:MYSPORTSFEEDS".encode()).decode("utf-8")
    print("Calling api...")
    response = requests.get(
        get_api_url(week, season),
        params={"position": position},
        headers={"Authorization": "Basic " + credentials},
    )
    print("API returned")
    return response.json()


def update_statistics(message: Dict, connection) -> None:
    create_job(message["job_id"], connection)
    if message["test"]:
        print("test message received, not calling api")
    else:
        fantasy_stats = get_fantasy_stats(
            message["position"], message["week"], message["season"]
        )
        save_data_to_database(
            message["position"],
            message["week"],
            message["season"],
            fantasy_stats,
            connection,
        )
    mark_job_complete(message["job_id"], connection)


def test_api():
    response = get_fantasy_stats("qb", "1", "2025-2026-regular")
    with open("output.json", "w") as f:
        json.dump(response, f, indent=2)


if __name__ == "__main__":
    test_api()
