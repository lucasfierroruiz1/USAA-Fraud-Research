import streamlit as st
from supabase_client import supabase
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import altair as alt
import datetime
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from itertools import combinations

st.set_page_config(page_title="Cybercrime Monitor", layout="wide")
st.title("🕵️ Cybercrime Article Monitor")

def fetch_articles():
    response = supabase.table("clean_articles").select("*").execute()
    return response.data

@st.cache_data
def fetch_raw_article(raw_id):
    response = supabase.table("raw_articles").select("title, url").eq("id", raw_id).limit(1).execute()
    return response.data[0] if response.data else {"title": "Unknown", "url": "#"}

articles = fetch_articles()
if not articles:
    st.info("No articles found.")
else:
    df = pd.DataFrame(articles)
    # Normalize created_at early so all tabs/charts get datetime objects
    df["created_at"] = pd.to_datetime(df.get("created_at", None), errors='coerce')
    df["url"] = df["raw_id"].apply(lambda rid: fetch_raw_article(rid)["url"])
    df = df[df["keywords"].str.strip() != ""]
    df = df.sort_values("created_at", ascending=False).drop_duplicates(subset="url")
    df["keyword_count"] = df["keywords"].apply(lambda x: len(x.split(", ")) if x and x.strip() else 0)
    df_sorted = df.sort_values(by="keyword_count", ascending=False)

    # 📊 Metrics: Scraped from latest run, Flagged from displayed data
    st.subheader("📊 Metrics")
    col1, col2 = st.columns(2)

    # Scraped (this run) from scrape_runs
    latest_run = supabase.table("scrape_runs").select("*").order("created_at", desc=True).limit(1).execute()
    scraped_this_run = latest_run.data[0]["scraped_count"] if latest_run.data else 0

    # Flagged (displayed cumulative) from df
    flagged_displayed = int(df["flagged"].sum())

    col1.metric("Articles Scraped (this run)", scraped_this_run)
    col2.metric("Articles Flagged (displayed)", flagged_displayed)

    # Create two tabs
    tab1, tab2 = st.tabs(["📰 Flagged Articles", "📊 Visuals"])

    with tab1:
        st.markdown("### 📰 Flagged Articles")
        
        # 🔍 Filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            keyword_filter = st.text_input("🔍 Filter by keyword (optional)").strip().lower()
        
        with col_filter2:
            min_score = st.slider("Min Score", min_value=0.0, max_value=float(df["score"].max()) if len(df) > 0 else 1.0, value=0.0, step=0.1)
        
        with col_filter3:
            min_date = df["created_at"].min().date()
            max_date = df["created_at"].max().date()

            preset = st.selectbox("Quick range:", options=["All time", "Last 7 days", "Last 30 days", "Last Year", "Custom"], index=0)

            if preset == "All time":
                start_date = min_date
                end_date = max_date
            elif preset == "Last 7 days":
                end_date = max_date
                start_date = end_date - datetime.timedelta(days=7)
            elif preset == "Last 30 days":
                end_date = max_date
                start_date = end_date - datetime.timedelta(days=30)
            elif preset == "Last Year":
                end_date = max_date
                start_date = end_date - datetime.timedelta(days=365)
            else:
                # Custom range picker
                # allow arbitrary custom ranges (not clamped to dataset min/max)
                date_range = st.date_input("Timeline", value=(min_date, max_date))
                if isinstance(date_range, tuple) or isinstance(date_range, list):
                    start_date, end_date = date_range[0], date_range[1]
                else:
                    start_date = end_date = date_range

        for _, article in df_sorted.iterrows():
            # Apply filters
            if keyword_filter and keyword_filter not in article["keywords"].lower():
                continue
            if article["score"] < min_score:
                continue
            article_date = pd.to_datetime(article["created_at"]).date()
            if not (pd.to_datetime(start_date).date() <= article_date <= pd.to_datetime(end_date).date()):
                continue
            
            raw = fetch_raw_article(article["raw_id"])
            st.markdown("### " + raw["title"])
            st.markdown(f"**Summary:** {article['summary']}")
            keywords = article["keywords"] if article["keywords"].strip() else "—"
            if keywords == "—":
                st.warning("⚠️ No keywords detected for this article.")
            st.markdown(f"**Keywords:** `{keywords}`")
            st.markdown(f"**Score:** {article['score']}")
            st.markdown(f"**Keyword Count:** {article['keyword_count']}")
            st.markdown(f"[🔗 Read full article]({raw['url']})")
            st.markdown("---")

    with tab2:
        st.markdown("### 📊 Threat Intelligence Visuals")
        
        # Sub-tabs for different visualizations
        visual_tabs = st.tabs(["Keywords Network", "Score Distribution", "Threat Trend", "Threat Categories"])
        
        # --- 1. KEYWORD NETWORK GRAPH ---
        with visual_tabs[0]:
            st.markdown("#### 🔗 Keyword Co-occurrence Network")
            st.markdown("Shows which keywords appear together in flagged articles (larger nodes = more frequent).")
            
            flagged_df = df[df["flagged"] == True].copy()
            if not flagged_df.empty and len(flagged_df) > 0:
                # Build co-occurrence graph
                all_keywords = []
                for kws in flagged_df["keywords"].dropna():
                    keywords_list = [kw.strip().lower() for kw in kws.split(",") if kw.strip()]
                    all_keywords.append(keywords_list)
                
                # Create network graph
                G = nx.Graph()
                for kw_list in all_keywords:
                    for kw in kw_list:
                        G.add_node(kw)
                    # Add edges for co-occurrence
                    for kw1, kw2 in combinations(kw_list, 2):
                        if G.has_edge(kw1, kw2):
                            G[kw1][kw2]["weight"] += 1
                        else:
                            G.add_edge(kw1, kw2, weight=1)
                
                if len(G.nodes()) > 0:
                    # Filter to top 20 keywords by degree for readability
                    top_keywords = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:20]
                    top_kw_names = [k[0] for k in top_keywords]
                    G_filtered = G.subgraph(top_kw_names)
                    
                    # Plotly network visualization
                    pos = nx.spring_layout(G_filtered, k=0.5, iterations=50, seed=42)
                    
                    edge_x, edge_y = [], []
                    for edge in G_filtered.edges():
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                    
                    edge_trace = go.Scatter(
                        x=edge_x, y=edge_y,
                        mode='lines',
                        line=dict(width=0.5, color='#888'),
                        hoverinfo='none',
                        showlegend=False
                    )
                    
                    node_x, node_y, node_text, node_size = [], [], [], []
                    for node in G_filtered.nodes():
                        x, y = pos[node]
                        node_x.append(x)
                        node_y.append(y)
                        node_text.append(node.title())
                        node_size.append(max(G_filtered.degree(node) * 5, 10))
                    
                    node_trace = go.Scatter(
                        x=node_x, y=node_y,
                        mode='markers+text',
                        text=node_text,
                        textposition='top center',
                        hoverinfo='text',
                        hovertext=node_text,
                        marker=dict(
                            size=node_size,
                            color='#FF6B6B',
                            line_width=2,
                            line_color='white'
                        ),
                        showlegend=False
                    )
                    
                    fig = go.Figure(data=[edge_trace, node_trace])
                    fig.update_layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough keywords to build network graph.")
            else:
                st.info("No flagged articles to visualize.")
        
        # --- 2. SCORE DISTRIBUTION HISTOGRAM ---
        with visual_tabs[1]:
            st.markdown("#### 📊 Score Distribution Histogram")
            st.markdown("Shows the distribution of threat scores for flagged articles.")
            
            flagged_scores = df[df["flagged"] == True]["score"].dropna()
            if len(flagged_scores) > 0:
                fig = px.histogram(
                    x=flagged_scores,
                    nbins=20,
                    labels={"x": "Score", "count": "Count"},
                    title="Distribution of Flagged Article Scores"
                )
                fig.update_traces(marker_color='#FF6B6B')
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No flagged scores to visualize.")
        
        # --- 3. FLAGGED ARTICLES OVER TIME (TREND LINE) ---
        with visual_tabs[2]:
            st.markdown("#### 📈 Flagged Articles Trend Over Time")
            st.markdown("Cumulative flagged articles by publication date with trend line.")
            
            df_timeline = df[df["flagged"] == True].copy()
            if len(df_timeline) > 0:
                # Extract publication date from URL (format: /YYYY/MM/DD/)
                def extract_date_from_url(url):
                    try:
                        if url and 'techcrunch.com' in url:
                            parts = url.split('/')
                            # Look for YYYY/MM/DD pattern in URL
                            for i, part in enumerate(parts):
                                if len(part) == 4 and part.isdigit() and i+2 < len(parts):
                                    year, month, day = parts[i], parts[i+1], parts[i+2]
                                    if year.isdigit() and month.isdigit() and day.isdigit():
                                        try:
                                            return pd.to_datetime(f"{year}-{month}-{day}")
                                        except:
                                            return None
                    except:
                        pass
                    return None
                
                df_timeline["pub_date"] = df_timeline["url"].apply(extract_date_from_url)
                df_timeline = df_timeline[df_timeline["pub_date"].notna()]
                
                if len(df_timeline) > 0:
                    daily_counts = df_timeline.groupby(df_timeline["pub_date"].dt.date).size().reset_index(name="count")
                    daily_counts.columns = ["date", "count"]
                    daily_counts = daily_counts.sort_values("date")
                    daily_counts["cumulative"] = daily_counts["count"].cumsum()
                    
                    # Build a figure with both daily counts and cumulative counts
                    fig = go.Figure()

                    # Daily counts as bars (primary y-axis)
                    fig.add_trace(go.Bar(
                        x=daily_counts["date"],
                        y=daily_counts["count"],
                        name="Daily Count",
                        marker_color="#FFA07A",
                        opacity=0.6,
                    ))

                    # Cumulative counts as a line on secondary y-axis
                    fig.add_trace(go.Scatter(
                        x=daily_counts["date"],
                        y=daily_counts["cumulative"],
                        mode="lines+markers",
                        name="Cumulative",
                        line=dict(color="#FF6B6B", width=3),
                        marker=dict(size=6),
                        yaxis="y2",
                    ))

                    fig.update_layout(
                        title="Flagged Articles Over Time (Daily + Cumulative, by Publication Date)",
                        xaxis=dict(title="Publication Date"),
                        yaxis=dict(title="Daily Count"),
                        yaxis2=dict(title="Cumulative", overlaying="y", side="right"),
                        legend=dict(x=0.01, y=0.99),
                        height=520,
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("**Daily Breakdown:**")
                    st.dataframe(daily_counts.sort_values("date", ascending=False), use_container_width=True)
                else:
                    st.info("Could not extract publication dates from article URLs.")
            else:
                st.info("No flagged articles to visualize.")
        
        # --- 4. TOP THREAT CATEGORIES (SUNBURST) ---
        with visual_tabs[3]:
            st.markdown("#### 🎯 Top Threat Categories")
            st.markdown("Breakdown of threat types based on flagged article keywords.")
            
            flagged_df = df[df["flagged"] == True].copy()
            if len(flagged_df) > 0:
                # Define threat categories
                threat_categories = {
                    "Data Breach": ["data breach", "data leak", "breach", "exposed", "stolen data"],
                    "Phishing": ["phishing", "phishing page", "fake website", "social engineering"],
                    "Malware": ["malware", "ransomware", "botnet", "trojan", "virus"],
                    "Fraud": ["fraud", "scam", "money laundering", "credit card fraud", "fake invoice"],
                    "Account Compromise": ["account takeover", "unauthorized access", "account irregularity"],
                    "Other": []
                }
                
                # Categorize each article
                categories = []
                for _, row in flagged_df.iterrows():
                    keywords = row["keywords"].lower() if row["keywords"] else ""
                    found = False
                    for cat, patterns in threat_categories.items():
                        if cat != "Other" and any(pattern in keywords for pattern in patterns):
                            categories.append(cat)
                            found = True
                            break
                    if not found:
                        categories.append("Other")
                
                cat_counts = Counter(categories)
                cat_df = pd.DataFrame(list(cat_counts.items()), columns=["Category", "Count"])
                cat_df = cat_df.sort_values("Count", ascending=False)
                
                fig = px.pie(
                    cat_df,
                    names="Category",
                    values="Count",
                    title="Threat Categories Distribution",
                    hole=0,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("**Breakdown by Category:**")
                st.dataframe(cat_df.sort_values("Count", ascending=False), use_container_width=True)
            else:
                st.info("No flagged articles to visualize.")