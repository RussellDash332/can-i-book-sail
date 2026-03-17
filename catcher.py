import os
import re
import time
import codecs
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

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
    )

with requests.Session() as session:
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    start_time = time.time()

    for _ in range(6):
        for URL in [codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/thyvanmun", "rot13"), codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/cnbcnbzngr", "rot13")]:
            while True:
                try:
                    r = session.get(URL)
                    if r.status_code == 200:
                        rank, point = get_stats(r.text)
                        now_str = datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S")
                        msg = f"{URL.split('/')[-1]} as of {now_str} is rank {rank} with {point} points."
                        print(msg)
                        send_telegram(msg, session)
                        break
                    else:
                        print(f"Retrying due to status code {r.status_code}")
                except Exception as e:
                    print(f"Retrying due to {type(e)}: {e}")
            
        time.sleep(600)
