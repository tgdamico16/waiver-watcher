from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from util import (
    get_db_connection_with_retries,
    get_rabbitmq_connection_with_retries,
    send_message_to_data_collector,
)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     connection = get_db_connection_with_retries()
#     app.state.postgres_connection = connection

#     connection = get_rabbitmq_connection_with_retries()
#     app.state.rabbitmq_connection = connection
#     yield


# app = FastAPI(lifespan=lifespan)
app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
# async def health_check(request: Request):
async def health_check():
    try:
        # rabbit_connection = request.app.state.rabbitmq_connection
        # postgres_connection = request.app.state.postgres_connection
        rabbit_connection = get_rabbitmq_connection_with_retries()
        postgres_connection = get_db_connection_with_retries()
        cursor = postgres_connection.cursor()

        job_id = send_message_to_data_collector(rabbit_connection, "", "", "", True)
        for _ in range(5):
            time.sleep(1)
            cursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
            row = cursor.fetchone()
            if row is not None:
                return {"status": "healthy"}
        return {"status": "unhealthy"}
    except Exception:
        return {"status": "unhealthy"}


@app.get("/start-job")
# async def start_job(request: Request, position: str, week: str, season: str):
async def start_job(position: str, week: str, season: str):
    try:
        # connection = request.app.state.rabbitmq_connection
        connection = get_rabbitmq_connection_with_retries()
        job_id = send_message_to_data_collector(connection, position, week, season)
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/job-status/{job_id}")
# async def get_job_status(job_id: str, request: Request):
async def get_job_status(job_id: str):
    try:
        # connection = request.app.state.postgres_connection
        connection = get_db_connection_with_retries()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
        row = cursor.fetchone()
        status = row[1] if row is not None else "nonexistent"
        return {"status": "success", "job_status": status}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/top-25-players")
# async def get_top_25_players(request: Request, position: str, week: str, season: str):
async def get_top_25_players(position: str, week: str, season: str):
    try:
        # connection = request.app.state.postgres_connection
        connection = get_db_connection_with_retries()
        cursor = connection.cursor()
        query = """
            SELECT * FROM players
            WHERE (
                position = %s AND
                week = %s AND
                season = %s
            )
        """
        cursor.execute(
            query,
            (position, week, season),
        )
        players = cursor.fetchall()

        sorted_players = sorted(players, key=lambda x: x[7], reverse=True)
        top_25_players = sorted_players[:25]
        top_25_players_obj = [
            {
                "first_name": player[4],
                "last_name": player[5],
                "team": player[6],
                "projected_points": player[7],
            }
            for player in top_25_players
        ]
        return {"status": "success", "players": top_25_players_obj}
    except Exception as e:
        print(players)
        print(e)
        return {"status": "error", "error": str(e)}


@app.get("/timestamp")
# async def get_timestamp(request: Request, position: str, week: str, season: str):
async def get_timestamp(position: str, week: str, season: str):
    try:
        # connection = request.app.state.postgres_connection
        connection = get_db_connection_with_retries()
        cursor = connection.cursor()
        query = """
            SELECT updated_at FROM last_updated
            WHERE (
                position = %s AND
                week = %s AND
                season = %s
            )
        """
        cursor.execute(
            query,
            (position, week, season),
        )
        row = cursor.fetchone()
        timestamp = row[0].isoformat() if row is not None else None
        print(timestamp)
        return {"status": "success", "timestamp": timestamp}
    except Exception as e:
        print(row)
        print(e)
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
