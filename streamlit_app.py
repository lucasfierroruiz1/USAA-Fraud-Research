import streamlit as st
from supabase_client import supabase
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import altair as alt
import datetime
import numpy as np

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
    tab1, tab2 = st.tabs(["📰 Flagged Articles", "📊 Interactive Chart"])

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
        # Provide choice between keywords and articles-by-date
        chart_choice = st.selectbox("Chart by:", options=["Keywords", "Articles by Date"], key="chart_choice")

        # --- Chart-specific filters: date range and min score ---
        # safe min/max for created_at
        if df["created_at"].notna().any():
            min_chart_date = df["created_at"].min().date()
            max_chart_date = df["created_at"].max().date()
        else:
            min_chart_date = datetime.date.today()
            max_chart_date = datetime.date.today()

        date_range_chart = st.date_input("Chart timeline", value=(min_chart_date, max_chart_date), key="chart_timeline")
        if isinstance(date_range_chart, (list, tuple)):
            chart_start, chart_end = date_range_chart[0], date_range_chart[1]
        else:
            chart_start = chart_end = date_range_chart

        # score filter for charts
        if "score" in df.columns and not df["score"].isna().all():
            smin = float(df["score"].min())
            smax = float(df["score"].max())
        else:
            smin, smax = 0.0, 1.0
        score_min_chart = st.slider("Min score (chart)", min_value=smin, max_value=smax, value=smin, step=0.1, key="chart_score")

        # Build filtered flagged dataframe for use by both charts
        filtered_flagged_df = df[df["flagged"] == True].copy()
        if not filtered_flagged_df.empty:
            filtered_flagged_df = filtered_flagged_df[filtered_flagged_df["created_at"].notna()]
            filtered_flagged_df = filtered_flagged_df[(filtered_flagged_df["created_at"].dt.date >= chart_start) & (filtered_flagged_df["created_at"].dt.date <= chart_end)]
            if "score" in filtered_flagged_df.columns:
                filtered_flagged_df = filtered_flagged_df[filtered_flagged_df["score"].fillna(0) >= score_min_chart]

        if chart_choice == "Keywords":
            # use filtered flagged dataframe for keywords
            if filtered_flagged_df.empty:
                st.info("No flagged articles match the chart filters.")
            else:
                flagged_keywords = filtered_flagged_df["keywords"].dropna()
                keywords_expanded = [kw.strip() for kws in flagged_keywords for kw in kws.split(",") if kw.strip()]
                if not keywords_expanded:
                    st.info("No flagged keywords available for interactive chart.")
                else:
                    kw_df = pd.DataFrame(keywords_expanded, columns=["Keyword"])
                    kw_counts = kw_df["Keyword"].value_counts().reset_index()
                    kw_counts.columns = ["Keyword", "Frequency"]
                    top_n = st.slider("Top N keywords", min_value=3, max_value=min(50, len(kw_counts)), value=min(10, len(kw_counts)), key="top_n_keywords")
                    top_counts = kw_counts.head(top_n)
                    # Vertical bar chart (Keywords on X, Frequency on Y) — full width
                    st.markdown("#### Top Keywords")
                    chart = (
                        alt.Chart(top_counts)
                        .mark_bar()
                        .encode(
                            x=alt.X("Keyword:N", sort=top_counts["Keyword"].tolist(), title="Keyword"),
                            y=alt.Y("Frequency:Q", title="Frequency"),
                            color=alt.Color("Keyword:N", legend=None),
                            tooltip=["Keyword", "Frequency"]
                        ).properties(height=420)
                    )
                    st.altair_chart(chart.interactive(), use_container_width=True)
                    st.dataframe(top_counts)
        else:
            # Articles by date
            df_dates = df.copy()
            df_dates["created_at"] = pd.to_datetime(df_dates["created_at"]).dt.date
            date_counts = df_dates.groupby("created_at").size().reset_index(name="Count")
            if not date_counts.empty:
                date_counts = date_counts.sort_values("created_at")
                brush = alt.selection(type='interval', encodings=['x'])
                base = alt.Chart(date_counts).mark_bar().encode(
                    x=alt.X('created_at:T', title='Date'),
                    y=alt.Y('Count:Q', title='Articles'),
                    tooltip=[alt.Tooltip('created_at:T', title='Date'), 'Count']
                ).add_selection(brush)

                st.altair_chart(base.interactive(), use_container_width=True)
                st.dataframe(date_counts)