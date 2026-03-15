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

RANK_PATTERN = re.compile(r'Rank</span><span class="important_text">([\d,]+)</span>')
SCORE_PATTERN = re.compile(r'Score</span><span class="important_text">([\d.]+)</span>')

def get_stats(html: str):
    rank_m = RANK_PATTERN.search(html)
    score_m = SCORE_PATTERN.search(html)
    rank = rank_m.group(1) if rank_m else "Unknown"
    point = score_m.group(1) if score_m else "Unknown"
    return rank, point

def send_telegram(text: str, session: requests.Session):
    session.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=10,
    )

with requests.Session() as session:
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    start_time = time.time()
    
    while time.time() - start_time < 21000:
        try:
            r = session.get(URL, timeout=10)
            if r.status_code == 200:
                rank, point = get_stats(r.text)
                now_str = datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S")
                msg = f"gulinazha as of {now_str} is rank {rank} with {point} points."
                print(msg)
                send_telegram(msg, session)
            else:
                print(f"Error {r.status_code}")
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(600)
