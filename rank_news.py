import json
import requests
import feedparser
from bs4 import BeautifulSoup
import re

# =======================
# Load Configs & API Keys
# =======================
with open("user_config.json") as f:
    user_config = json.load(f)

with open("api_key.json") as f:
    api_keys = json.load(f)

LANGUAGE = user_config.get("language", "en")
CATEGORY = ",".join(user_config.get("category", []))
KEYWORD = user_config.get("keyword", "")
PAGE_SIZE = user_config.get("page_size", 20)

RSS_FEEDS = user_config.get("rss_feeds", [
    "https://news.ycombinator.com/rss",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
])

# ==================================
# Fetch news from different sources
# ==================================
def fetch_gnews():
    base_url = "https://gnews.io/api/v4/search"
    params = {
        "q": KEYWORD,
        "lang": LANGUAGE,
        "token": api_keys["GNEWS_API_KEY"],
        "max": PAGE_SIZE
    }
    r = requests.get(base_url, params=params).json()
    return [{"title": a["title"], "url": a["url"], "source": a["source"]["name"]} for a in r.get("articles", [])]

def fetch_newsapi():
    base_url = "https://newsapi.org/v2/everything"
    params = {
        "q": KEYWORD,
        "language": LANGUAGE,
        "pageSize": PAGE_SIZE,
        "apiKey": api_keys["NEWS_API_KEY"]
    }
    r = requests.get(base_url, params=params).json()
    return [{"title": a["title"], "url": a["url"], "source": a["source"]["name"]} for a in r.get("articles", [])]

def fetch_mediastack():
    base_url = "http://api.mediastack.com/v1/news"
    params = {
        "access_key": api_keys["MEDIASTACK_API_KEY"],
        "languages": LANGUAGE,
        "keywords": KEYWORD,
        "limit": PAGE_SIZE
    }
    r = requests.get(base_url, params=params).json()
    return [{"title": a["title"], "url": a["url"], "source": a["source"]} for a in r.get("data", [])]

def fetch_rss():
    articles = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if KEYWORD.lower() in entry.title.lower() or KEYWORD.lower() in getattr(entry, "summary", "").lower():
                articles.append({
                    "title": entry.title,
                    "url": entry.link,
                    "source": feed.feed.get("title", "RSS")
                })
    return articles

# ======================
# Merge & Deduplicate
# ======================
def merge_articles(*sources):
    seen = set()
    merged = []
    for source_list in sources:
        for art in source_list:
            if art["url"] not in seen:
                seen.add(art["url"])
                merged.append(art)
    return merged

# ==========================
# Fetch full text & Summarize
# ==========================
def get_article_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        paragraphs = soup.find_all("p")
        text = "\n".join(
            p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50
        )
        return text.strip()
    except Exception as e:
        return ""

def create_summary(text, max_sentences=2):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return " ".join(sentences[:max_sentences]) if sentences else ""

# ======================
# Main Execution
# ======================
if __name__ == "__main__":
    gnews_articles = fetch_gnews()
    newsapi_articles = fetch_newsapi()
    mediastack_articles = fetch_mediastack()
    rss_articles = fetch_rss()

    MAX_NEWS = 15
    all_articles = merge_articles(
        gnews_articles, 
        newsapi_articles, 
        mediastack_articles, 
        rss_articles
    )[:MAX_NEWS]

    # Print headlines list
    print("\nHEADLINES:\n")
    for idx, art in enumerate(all_articles, 1):
        print(f"{idx}. {art['title']}")

    # Expanded news section
    print("\n-------------- Expanded news of the headlines -------------\n")
    for idx, art in enumerate(all_articles, 1):
        full_text = get_article_text(art["url"])
        summary_text = create_summary(full_text) if full_text else "No content available."
        print(f"{idx}. {art['title']} ({art['source']})")
        print(f"Summary: {summary_text}")
        print(f"Full Article: {full_text if full_text else 'No content could be retrieved.'}")
        print()

