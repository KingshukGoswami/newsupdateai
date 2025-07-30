import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load env and config
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def load_user_config(path="user_config.json"):
    with open(path, "r") as f:
        return json.load(f)

def fetch_filtered_news():
    config = load_user_config()

    with open("api_key.json") as api_key_file:
        api_key = json.load(api_key_file)

    params = {
        "apiKey": api_key["api_key"],
        "language": config["language"],
        "country": config.get("country"),
        "category": config.get("category"),
        "q": config.get("keyword"),
        "pageSize": config.get("page_size", 30),
    }

    response = requests.get("https://newsapi.org/v2/top-headlines", params=params)
    response.raise_for_status()
    articles = response.json().get("articles", [])

    news_list = []
    for article in articles:
        if article["title"] and article["description"]:
            news = {
                "title": article["title"],
                "description": article["description"],
                "content": article.get("content"),
                "url": article["url"],
                "source": article["source"]["name"],
                "publishedAt": article["publishedAt"]
            }
            news_list.append(news)

    # Sort by date and pick top 10
    top_10 = sorted(news_list, key=lambda x: x["publishedAt"], reverse=True)[:10]
    return top_10

# Test
if __name__ == "__main__":
    top_news = fetch_filtered_news()
    for i, news in enumerate(top_news, 1):
        print(f"{i}. {news['title']} ({news['source']})")
        print(f"   {news['description']}\n")
