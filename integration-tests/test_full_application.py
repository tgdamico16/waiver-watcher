from datetime import datetime
import time
from typing import Dict, Union

import requests

BACKEND_HOST = "waiver_watcher_backend:8000"


def hit_backend(endpoint: str, params: Union[Dict, None] = None) -> Dict:
    backend_api_url = f"http://{BACKEND_HOST}/{endpoint}"
    response = requests.get(backend_api_url, params=params)
    print(f"hit backend, response: {response.json()}")
    return response.json()


def wait_for_backend_to_start():
    health_check_response = None
    while health_check_response != {"status": "healthy"}:
        try:
            time.sleep(1)
            health_check_response = hit_backend("health")
        except Exception:
            print("unable to connect, retrying")
            pass


def test_full_application():
    print("waiting for backend to start...")
    wait_for_backend_to_start()
    print("backend started")

    print("starting job")
    params = {"position": "qb", "week": "1", "season": "2026-2027-regular"}
    job_start_response = hit_backend("start-job", params)
    print("job started")

    job_id = job_start_response["job_id"]

    job_status_response = hit_backend(f"job-status/{job_id}")
    query_count = 1
    print(f"queried job status {query_count} time")
    job_status = job_status_response["job_status"]
    while job_status != "complete":
        time.sleep(1)
        job_status_response = hit_backend(f"job-status/{job_id}")
        job_status = job_status_response["job_status"]
        query_count += 1
        print(f"queried job status {query_count} times")

    print("job complete, getting top 25 players & timestamp")
    top_25_players_response = hit_backend("top-25-players", params)
    top_25_players = top_25_players_response["players"]
    print("got top 25 players")
    timestamp_response = hit_backend("timestamp", params)
    timestamp = timestamp_response["timestamp"]
    datetime.fromisoformat(timestamp)

    assert len(top_25_players) == 25 and "projected_points" in top_25_players[0]
