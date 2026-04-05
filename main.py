import os
import time
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SEEN_FILE = "seen_jobs.txt"


def send_telegram_message(message: str) -> None:
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing BOT_TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=data, timeout=15)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Telegram send error:", e)


def load_seen_jobs() -> set[str]:
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file if line.strip())


def save_seen_job(job: str) -> None:
    with open(SEEN_FILE, "a", encoding="utf-8") as file:
        file.write(job + "\n")


def is_good_job(text: str) -> bool:
    text = text.lower()

    keywords = [
        "python",
        "ai",
        "ml",
        "machine learning",
        "data",
        "backend",
        "developer",
        "engineer"
    ]

    bad_words = [
        "senior",
        "staff",
        "principal",
        "lead",
        "manager",
        "director"
    ]

    return any(word in text for word in keywords) and not any(bad in text for bad in bad_words)


def get_remoteok_jobs() -> list[str]:
    url = "https://remoteok.com/remote-python-jobs"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    jobs: list[str] = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        print("RemoteOK status:", response.status_code)

        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr", class_="job")
        print("RemoteOK rows found:", len(rows))

        for row in rows[:15]:
            title_tag = row.find("h2")
            company_tag = row.find("h3")
            link_tag = row.find("a", class_="preventLink")

            if not title_tag or not company_tag:
                continue

            title = title_tag.get_text(strip=True)
            company = company_tag.get_text(strip=True)

            job_link = ""
            if link_tag and link_tag.get("href"):
                job_link = "https://remoteok.com" + link_tag.get("href")

            text = f"{title} {company} {row.get_text(' ', strip=True)}"

            if is_good_job(text):
                full_job = f"{title} at {company}\n{job_link}".strip()
                jobs.append(full_job)

    except Exception as e:
        print("RemoteOK error:", e)

    print("RemoteOK jobs:", len(jobs))
    return jobs


def get_weworkremotely_jobs() -> list[str]:
    url = "https://weworkremotely.com/remote-jobs/search?term=python"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    jobs: list[str] = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        print("WWR status:", response.status_code)

        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        print("WWR links found:", len(links))

        for link in links:
            text = link.get_text(" ", strip=True)
            href = link.get("href", "")

            if not text or not href:
                continue

            if href.startswith("/"):
                job_link = "https://weworkremotely.com" + href
            else:
                continue

            if is_good_job(text):
                full_job = f"{text}\n{job_link}"
                jobs.append(full_job)

    except Exception as e:
        print("WWR error:", e)

    print("WWR jobs:", len(jobs))
    return jobs


def main_loop() -> None:
    while True:
        print("\n--- Running job check ---")

        seen_jobs = load_seen_jobs()

        remoteok_jobs = get_remoteok_jobs()
        wwr_jobs = get_weworkremotely_jobs()

        jobs = remoteok_jobs + wwr_jobs
        print("Combined jobs:", len(jobs))

        jobs = list(dict.fromkeys(jobs))
        print("Unique combined jobs:", len(jobs))

        new_jobs: list[str] = []

        for job in jobs:
            if job not in seen_jobs:
                new_jobs.append(job)
                save_seen_job(job)

        if new_jobs:
            message = "🔥 New Job Alerts\n\n" + "\n\n".join(new_jobs[:5])
            print("Final message:")
            print(message)
            send_telegram_message(message)
        else:
            print("No new jobs found right now.")

        print("Sleeping for 10 minutes...\n")
        time.sleep(600)


if __name__ == "__main__":
    main_loop()
