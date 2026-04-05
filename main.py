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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://google.com"
}

    jobs = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print("RemoteOK status:", response.status_code)

        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr", class_="job")
        print("RemoteOK rows found:", len(rows))

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

                job_text = f"{title} at {company}"
                full_job = f"{job_text}\n{job_link}".strip()

                text = f"{title} {company} {row.get_text(' ', strip=True)}".lower()

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

                if any(word in text for word in keywords) and not any(bad in text for bad in bad_words):
                    jobs.append(full_job)

    except Exception as e:
        print("RemoteOK error:", e)

    print("RemoteOK jobs:", len(jobs))
    return jobs
def get_weworkremotely_jobs():
    url = "https://weworkremotely.com/remote-jobs/search?term=python"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    jobs = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print("WWR status:", response.status_code)

        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.find_all("a", href=True)

        print("Total links found:", len(links))

        for link in links:
            text = link.get_text(" ", strip=True)

            if text and ("python" in text.lower() or "developer" in text.lower()):
                job_link = "https://weworkremotely.com" + link["href"]

                full_job = f"{text}\n{job_link}"

                jobs.append(full_job)

        print("WWR jobs:", len(jobs))

    except Exception as e:
        print("WWR error:", e)

    return jobs

        soup = BeautifulSoup(response.text, "html.parser")
        listings = soup.find_all("section", class_="jobs")
        print("WWR sections found:", len(listings))

        for section in listings:
            for li in section.find_all("li"):
                title_tag = li.find("span", class_="title")
                company_tag = li.find("span", class_="company")
                link_tag = li.find("a")

                if title_tag and company_tag and link_tag and link_tag.get("href"):
                    title = title_tag.get_text(strip=True)
                    company = company_tag.get_text(strip=True)
                    job_link = "https://weworkremotely.com" + link_tag.get("href")

                    full_job = f"{title} at {company}\n{job_link}"

                    text = f"{title} {company} {li.get_text(' ', strip=True)}".lower()

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

                    if any(word in text for word in keywords) and not any(bad in text for bad in bad_words):
                        jobs.append(full_job)

    except Exception as e:
        print("WWR error:", e)

    print("WWR jobs:", len(jobs))
    return jobs


while True:
    print("\n--- Running job check ---")

    seen_jobs = load_seen_jobs()

    remoteok_jobs = get_remoteok_jobs()
    wwr_jobs = get_weworkremotely_jobs()

    jobs = remoteok_jobs + wwr_jobs
    print("Combined jobs:", len(jobs))

    jobs = list(dict.fromkeys(jobs))
    print("Unique combined jobs:", len(jobs))

    new_jobs = []

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
