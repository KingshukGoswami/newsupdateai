import os
import json
import requests
import feedparser
from dotenv import load_dotenv
from datetime import datetime
from dateutil import parser as date_parser

# Load environment variables
load_dotenv()

# Load user config
def load_user_config(path="user_config.json"):
    with open(path, "r") as f:
        return json.load(f)

def fetch_news_from_newsapi(config, api_key):
    params = {
        "apiKey": api_key,
        "language": config["language"],
        "country": config.get("country"),
        "category": config.get("category"),
        "q": config.get("keyword"),
        "pageSize": config.get("page_size", 30),
    }
    try:
        resp = requests.get("https://newsapi.org/v2/top-headlines", params=params)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return [
            {
                "title": a["title"],
                "description": a["description"],
                "content": a.get("content"),
                "url": a["url"],
                "source": a["source"]["name"],
                "publishedAt": a["publishedAt"]
            }
            for a in articles if a["title"] and a["description"]
        ]
    except Exception as e:
        print(f"[NewsAPI Error] {e}")
        return []

def fetch_news_from_gnews(config, api_key):
    params = {
        "token": api_key,
        "lang": config["language"],
        "country": config.get("country", "us"),
        "max": config.get("page_size", 30),
        "q": config.get("keyword", "")
    }
    try:
        resp = requests.get("https://gnews.io/api/v4/top-headlines", params=params)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return [
            {
                "title": a["title"],
                "description": a["description"],
                "content": a.get("content"),
                "url": a["url"],
                "source": a["source"]["name"],
                "publishedAt": a["publishedAt"]
            }
            for a in articles if a["title"] and a["description"]
        ]
    except Exception as e:
        print(f"[GNews Error] {e}")
        return []

def fetch_news_from_mediastack(config, api_key):
    params = {
        "access_key": api_key,
        "languages": config["language"],
        "countries": config.get("country"),
        "keywords": config.get("keyword"),
        "limit": config.get("page_size", 30),
        "sort": "published_desc"
    }
    try:
        resp = requests.get("http://api.mediastack.com/v1/news", params=params)
        resp.raise_for_status()
        articles = resp.json().get("data", [])
        return [
            {
                "title": a["title"],
                "description": a["description"],
                "content": a.get("description"),
                "url": a["url"],
                "source": a["source"],
                "publishedAt": a["published_at"]
            }
            for a in articles if a["title"] and a["description"]
        ]
    except Exception as e:
        print(f"[Mediastack Error] {e}")
        return []

def fetch_news_from_rss(url, source_name):
    try:
        feed = feedparser.parse(url)
        return [
            {
                "title": entry.title,
                "description": entry.get("summary", ""),
                "content": entry.get("summary", ""),
                "url": entry.link,
                "source": source_name,
                "publishedAt": entry.get("published", datetime.utcnow().isoformat())
            }
            for entry in feed.entries
        ]
    except Exception as e:
        print(f"[RSS Error] {e}")
        return []

def fetch_filtered_news():
    config = load_user_config()

    # Load API keys from env or file
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
    MEDIASTACK_API_KEY = os.getenv("MEDIASTACK_API_KEY")

    all_articles = []

    # Fetch from NewsAPI
    if NEWS_API_KEY:
        all_articles.extend(fetch_news_from_newsapi(config, NEWS_API_KEY))

    # Fetch from GNews
    if GNEWS_API_KEY:
        all_articles.extend(fetch_news_from_gnews(config, GNEWS_API_KEY))

    # Fetch from Mediastack
    if MEDIASTACK_API_KEY:
        all_articles.extend(fetch_news_from_mediastack(config, MEDIASTACK_API_KEY))

    # Fetch from RSS feeds
    rss_feeds = [
        ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
        ("https://www.reutersagency.com/feed/?best-topics=world&post_type=best", "Reuters"),
        ("https://www.aljazeera.com/xml/rss/all.xml", "Al Jazeera"),
        ("https://www.theguardian.com/world/rss", "The Guardian")
    ]
    for url, name in rss_feeds:
        all_articles.extend(fetch_news_from_rss(url, name))

    # Deduplicate by title
    unique_articles = {a["title"]: a for a in all_articles}.values()

    # Sort by published date
    sorted_articles = sorted(
        unique_articles,
        key=lambda x: date_parser.parse(x["publishedAt"]) if x["publishedAt"] else datetime.min,
        reverse=True
    )

    # Limit to top 15
    return sorted_articles[:30]

# Test
if __name__ == "__main__":
    top_news = fetch_filtered_news()
    for i, news in enumerate(top_news, 1):
        print(f"{i}. {news['title']} ({news['source']})")
        print(f"   {news['description']}\n")
