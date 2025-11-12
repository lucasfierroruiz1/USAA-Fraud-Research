import requests
from bs4 import BeautifulSoup
from uuid import uuid4
from datetime import datetime
from collections import defaultdict
from dateutil.parser import parse

from config import KEYWORDS
from models import train_keyword_model
from utils import summarize_text, extract_keywords
from supabase_client import supabase

# Train the keyword-based model
vectorizer, model = train_keyword_model(KEYWORDS)

def extract_keywords(text, keyword_list):
    text_lower = text.lower()
    return [kw.strip() for kw in keyword_list if kw.strip() in text_lower]

def flag_article(text):
    found = extract_keywords(text, KEYWORDS)
    return len(found) >= 1

def scrape_articles(pages=5):
    base_url = "https://techcrunch.com/page/"
    articles = []

    for page_num in range(1, pages + 1):
        url = f"{base_url}{page_num}/"
        print(f"Scraping {url}")
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

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
    existing = supabase.table("raw_articles").select("id", "full_text").eq("url", url).execute()
    if existing.data:
        raw_id = existing.data[0]["id"]
        keywords_found = extract_keywords(existing.data[0]["full_text"], KEYWORDS)
        return raw_id, keywords_found

    keywords_found = extract_keywords(full_text, KEYWORDS)
    raw_id = str(uuid4())
    supabase.table("raw_articles").insert({
        "id": raw_id,
        "title": title,
        "url": url,
        "keywords": ', '.join(sorted(set(kw.strip() for kw in keywords_found))),
        "full_text": full_text,
        "source": source,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return raw_id, keywords_found

def insert_clean_article(raw_id, summary, keywords_found, title, url):
    if not keywords_found:
        return  # Skip inserting if no keywords found

    flagged = True
    score = round(len(keywords_found) * 0.10, 2)
    keywords = ', '.join(sorted(set(kw.strip() for kw in keywords_found)))

    supabase.table("clean_articles").insert({
        "id": str(uuid4()),
        "raw_id": raw_id,
        "summary": summary,
        "keywords": keywords,
        "flagged": flagged,
        "score": score,
        "title": title,
        "url": url,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

def compute_score(found_keywords):
    return round(len(found_keywords) * 0.10, 2)

def deduplicate_clean_articles():
    response = supabase.table("clean_articles").select("*").execute()
    articles = response.data

    grouped = defaultdict(list)
    for article in articles:
        raw = supabase.table("raw_articles").select("url").eq("id", article["raw_id"]).execute()
        if raw.data:
            url = raw.data[0]["url"]
            grouped[url].append(article)

    duplicates = []
    for url, group in grouped.items():
        if len(group) > 1:
            sorted_group = sorted(group, key=lambda x: parse(x["created_at"]), reverse=True)
            duplicates.extend(sorted_group[1:])  # Keep newest, delete rest

    for article in duplicates:
        print(f"🗑️ Removing duplicate: {article['raw_id']} (ID: {article['id']})")
        supabase.table("clean_articles").delete().eq("id", article["id"]).execute()

    print(f"✅ Deleted {len(duplicates)} duplicate rows from clean_articles.")

def main():
    articles = scrape_articles(pages=5)
    print(f"Scraped {len(articles)} articles")

    for a in articles:
        print(f"- {a['title']}: {a['url']}")

    for article in articles:
        content = scrape_article(article['url'])
        if content:
            raw_id, raw_keywords = insert_raw_article(article['title'], article['url'], content)
            summary = summarize_text(content)
            insert_clean_article(raw_id, summary, raw_keywords, article["title"], article["url"])
            if raw_keywords:
                print(f"✅ Flagged: {article['title']}")
                print(f"Summary: {summary}")
                print("-" * 80)

if __name__ == "__main__":
    main()
    deduplicate_clean_articles()