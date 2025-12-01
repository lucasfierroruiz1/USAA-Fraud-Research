Project Overview
The Cybercrime Article Monitor is a Python-based system designed to scrape, identify, and summarize news articles related to fraud, scams, and broader cybercrime activity. The goal is to automate the monitoring of major news sources and extract content relevant to fraud detection. The system supports the creation of intelligence updates for fraud teams, including short weekly briefs and material that can inform USAA’s State of Fraud quarterly publication.

The project uses web scraping, keyword detection, and a machine learning classification model to filter security-related articles. It summarizes flagged articles, stores them in a Supabase database, and displays results inside an interactive Streamlit dashboard. This allows users to quickly identify trends in malware attacks, data breaches, fraud schemes, and emerging cyber threats.

Main Features
Automated scraping of technology news articles.
Keyword detection to identify fraud and cybercrime content.
Lightweight machine learning model for additional classification.
Summary generation for flagged articles.
Supabase storage for both raw and cleaned article data.
Duplicate handling and run logging.
Streamlit dashboard for visualization and review.

System Workflow
Scrape news pages from the selected source.
Extract article titles, URLs, dates, and full text.
Scan content for fraud and cybercrime keywords.
Classify articles as relevant or irrelevant using a simple model.
Generate a short summary for all flagged articles.
Insert article data into Supabase tables.
Render analytics and summaries in the Streamlit dashboard.

How to Set Up

1. Clone the project repository.
2. Create a virtual environment and install dependencies.
3. Add a .env file with your Supabase credentials.
4. Ensure the database schema includes raw_articles, clean_articles, and scrape_runs.
5. Verify that the required Python files are in place.

How to Run the Scraper

1. Activate your virtual environment.
2. Run collector.py from the terminal.
3. The script will scrape articles, process them, store results, and record run statistics.

How to Run the Dashboard

1. Activate your virtual environment.
2. Run the command: streamlit run streamlit_app.py
3. The dashboard will open in your browser.
4. Use the interface to view metrics, keyword clouds, top keywords, and flagged articles.

Understanding the Dashboard Output
The dashboard shows the number of articles scraped in the most recent run and the number flagged as cybercrime related. It displays a word cloud of common keywords and a frequency chart highlighting the most frequent indicators of fraud and hacking. Flagged articles appear with summaries, relevance scores, extracted keywords, and a link to view the full article.

Summary of Project Findings
The system effectively filters high risk articles from large volumes of news reporting. In one representative run, 135 articles were scraped and 24 were flagged for cybercrime relevance. The flagged content covered university data breaches, government intrusions, insider fraud, malware distribution, and large scale scams. These results reflect real cybercrime patterns and validate the system’s detection framework.

The distribution of keywords such as hacking, malware, fraud, scam, and data breach confirms strong alignment between keyword detection and actual threat activity. Articles reveal diverse threat categories, including zero day exploits, botnets, location data misuse, and identity theft. The system captures both technical intrusion events and broader forms of cybercrime involving data monetization and deceptive advertising.

Theoretical and Practical Relevance
The project aligns with routine activity theory, signaling theory, and criminological pattern analysis. It also demonstrates the value of open source intelligence for early detection. The findings have clear implications for security teams, including the need for stronger access controls, better monitoring of insider risk, and greater coordination across sectors.

Future improvements may include support for multiple news sources, expanded classification models, and automated alerting.
