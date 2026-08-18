from datetime import datetime
import os
import time
from dotenv import load_dotenv
import requests
import smtplib
from email.mime.text import MIMEText

load_dotenv()

FRONTEND_HEALTH_URL = "http://waiver_watcher_frontend:3000/api/health"
ALERT_EMAIL = os.getenv("EMAIL")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("EMAIL")
SMTP_PASS = os.getenv("GOOGLE_APP_PASSWORD")


def send_alert():
    msg = MIMEText("Waiver Watcher Health Check Failed")
    msg["Subject"] = "Waiver Watcher Health Check Failed"
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_EMAIL

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())


def check_health():
    response = requests.get(FRONTEND_HEALTH_URL)
    if response.status_code != 200:
        raise Exception("Health check failed")
    else:
        print(f"{datetime.now()} Healthy")


def main():
    consecutive_failures = 0
    while True:
        time.sleep(60)
        try:
            check_health()
            consecutive_failures = 0
        except Exception as e:
            consecutive_failures += 1
            if consecutive_failures >= 5:
                send_alert()
                raise e


if __name__ == "__main__":
    main()
