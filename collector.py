import requests
from bs4 import BeautifulSoup
from uuid import uuid4
from datetime import datetime
import re

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

def scrape_article(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    content_div = soup.find("div", class_="wp-block-post-content")
    if not content_div:
        return ""
    paragraphs = content_div.find_all("p")
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