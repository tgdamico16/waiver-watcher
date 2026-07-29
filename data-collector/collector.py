import requests

url = "https://api.sleeper.app/v1/players/nfl"
response = requests.get(url, timeout=5)
response.raise_for_status()
data = response.json()
print(data)