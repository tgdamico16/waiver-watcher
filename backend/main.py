from fastapi import FastAPI
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
async def health_check():
    return {"status": "healthy"}


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


@app.get("/top-10-players")
# async def get_top_10_players(request: Request):
async def get_top_10_players():
    try:
        # connection = request.app.state.postgres_connection
        connection = get_db_connection_with_retries()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM player_projections")
        players = cursor.fetchall()

        sorted_players = sorted(players, key=lambda x: x[5], reverse=True)
        top_10_players = sorted_players[:10]
        top_10_players_obj = [
            {
                "id": player[0],
                "first_name": player[1],
                "last_name": player[2],
                "position": player[3],
                "team": player[4],
                "projected_points": player[5],
            }
            for player in top_10_players
        ]
        return {"status": "success", "players": top_10_players_obj}
    except Exception as e:
        print(players)
        print(e)
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
