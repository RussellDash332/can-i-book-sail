import os
import re
import time
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

URL = "https://open.kattis.com/users/gulinazha"
SGT = ZoneInfo("Asia/Singapore")

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

RANK_PATTERN = re.compile(r'Rank\D+([\d,]+)', re.IGNORECASE)
POINT_PATTERN = re.compile(r'Score\D+([\d.]+)', re.IGNORECASE)

def get_stats(html: str):
    rank_m = RANK_PATTERN.search(html)
    point_m = POINT_PATTERN.search(html)
    rank = rank_m.group(1) if rank_m else "Unknown"
    point = point_m.group(1) if point_m else "Unknown"
    return rank, point

def send_telegram(text: str, session: requests.Session):
    session.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=10,
    )

with requests.Session() as session:
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    
    while True:
        r = session.get(URL, timeout=10)
        rank, point = get_stats(r.text)
        
        now_str = datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S")
        msg = f"gulianzaha as of {now_str} is rank {rank} with {point} points."
        
        print(msg)
        send_telegram(msg, session)
        
        time.sleep(600)
