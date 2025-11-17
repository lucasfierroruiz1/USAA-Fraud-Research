import streamlit as st
from supabase_client import supabase
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter

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

    # 📊 Dashboard Visualizations
    st.subheader("📊 Dashboard Visualizations")
    tab1, tab3 = st.tabs(["Word Cloud", "Top Keywords"])

    # Word Cloud
    with tab1:
        flagged_keywords = df[df["flagged"] == True]["keywords"].dropna()
        all_keywords = ", ".join(flagged_keywords)
        if all_keywords.strip():
            wordcloud = WordCloud(width=600, height=300, background_color="white").generate(all_keywords)
            fig_wc, ax_wc = plt.subplots(figsize=(8, 3))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)
        else:
            st.info("No flagged keywords available for word cloud.")

    # Top 10 Flagged Keywords (fixed palette warning)
    with tab3:
        flagged_keywords = df[df["flagged"] == True]["keywords"].dropna()
        keywords_list = [kw.strip() for kws in flagged_keywords for kw in kws.split(",") if kw.strip()]
        if keywords_list:
            top_keywords = Counter(keywords_list).most_common(10)
            top_df = pd.DataFrame(top_keywords, columns=["Keyword", "Frequency"])
            fig_bar2, ax2 = plt.subplots(figsize=(6, 4))
            sns.barplot(
                data=top_df,
                x="Frequency",
                y="Keyword",
                hue="Keyword",      # fix warning
                palette="viridis",
                legend=False,
                ax=ax2
            )
            ax2.set_title("Top 10 Flagged Keywords")
            st.pyplot(fig_bar2)
        else:
            st.info("No flagged keywords available for top keywords chart.")

    # --- Article rendering below ---
    st.subheader("📰 Flagged Articles")
    keyword_filter = st.text_input("🔍 Filter by keyword (optional)").strip().lower()

    for _, article in df_sorted.iterrows():
        if keyword_filter and keyword_filter not in article["keywords"].lower():
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