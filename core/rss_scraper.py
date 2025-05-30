import feedparser
import os
import json
from datetime import datetime
from collections import defaultdict

RSS_FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "SkySports": "https://www.skysports.com/rss/12040",
    "Guardian": "https://www.theguardian.com/football/rss",
}

DATA_DIR = "data/rss_by_day"
os.makedirs(DATA_DIR, exist_ok=True)

def parse_feed(source, url, seen_urls):
    print(f"[{source}] Fetching feed...")
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        if entry.link in seen_urls:
            continue

        pub_date = entry.get("published", datetime.utcnow().isoformat())
        try:
            date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            pub_date = date_obj.isoformat()
        except Exception:
            pass

        article = {
            "title": entry.title,
            "url": entry.link,
            "summary": entry.get("summary", ""),
            "date": pub_date,
            "source": source
        }
        articles.append(article)
        seen_urls.add(entry.link)

    print(f"[{source}] Collected {len(articles)} new articles")
    return articles

def load_seen_urls():
    seen = set()
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            path = os.path.join(DATA_DIR, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    seen.update(article["url"] for article in data if "url" in article)
            except Exception:
                continue
    return seen

def save_by_day(all_articles):
    grouped = defaultdict(list)

    for article in all_articles:
        try:
            date_obj = datetime.strptime(article["date"][:10], "%Y-%m-%d")
        except ValueError:
            date_obj = datetime.utcnow()
        date_key = date_obj.strftime("%Y-%m-%d")
        grouped[date_key].append(article)

    for date, new_items in grouped.items():
        file_path = os.path.join(DATA_DIR, f"{date}.json")

        existing_items = []
        seen_urls = set()

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing_items = json.load(f)
                seen_urls.update(item["url"] for item in existing_items)

        fresh_articles = [
            item for item in new_items if item["url"] not in seen_urls
        ]

        all_combined = existing_items + fresh_articles

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_combined, f, indent=2, ensure_ascii=False)

        print(f"[Saved] {len(fresh_articles)} new articles (total: {len(all_combined)}) to {file_path}")

def run_all_rss_scrapers():
    all_articles = []
    seen_urls = load_seen_urls()
    for source, url in RSS_FEEDS.items():
        try:
            articles = parse_feed(source, url, seen_urls)
            all_articles.extend(articles)
        except Exception as e:
            print(f"[{source}] Failed to parse feed:", e)

    save_by_day(all_articles)
    print(f" Done! Total new articles saved: {len(all_articles)}")

if __name__ == "__main__":
    run_all_rss_scrapers()

