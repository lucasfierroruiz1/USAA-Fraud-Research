# USAA Fraud Research Dashboard 🔍  
**Scrape → Detect → Summarize → Visualize**  
*Authors: Elver, Lucas, Precious, Zack*  

---

 Project Summary
A pipeline that scrapes TechCrunch articles, detects fraud content, summarizes flagged entries, and visualizes fraud trends in a Streamlit dashboard powered by Supabase.  


 Quick Start
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

Creating an .env file:
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key

Running the dashboard:
uv run streamlit run streamlit_app.py

Our Process Diagram:
flowchart TD
    A[Scraper: collector.py] --> B[Supabase: raw_articles]
    B --> C[Keyword Detection + Summarization]
    C --> D[Supabase: clean_articles]
    D --> E[Deduplication Logic]
    E --> F[Streamlit Dashboard]
    F --> G[Visualizations: Word Cloud, Bar Charts, Timelines]

Folder Structure:
USAA-Fraud-Research/
├── collector.py        # Scraper + deduplication logic
├── streamlit_app.py    # Streamlit dashboard
├── utils.py            # Summarization + keyword extraction
├── requirements.txt    # Dependencies
├── .env / example.env  # Supabase credentials
└── README.md           # Documentation

Data Transformation & Workflow
- Scrape → Collect TechCrunch articles (title, URL, date, full text).
- Detect → Flag articles containing fraud keywords.
- Summarize → Generate concise summaries using summarize_text().
- Deduplicate → Keep only the most recent flagged entry per URL.
- Store → Insert into Supabase (raw_articles, clean_articles, scrape_runs).
- Visualize → Dashboard displays metrics, keywords, and fraud trends.

Example Transformation:
# Keyword detection
keywords = ["fraud", "cybercrime", "phishing"]
flagged = any(word in content.lower() for word in keywords)

# Summarization
summary = summarize_text(content)

# Insert into Supabase
supabase.table("clean_articles").insert({
    "url": url,
    "summary": summary,
    "flagged": flagged
}).execute()

Dashboard Example
- Metrics: Scraped 135 articles, 24 flagged.
- Word Cloud: Highlights dominant fraud terms.
- Bar Chart: Keyword frequencies (Fraud, Cybercrime, Identity Theft, Phishing, Financial Scam).
- Timeline: Flagged articles plotted over time.

Clear Findings & Key Insights
- Top 5 Keywords: Fraud (10), Cybercrime (8), Identity Theft (7), Phishing (6), Financial Scam (5).
- Top 3 Trends:
- AI‑driven phishing attacks
- Identity theft from breaches
- Financial scams in fintech & crypto

 Why This Project is Useful
- Provides real‑time fraud monitoring from public sources.
- Summarizes articles for quick review.
- Ensures data integrity with deduplication.
- Visualizes fraud activity patterns for actionable insights.
- Supabase integration makes the system scalable and reproducible.

 Visual Examples
- Word Cloud of fraud keywords
- Bar chart of keyword frequencies
- Timeline of flagged articles
- GIF demo of dashboard filtering (date range, category dropdowns)

 Current Status
- Scraping, detection, summarization, and Supabase integration fully operational.
- Dashboard metrics and keyword visualizations functioning correctly.
- Deduplication logic implemented for clean data integrity.

 What’s Next
- Add date range filters and category dropdowns in the dashboard.
- Record GIF demos of dashboard interactions.
- Implement timelines for fraud activity trends.
- Expand scraping sources beyond TechCrunch.
- Enhance summarization with advanced NLP models.

 Acknowledgment
Developed for USAA Fraud Research Project
Demonstrates applied data science using NLP, Supabase integration, and visual analytics for fraud trend monitoring.


