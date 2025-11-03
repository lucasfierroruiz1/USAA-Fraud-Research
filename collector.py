import requests
from bs4 import BeautifulSoup
from uuid import uuid4
from datetime import datetime

from config import KEYWORDS
from models import train_keyword_model
from utils import summarize_text, extract_keywords
from supabase_client import supabase

# Train the keyword-based model
vectorizer, model = train_keyword_model(KEYWORDS)

def flag_article(text):
    X_test = vectorizer.transform([text.lower()])
    return model.predict(X_test)[0] == 1

def scrape_articles(pages=5):
    base_url = "https://techcrunch.com/page/"
    articles = []

    for page_num in range(1, pages + 1):
        url = f"{base_url}{page_num}/"
        print(f"Scraping {url}")
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Save raw HTML for inspection
        with open(f"techcrunch_page_{page_num}.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        for card in soup.find_all("div", class_="loop-card"):
            title_tag = card.find("h3")
            link_tag = title_tag.find("a") if title_tag else None
            meta_tag = card.find("div", class_="loop-card__meta")

            if not link_tag or not link_tag.get("href"):
                continue

            title = link_tag.get_text(strip=True)
            link = link_tag["href"]
            date = meta_tag.get_text(strip=True) if meta_tag else "Unknown date"

            articles.append({
                "title": title,
                "url": link,
                "date": date
            })

    return articles

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import re

# Step 1: Keywords to flag articles
keywords = [
    "fraud", "scam", "phishing", "cybercrime", "hacking", "data breach", 
    "identity theft", "malware", "ransomware", "social engineering",
    "money laundering", "credit card fraud", "sms spam", "phishing page",
    "fake website", "stolen data", "cryptocurrency scam", "cyber attack",
    "unauthorized access", "supply chain attack", "botnet", "AI scam",
    "encrypted messaging", "deep web", "dark web"
]

# Simplified model training for demo purposes (use real labeled data for production)
# Here, training on presence of keywords to flag fraud articles
def train_simple_keyword_model(keywords):
    X_train = keywords
    y_train = [1]*len(keywords)  # Assume all keywords = fraud related
    vectorizer = TfidfVectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train)
    model = LogisticRegression()
    model.fit(X_train_tfidf, y_train)
    return vectorizer, model

vectorizer, model = train_simple_keyword_model(keywords)

def flag_article(text):
    text = text.lower()
    X_test = vectorizer.transform([text])
    pred = model.predict(X_test)
    return pred[0] == 1

def summarize_text(text, max_sentences=3):
    # Simple summarization: return first max_sentences sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    return ' '.join(sentences[:max_sentences])

# Step 2: Scrape TechCrunch homepage article titles and URLs
def scrape_homepage():
    url = "https://techcrunch.com"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []
    for tag in soup.find_all("div", class_="post-block post-block--image post-block--unread"):
        title_tag = tag.find("a", class_="post-block__title__link")
        if not title_tag:
            continue
        title = title_tag.get_text().strip()
        link = title_tag['href']

        # Flag article if title contains any keyword
        if any(keyword in title.lower() for keyword in keywords):
            articles.append({"title": title, "url": link})
    return articles

# Step 3: Scrape full article content for flagged articles
def scrape_article(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    content_div = soup.find("div", class_="wp-block-post-content")
    if not content_div:
        return ""
    paragraphs = content_div.find_all("p")
<<<<<<< HEAD
    return ' '.join(p.get_text().strip() for p in paragraphs if p.get_text())

def insert_raw_article(title, url, full_text, source="TechCrunch"):
    keywords_found = extract_keywords(full_text, KEYWORDS)
    raw_id = str(uuid4())
    supabase.table("raw_articles").insert({
        "id": raw_id,
        "title": title,
        "url": url,
        "keywords": ', '.join(keywords_found),
        "full_text": full_text,
        "source": source,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return raw_id, keywords_found

def insert_clean_article(raw_id, summary, keywords, flagged, score=1.0):
    supabase.table("clean_articles").insert({
        "id": str(uuid4()),
        "raw_id": raw_id,
        "summary": summary,
        "keywords": ', '.join(keywords),
        "flagged": int(flagged),
        "score": score,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

def main():
    articles = scrape_articles(pages=5)
    print(f"Scraped {len(articles)} articles")

    # 🔍 Print each scraped article for debugging
    for a in articles:
        print(f"- {a['title']}: {a['url']}")

    for article in articles:
        content = scrape_article(article['url'])
        if content:
            raw_id, raw_keywords = insert_raw_article(article['title'], article['url'], content)
            flagged = flag_article(content)
            summary = summarize_text(content)
            insert_clean_article(raw_id, summary, raw_keywords, flagged, score=1.0 if flagged else 0.0)
            if flagged:
                print(f"✅ Flagged: {article['title']}")
                print(f"Summary: {summary}")
                print("-" * 80)

if __name__ == "__main__":
    main()
=======
    content = ' '.join(p.get_text().strip() for p in paragraphs if p.get_text())
    return content

def main():
    flagged_articles = scrape_homepage()
    for article in flagged_articles:
        content = scrape_article(article['url'])
        if content and flag_article(content):
            summary = summarize_text(content)
            print(f"Title: {article['title']}")
            print(f"URL: {article['url']}")
            print(f"Summary: {summary}")
            print("-" * 80)

if __name__ == "__main__":
    main()
>>>>>>> 17f3f43e9847635fcd7f9e46e98d87515ebcf68a
