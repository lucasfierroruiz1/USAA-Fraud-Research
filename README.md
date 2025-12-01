# USAA Fraud Research Dashboard 🔍  
**Scrape → Detect → Summarize → Visualize**  
*Author: Elver, Lucas, Precious, Zack

---

## Project Summary( WHat and WHy)
A pipeline that scrapes TechCrunch articles, detects fraud related content, summarizes flagged entries and visualizes trends.

The project automates the collection, detection, and summarization of **fraud-related articles** from TechCrunch.  
It integrates **Supabase** for storage, keyword-based detection for fraud relevance, and **Streamlit** for visualization.  
The goal is to identify fraud themes, track emerging risks, and provide concise summaries for rapid analysis.  

---

## ⚙️ ETL Pipeline

| Stage       | Description | Tools Used |
|-------------|-------------|------------|
| **Extract** | Scrapes TechCrunch articles (title, URL, date, full text). | `requests`, `BeautifulSoup4` |
| **Transform** | Detects fraud keywords, generates summaries, deduplicates flagged articles. | `pandas`, `re`, custom `summarize_text` |
| **Load**    | Uploads structured data into **Supabase**, storing raw and clean articles with metadata. | `supabase-py` |

### 📊 ETL Workflow

---

## 🧩 System Architecture

| Modality | Description | Example |
|----------|-------------|---------|
| **Textual (unstructured)** | Raw article text scraped from TechCrunch. | Full article body |
| **Structured/tabular** | Metadata such as `date`, `url`, `flagged`, `keywords`. | Supabase tables |
| **Summarized (NLP)** | Condensed article summaries highlighting fraud relevance. | `summarize_text()` output |
| **Visual** | Streamlit-based charts showing keyword frequencies and flagged counts. | Word Cloud, Bar Charts |
USAA-Fraud-Research/
├── collector.py
├── streamlit_app.py
├── utils.py
├── requirements.txt
└── .env / example.env



---

## Key Features
✅ Automated TechCrunch scraping  
✅ Supabase integration for centralized storage  
✅ Keyword-based fraud detection  
✅ Summarization of flagged articles  
✅ Deduplication to prevent duplicate entries  
✅ Streamlit dashboard with metrics and visualizations  

---

## Tech Stack
- **Python 3.12**  
- **Streamlit** – interactive dashboard interface  
- **Supabase** – data storage and querying  
- **Pandas**, **Matplotlib**, **Seaborn** – analytics and visualization  
- **BeautifulSoup4**, **Requests** – data scraping  
- **Custom NLP utilities** – keyword detection + summarization  

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/lucasfierroruiz1/USAA-Fraud-Research.git
cd USAA-Fraud-Research

uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key

uv run streamlit run streamlit_app.py

Top 5 Keywords- Fraud(10), Cybercrime(8), Identity Theft(6), Phising(6), Financial Scam(5)

Top 3 Fraud Trends
- AI-driven phishing attacks
- Identity theft from data breaches
- Financial scams in fintech & crypto

Demo-
<img width="942" height="848" alt="Screenshot 2025-11-30 231457" src="https://github.com/user-attachments/assets/831e5215-edc4-494a-94a2-2a33dad8a56f" />

(Above is a screenshot of the Streamlit Dashboarrd showing our metrics and keyword visualization)


Current Status
✅ Scraping, detection, summarization, and Supabase integration are fully operational
✅ Dashboard metrics and keyword visualizations functioning correctly
✅ Deduplication logic implemented for clean data integrity

Acknowledgement
Developed for USAA Fraud Research Project
Demonstrates applied data science using NLP, Supabase integration, and visual analytics for fraud trend monitoring.




