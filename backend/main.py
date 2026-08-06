import os
import random

from dotenv import load_dotenv
import psycopg2

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from producer import send_message_to_data_collector

app = FastAPI()

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connection = psycopg2.connect(
    host="localhost",
    port=5432,
    database="waiver_watcher",
    user=DB_USER,
    password=DB_PASSWORD,
)
cursor = connection.cursor()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/update-statistics")
async def update_statistics():
    try:
        job_id = send_message_to_data_collector()
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        return {"status": "error", "error": e}


@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    try:
        cursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
        row = cursor.fetchone()
        return {"status": "success", "job_status": row[1]}
    except Exception as e:
        return {"status": "error", "error": e}


@app.get("/random-player")
async def get_random_player():
    try:
        cursor.execute("SELECT * FROM player_projections")
        rows = cursor.fetchall()
        randomPlayerIndex = random.randint(0, len(rows) - 1)
        playerRow = rows[randomPlayerIndex]
        player = " ".join([str(info) for info in playerRow])
        return {"status": "success", "player": player}
    except Exception as e:
        print(rows)
        print(e)
        return {"status": "error", "error": e}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
