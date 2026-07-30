import base64
import os

from dotenv import load_dotenv
import requests

load_dotenv()


def send_request(url: str, apiKey: str):
    credentials = base64.b64encode(f"{apiKey}:MYSPORTSFEEDS".encode()).decode("utf-8")
    response = requests.get(
        url,
        params={"fordate": "20161121"},
        headers={"Authorization": "Basic " + credentials},
    )
    print(
        "Response HTTP Status Code: {status_code}".format(
            status_code=response.status_code
        )
    )
    print("Response HTTP Response Body: {content}".format(content=response.content))


apiKey = os.getenv("API_KEY")

url = "https://api.mysportsfeeds.com/v2.1/pull/nfl/2026-2027-regular/week/1/dfs_projections.json"
send_request(url, apiKey)
