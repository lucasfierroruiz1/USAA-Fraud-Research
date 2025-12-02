# USAA Fraud Research Dashboard 🔍
**Scrape → Detect → Summarize → Visualize**  
*Author: Elver, Lucas, Precious, Zack*

---

## Project Summary (What and Why)
An ETL pipeline that scrapes TechCrunch articles, detects fraud-related content, summarizes flagged entries, and visualizes trends.

This project automates collection, detection and summarization of fraud-relevant articles from TechCrunch. It stores data in Supabase, uses keyword-based detection and lightweight NLP summarization, and exposes an interactive Streamlit dashboard for analysis.

---

## ⚙️ ETL Pipeline

| Stage       | Description | Tools Used |
|-------------|-------------|------------|
| **Extract** | Scrapes TechCrunch listing pages (title, URL, extracted publication date) and article pages (full text). | `requests`, `beautifulsoup4` |
| **Transform** | Detects fraud keywords, generates summaries, and deduplicates flagged articles. | `pandas`, custom `summarize_text` |
| **Load**    | Uploads structured data into **Supabase** (`raw_articles`, `clean_articles`, `scrape_runs`). | `supabase-py` |

---

## 🧩 System Architecture

| Modality | Description | Example |
|----------|-------------|---------|
| **Textual (unstructured)** | Raw article HTML / body text scraped from TechCrunch. | Full article body |
| **Structured/tabular** | Metadata such as `url`, `pub_date`, `flagged`, `keywords`, `score`. | Supabase tables |
| **Summarized (NLP)** | Condensed article summaries highlighting fraud relevance. | `summarize_text()` output |
| **Visual** | Streamlit charts showing keyword networks, score distribution, trends, and categories. | Network, Histogram, Line + Bars, Pie |

### Repository Structure
```
USAA-Fraud-Research/
├── collector.py            # Scraper + insertion logic
├── streamlit_app.py        # Streamlit dashboard (Flagged Articles + Visuals)
├── supabase_client.py      # Supabase client wrapper
├── config.py               # Loads .env and configuration
├── models.py               # ML / keyword-model helpers
├── utils.py                # summarize_text, keyword helpers
├── requirements.txt
├── README.md
└── .env.example
```

---

## Key Features
- Automated TechCrunch scraping
- Supabase integration for centralized storage
- Keyword-based fraud detection and lightweight summarization
- Deduplication to prevent duplicate clean articles
- Streamlit dashboard with multiple visuals (network, histogram, trend, categories)

---

## Tech Stack
- **Python 3.x** (tested on 3.10/3.11)
- **Streamlit** – interactive dashboard
- **Supabase** – Postgres-backed storage & API
- **Pandas**, **Plotly**, **NetworkX** – analytics & visualizations
- **BeautifulSoup4**, **Requests** – scraping
- **Custom NLP utilities** – summarization & keyword extraction

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/lucasfierroruiz1/USAA-Fraud-Research.git
cd USAA-Fraud-Research
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Provide Supabase credentials
Create a file named `.env` in the project root with the following variables (DO NOT commit `.env`):
```env
SUPABASE_URL="https://<your-project>.supabase.co"
SUPABASE_KEY="<your-supabase-key>"
```

To avoid accidental commits, add `.env` to `.gitignore` and create `.env.example` with placeholders:
```bash
echo ".env" >> .gitignore
cp .env .env.example
# Edit .env.example to remove real values before committing
```

### 5. Run the Streamlit app
```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

### 6. Scraper usage
`collector.py` supports a `--pages` argument to control how many TechCrunch listing pages to fetch:
```bash
python collector.py --pages 100
```

**Notes:**
- The scraper inserts `raw_articles` and `clean_articles`. If a URL already exists, duplicates are skipped.
- The pipeline records each run in `scrape_runs` with `scraped_count` and `flagged_count`.

---

## Visuals (Current)
- **📰 Flagged Articles**: Filterable list by keyword, score, and date.
- **📊 Visuals** (sub-tabs):
  - *Keywords Network*: keyword co-occurrence graph (NetworkX + Plotly)
  - *Score Distribution*: histogram of article scores (Plotly)
  - *Threat Trend*: daily counts (bars) + cumulative (line) based on publication date
  - *Threat Categories*: pie chart of mapped categories (Plotly)

---

## Security & Git Hygiene
- Never commit `.env` or your virtual environment. Add them to `.gitignore`.
- If you ever commit secrets, rotate them immediately (Supabase keys, tokens, etc.) and consider rewriting history (BFG or `git filter-repo`) before pushing.
- Use a limited API key rather than a full service key in `.env` where possible.

---

## Current Status
- Local pipeline: scraping, detection, summarization, and Streamlit dashboard run locally.
- Recent scrape runs are recorded in `scrape_runs`. Inserted rows are deduplicated by URL.
- GitHub remote pushes may require repo cleanup if large files were committed previously.

---

## Acknowledgement
Developed for USAA Fraud Research Project — a practical demonstration of applied data science using NLP, Supabase, and interactive visual analytics for fraud monitoring.




