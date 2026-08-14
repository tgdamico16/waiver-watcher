from contextlib import asynccontextmanager
import os
import random

from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from util import (
    get_db_connection_with_retries,
    get_rabbitmq_channel_with_retries,
    send_message_to_data_collector,
)

load_dotenv()

SERVER_HOST = os.getenv("SERVER_HOST")


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = get_db_connection_with_retries()
    app.state.postgres_connection = connection

    channel = get_rabbitmq_channel_with_retries()
    channel.queue_declare(queue="update_statistics", durable=True)
    app.state.rabbitmq_channel = channel
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    f"http://{SERVER_HOST}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/update-statistics")
async def update_statistics(request: Request):
    try:
        channel = request.app.state.rabbitmq_channel
        job_id = send_message_to_data_collector(channel)
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str, request: Request):
    try:
        connection = request.app.state.postgres_connection
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
        row = cursor.fetchone()
        status = row[1] if row is not None else "nonexistent"
        return {"status": "success", "job_status": status}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/random-player")
async def get_random_player(request: Request):
    try:
        connection = request.app.state.postgres_connection
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM player_projections")
        rows = cursor.fetchall()
        randomPlayerIndex = random.randint(0, len(rows) - 1)
        playerRow = rows[randomPlayerIndex]
        player = " ".join([str(info) for info in playerRow])
        return {"status": "success", "player": player}
    except Exception as e:
        print(rows)
        print(e)
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
