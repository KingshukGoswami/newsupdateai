import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS").split(",")


def build_html(news_items):
    html = "<h2>📰 Daily News Update</h2><br>"
    for i, item in enumerate(news_items, 1):
        html += f"<h3>{i}. {item['title']}</h3>"
        html += f"<p><strong>Source:</strong> {item['source']}<br>"
        html += f"<strong>Published At:</strong> {item['publishedAt']}<br>"
        html += f"<a href='{item['url']}'>Read full article</a></p><hr>"
    return html


def send_news_email(news_items):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📰 Your Daily News Digest"
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECIPIENTS)

    html_content = build_html(news_items)
    msg.attach(MIMEText(html_content, "html"))

    try:
        # Use Outlook SMTP
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENTS, msg.as_string())
        print("✅ Email sent successfully via Outlook.")
    except Exception as e:
        print(f"❌ Failed to send email via Outlook: {e}")


# Example Usage
if __name__ == "__main__":
    from fetch_news_filter import fetch_filtered_news

    top_news = fetch_filtered_news()
    send_news_email(top_news)
