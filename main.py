import os
import re
import time
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

URL = "https://www.dbs.com/sailing/index.html"
SGT = ZoneInfo("Asia/Singapore")

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
IS_CRON = os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
print([os.environ.get("GITHUB_EVENT_NAME"), __name__])

MONTH_PATTERN = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+Registration",
    re.IGNORECASE
)

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}


def get_displayed_month(html: str):
    m = MONTH_PATTERN.search(html)
    if not m:
        return None
    name = m.group(1)
    return MONTH_MAP[name.lower()], name


def send_telegram(text: str, session: requests.Session):
    print(f'send_telegram({text}, session)')
    session.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=10,
    ).raise_for_status()


def check_once(session: requests.Session):
    print('check_once(session)')
    now = datetime.now(SGT)
    current_month = now.month
    next_month = 1 if current_month == 12 else current_month + 1

    r = session.get(URL, timeout=10)
    r.raise_for_status()

    result = get_displayed_month(r.text)
    if result is None:
        send_telegram("DBS Sailing: Could not detect registration month.", session)
        return

    displayed_month_num, displayed_month_name = result

    if displayed_month_num == next_month:
        send_telegram(
            f"DBS Sailing switched to {displayed_month_name}.",
            session
        )


def run_cron_mode(session: requests.Session):
    print('run_cron_mode(session)')
    now = datetime.now(SGT)

    # Target time today 23:55
    target = now.replace(hour=23, minute=55, second=0, microsecond=0)

    # If before 23:55, wait
    if now < target:
        time.sleep((target - now).total_seconds())

    # Always run 10 checks regardless of current time
    for _ in range(10):
        check_once(session)
        time.sleep(60)


def main():
    print('main()')
    with requests.Session() as session:
        session.headers.update({"User-Agent": "Mozilla/5.0"})

        if IS_CRON:
            run_cron_mode(session)
        else:
            check_once(session)

main()
