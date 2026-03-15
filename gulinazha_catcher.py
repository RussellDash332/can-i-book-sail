import os
import re
import time
import codecs
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

URL = codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/thyvanmun", "rot13")
SGT = ZoneInfo("Asia/Singapore")

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Precise patterns for Kattis profile sidebar: <span class="important">Rank: 1,234</span>
RANK_PATTERN = re.compile(r'Rank:\s*([\d,]+)', re.IGNORECASE)
SCORE_PATTERN = re.compile(r'Score:\s*([\d.]+)', re.IGNORECASE)

def get_stats(html: str):
    rank_m = RANK_PATTERN.search(html)
    score_m = SCORE_PATTERN.search(html)
    rank = rank_m.group(1) if rank_m else "Unknown"
    score = score_m.group(1) if score_m else "Unknown"
    return rank, score

def send_telegram(text: str, session: requests.Session):
    session.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=10,
    )

with requests.Session() as session:
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    start_time = time.time()
    
    for _ in range(6):
        try:
            r = session.get(URL, timeout=10)
            if r.status_code == 200:
                rank, point = get_stats(r.text)
                now_str = datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S")
                msg = f"gulinazha as of {now_str} is rank {rank} with {point} points."
                print(msg)
                send_telegram(msg, session)
            else:
                print(f"Error {r.status_code} at {datetime.now(SGT)}")
        except Exception as e:
            print(f"Loop error: {e}")
            
        time.sleep(600)
