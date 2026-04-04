import time 
import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SEEN_FILE = "seen_jobs.txt"


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    print("Telegram response:", response.text)


def load_seen_jobs():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file if line.strip())


def save_seen_job(job):
    with open(SEEN_FILE, "a", encoding="utf-8") as file:
        file.write(job + "\n")


def get_remoteok_jobs():
    url = "https://remoteok.com/remote-python-jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language" :"en-us,en;q=0.9"
    }

    response = requests.get(url, headers=headers , timeout =10)
    print("Website status:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []

    rows = soup.find_all("tr", class_="job")
    print("Total job rows found:", len(rows))

    for row in rows[:10]:
        title_tag = row.find("h2")
        company_tag = row.find("h3")
        link_tag = row.find("a", class_="preventLink")

        if title_tag and company_tag:
            title = title_tag.get_text(strip=True)
            company = company_tag.get_text(strip=True)

            job_link = ""
            if link_tag and link_tag.get("href"):
                job_link = "https://remoteok.com" + link_tag.get("href")
            jobs.append(f"{title} at {company}\n{job_link}")
            job_text = f"{title} at {company}"
            full_job = f"{job_text}\n{job_link}".strip()

            jobs.append(full_job)

    return jobs

while True:
    print("\n--- Running job check ---")
    seen_jobs = load_seen_jobs()
    jobs = get_remoteok_jobs()

    new_jobs = []

    for job in jobs:
        if job not in seen_jobs:
            new_jobs.append(job)
            save_seen_job(job)

    if new_jobs:
        message =  "\n\n".join(new_jobs[:5])
    else:
        message = "No new jobs found right now."

    print("Final message:")
    print(message)

    send_telegram_message(message)
    print("Sleeping for 10 minutes...\n")
    time.sleep(600)  # 600 seconds = 10 minutes
