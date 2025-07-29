import os
import openai
from dotenv import load_dotenv

# Load OpenAI API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_news_item(title, content):
    prompt = (
        f"News Title: {title}\n\n"
        f"Full Content: {content}\n\n"
        "Give me:\n"
        "1. A short gist (1-2 lines)\n"
        "2. A detailed explanation (2-3 paragraphs)\n"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"Error summarizing news: {e}")
        return "Summary not available."

# Example Usage
if __name__ == "__main__":
    from fetch_news import fetch_filtered_news
    top_news = fetch_filtered_news()

    for item in top_news:
        print(f"📰 {item['title']}")
        summary = summarize_news_item(item['title'], item['content'] or item['description'])
        print(summary, "\n" + "-"*80 + "\n")

