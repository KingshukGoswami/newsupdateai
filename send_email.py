import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fetch_news_filter import fetch_filtered_news  # Assumes this function exists and works

# Load from email_config.json
with open("email_config.json") as config_file:
    config = json.load(config_file)

EMAIL_SENDER = config["EMAIL_SENDER"]
EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
EMAIL_RECIPIENTS = config["EMAIL_RECIPIENTS"]  # Should be a list


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
        with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENTS, msg.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


# Run the email sender
if __name__ == "__main__":
    top_news = fetch_filtered_news()
    print (top_news)
    send_news_email(top_news)
