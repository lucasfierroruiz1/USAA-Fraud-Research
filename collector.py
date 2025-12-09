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

def scrape_articles(pages=10):
    base_url = "https://techcrunch.com/page/"
    articles = []

    for page_num in range(1, pages + 1):
        url = f"{base_url}{page_num}/"
        print(f"Scraping {url}")
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching page {url}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

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
    try:
        print(f"Fetching article: {url}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.TooManyRedirects:
        print(f"⚠️ Skipping {url} due to redirect loop")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return ""

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

from utils import embed_text

def insert_clean_article(raw_id, summary, keywords_found, title, url):
    if not keywords_found:
        return  # Skip inserting if no keywords found

    flagged = True
    score = round(len(keywords_found) * 0.10, 2)
    keywords = ', '.join(sorted(set(kw.strip() for kw in keywords_found)))

    embedding = embed_text(summary)  # generate embedding from summary

    supabase.table("clean_articles").insert({
        "id": str(uuid4()),
        "raw_id": raw_id,
        "summary": summary,
        "keywords": keywords,
        "flagged": flagged,
        "score": score,
        "title": title,
        "url": url,
        "embedding": embedding,   # new field
        "created_at": datetime.utcnow().isoformat()
    }).execute()


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

def main(pages=5):
    articles = scrape_articles(pages=pages)
    scraped_count = len(articles)
    flagged_count = 0

    print(f"Scraped {scraped_count} articles")

    for article in articles:
        content = scrape_article(article['url'])
        if content:
            raw_id, raw_keywords = insert_raw_article(article['title'], article['url'], content)
            summary = summarize_text(content)
            insert_clean_article(raw_id, summary, raw_keywords, article["title"], article["url"])
            if raw_keywords:
                flagged_count += 1
                print(f"✅ Flagged: {article['title']}")
                print(f"Summary: {summary}")
                print("-" * 80)

    # Save run stats into scrape_runs
    supabase.table("scrape_runs").insert({
        "id": str(uuid4()),
        "scraped_count": scraped_count,
        "flagged_count": flagged_count,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    print(f"📊 Run complete: Scraped {scraped_count}, Flagged {flagged_count}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape TechCrunch articles and insert into Supabase")
    parser.add_argument("--pages", type=int, default=5, help="Number of TechCrunch pages to scrape")
    args = parser.parse_args()

    main(pages=args.pages)
    deduplicate_clean_articles()