import os
import json
import feedparser
import smtplib
from email.mime.text import MIMEText

from oa_detector import is_open_access

STATE_FILE = "state.json"

RSS_FEEDS = {
    "MIT Press": "https://mitpress.mit.edu/feed/",
    "Oxford UP": "https://academic.oup.com/rss",
    "Cambridge UP": "https://www.cambridge.org/core/rss",
    "Princeton UP": "https://press.princeton.edu/rss",
    "Harvard UP": "https://www.hup.harvard.edu/rss",
    "UCL Press": "https://uclpress.co.uk/pages/rss",

    "Harvard University": "https://news.harvard.edu/gazette/feed/",
    "MIT": "https://news.mit.edu/rss/feed",
    "Stanford": "https://news.stanford.edu/feed/",
    "Oxford": "https://www.ox.ac.uk/news/rss.xml",
    "Cambridge": "https://www.cam.ac.uk/news/rss.xml",
    "ETH Zurich": "https://ethz.ch/en/news-and-events/eth-news/news.rss",
}

def load_seen():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_seen(seen: set):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        # Son 5000 kaydı tut (dosya şişmesin)
        json.dump(list(seen)[-5000:], f)

def send_email(subject: str, body: str):
    user = os.environ["SMTP_USER"]
    pwd  = os.environ["SMTP_PASS"]
    to   = os.environ["TO_EMAIL"]

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pwd)
        s.sendmail(user, [to], msg.as_string())

def run():
    seen = load_seen()

    normal_items = []
    open_access_items = []

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        for e in feed.entries[:20]:
            uid = e.get("id") or e.get("link")
            if not uid or uid in seen:
                continue

            title = e.get("title", "Untitled")
            link = e.get("link", "")
            entry_text = f"[{source}] {title}\n{link}\n"

            if is_open_access(title, link):
                open_access_items.append(entry_text)
            else:
                normal_items.append(entry_text)

            seen.add(uid)

    # state'i bir kere kaydet
    save_seen(seen)

    # Normal yayın maili
    if normal_items:
        send_email(
            f"Academic Radar – {len(normal_items)} yeni yayın",
            "\n".join(normal_items[:50])
        )

    # Open Access ayrı mail
    if open_access_items:
        send_email(
            f"🟢 Academic Radar – OPEN ACCESS ({len(open_access_items)})",
            "\n".join(open_access_items[:50])
        )

if __name__ == "__main__":
    run()
