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

RANK_PATTERN = re.compile(r'Rank</span>[\n\s]*<span class="important_text">([\d,]+)</span>')
SCORE_PATTERN = re.compile(r'Score</span>[\n\s]*<span class="important_text">([\d.]+)</span>')

def get_stats(html: str):
    rank_m = RANK_PATTERN.search(html)
    score_m = SCORE_PATTERN.search(html)
    rank = rank_m.group(1) if rank_m else "??"
    point = score_m.group(1) if score_m else "??"
    return rank, point

def send_telegram(text: str, session: requests.Session):
    session.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
    )

with requests.Session() as session:
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    start_time = time.time()

    for _ in range(3):
        urls = [
            codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/kvnbjhp1", "rot13"),
            codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/ngyv-snaane-senaxyva", "rot13"),
            codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/znvfr-fgreyvat", "rot13"),
            codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/fcbbxljbbxl", "rot13"),
            codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/puhat-lna-pubj", "rot13"),
            codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/yi0flf", "rot13"),
            codecs.decode("uggcf://bcra.xnggvf.pbz/hfref/uenag-ubiunaavflna", "rot13"),
        ]
        stats = []
        for URL in urls:
            while True:
                try:
                    r = session.get(URL)
                    if r.status_code == 200:
                        rank, point = get_stats(r.text)
                        name = URL.split('/')[-1]
                        stats.append((name, rank, point))
                        break
                    else:
                        print(f"Retrying due to status code {r.status_code}")
                except Exception as e:
                    print(f"Retrying due to {type(e)}: {e}")

        stats.sort(key=lambda x: int(x[1].replace(',', '')) if x[1].replace(',', '').isdigit() else float('inf'))

        now_str = datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S")
        msg_lines = [f"<b>{name}<b>\nrank = {rank}, score = {point}\n" for name, rank, point in stats]
        msg = "\n".join(msg_lines) + f"\nLast Updated: {now_str}"

        print(msg)
        send_telegram(msg, session)

        time.sleep(1200)
