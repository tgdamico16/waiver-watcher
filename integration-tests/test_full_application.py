import time
from typing import Dict

import requests

BACKEND_HOST = "waiver_watcher_backend:8000"


def hit_backend(endpoint: str) -> Dict:
    backend_api_url = f"http://{BACKEND_HOST}/{endpoint}"
    response = requests.get(backend_api_url)
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
    job_start_response = hit_backend("update-statistics")
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

    print("job complete, getting random player")
    random_player_response = hit_backend("random-player")
    random_player = random_player_response["player"]
    print("got random player")

    assert "QB" in random_player
