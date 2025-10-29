import requests
from bs4 import BeautifulSoup
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
