import streamlit as st
from supabase_client import supabase
import pandas as pd

st.set_page_config(page_title="Cybercrime Monitor", layout="wide")
st.title("🕵️ Cybercrime Article Monitor")

# Fetch flagged articles from Supabase
def fetch_flagged_articles():
    response = supabase.table("clean_articles").select("*").eq("flagged", True).execute()
    return response.data

# Fetch raw article metadata (title + URL) by raw_id
@st.cache_data
def fetch_raw_article(raw_id):
    response = supabase.table("raw_articles").select("title, url").eq("id", raw_id).limit(1).execute()
    return response.data[0] if response.data else {"title": "Unknown", "url": "#"}

# Load and filter articles
articles = fetch_flagged_articles()
if not articles:
    st.info("No flagged articles found.")
else:
    df = pd.DataFrame(articles)

    # Add URL column from raw_articles
    df["url"] = df["raw_id"].apply(lambda rid: fetch_raw_article(rid)["url"])
    df = df[df["keywords"].str.strip() != ""]  # Filter out articles with no keywords
    # Sort and drop duplicates by URL
    df = df.sort_values("created_at", ascending=False)
    df = df.drop_duplicates(subset="url")

    # Add keyword count
    df["keyword_count"] = df["keywords"].apply(lambda x: len(x.split(", ")) if x and x.strip() else 0)

    # Sort by keyword count descending
    df_sorted = df.sort_values(by="keyword_count", ascending=False)

    # Optional keyword filter
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