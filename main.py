import os, json
import feedparser
import smtplib
from email.mime.text import MIMEText

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
    except:
        return set()

def save_seen(seen):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen)[-5000:], f)

def send_email(subject, body):
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
    new_items = []

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for e in feed.entries[:20]:
            uid = e.get("id") or e.get("link")
            if uid and uid not in seen:
                title = e.get("title", "Untitled")
                link = e.get("link", "")
                new_items.append(f"[{source}] {title}\n{link}\n")
                seen.add(uid)

    save_seen(seen)

    if new_items:
        send_email(
            f"Academic Radar – {len(new_items)} yeni yayın",
            "\n".join(new_items[:50])
        )

if __name__ == "__main__":
    run()
