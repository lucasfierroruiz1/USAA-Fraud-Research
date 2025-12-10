# USAA Fraud Research Dashboard 🔍
**Scrape → Detect → Summarize → Visualize**  
*Author: Elver, Lucas, Precious, Zack*

---

## Project Summary (What and Why)
An automated ETL pipeline that collects TechCrunch articles, detects fraud related content, generates summaries and visualizes trends.

The system scrapes TechCrunch, extracts text, identifies fraud indicators using keyword scoring, and stores the results in Supabase. It produces clean summaries and exposes an interactive Streamlit dashboard that helps analysts review fraud topics faster and with more structure.

---

## ⚙️ ETL Pipeline

| Stage       | Description | Tools Used |
|-------------|-------------|------------|
| **Extract** | Scrapes listing pages, captures titles, URLs, authors, and publication dates. Scrapes article pages for full text. | `requests`, `beautifulsoup4` |
| **Transform** | Runs keyword detection, assigns a fraud score, creates summaries, removes duplicates and categorizes article content. | `pandas`, `sentence-transformers`, custom NLP functions |
| **Load**    | Uploads structured results into Supabase tables (`raw_articles`, `clean_articles`, `scrape_runs`). | `supabase-py` |

---

## 🧩 System Architecture

| Modality | Description | Example |
|----------|-------------|---------|
| **Textual (unstructured)** | Full article text from TechCrunch. | Scraped HTML content |
| **Structured/tabular** | Metadata and fraud indicators, including `keywords`, `score`, `flagged`, and publication date. | Supabase tables |
| **Summarized (NLP)** | Short summaries highlighting the fraud relevance of each flagged article. | Output of `summarize_text()` |
| **Visual** | Dashboard views including networks, trends and score distributions. | Streamlit + Plotly visualizations |

### Repository Structure
```
USAA-Fraud-Research/
├── collector.py            # Scrapes TechCrunch and loads to Supabase
├── streamlit_app.py        # Streamlit UI with Flagged Articles + Visuals
├── supabase_client.py      # Supabase API wrapper
├── config.py               # Loads environment variables
├── models.py               # Keyword model, scoring logic, categorization
├── utils.py                # Summary function, helpers, text cleaning
├── requirements.txt        # Dependencies
├── README.md
└── .env.example
```

---

## Key Features
- Automated TechCrunch scraping  
- Fraud keyword scoring and detection  
- Concise summaries for fast review  
- Categorization of fraud types based on matched terms  
- Deduplication logic to avoid repeated entries  
- Streamlit dashboard with multiple visual layers  
- Supabase storage for runs, raw articles and cleaned articles  

---

## Tech Stack
Dependencies in `requirements.txt` confirm the following environment setup.

- **Python 3.x**  
- **Streamlit** for dashboard  
- **Supabase** for data storage  
- **Pandas, NumPy** for data processing  
- **Plotly, Altair, Matplotlib, Seaborn** for visuals  
- **NetworkX** for keyword network graphs  
- **BeautifulSoup4, Requests** for scraping  
- **Sentence Transformers** for improved summarization  
- **WordCloud** for optional text visualization  

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
Create a `.env` file with:
```env
SUPABASE_URL="https://<your-project>.supabase.co"
SUPABASE_KEY="<your-supabase-key>"
```

Add `.env` to `.gitignore` for safety.  
Use `.env.example` as a template for collaborators.

### 5. Run the Streamlit dashboard
```bash
streamlit run streamlit_app.py
```

### 6. Run the scraper
```bash
python collector.py --pages 50
```

Options include:  
- `--pages N` to control how many listing pages to scrape  
- Automatic insertion into Supabase  
- Tracking of runs in `scrape_runs`  

Duplicates are skipped based on URL.

---

## Visuals (Current)

### 📰 Flagged Articles
Filtered by keyword, score, date or category.  
Shows summary, keywords, score and a direct link to the article.

### 📊 Visuals
- **Keyword Network**: Graph showing relationships among fraud terms  
- **Score Distribution**: Histogram showing how many articles fall into each fraud score range  
- **Threat Trend**: Daily article counts with cumulative line  
- **Threat Categories**: Pie chart showing distribution across fraud types  

These views help analysts scan activity patterns quickly.

---

## Security & Git Hygiene
- Do not commit `.env`  
- Rotate keys if exposed  
- Avoid committing large files or virtual environments  
- Use `.gitignore` to keep repo clean  

---

## Current Status
- End to end pipeline working locally  
- Supabase tables updated with each run  
- Dashboard visualizations stable  
- Codebase supports future expansion such as more sources or ML classification  

---

## Acknowledgement
Developed for the USAA Fraud Research Project as an applied demonstration of applied data science, automation and interactive analytics.


