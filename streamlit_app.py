import streamlit as st
from supabase_client import supabase

st.set_page_config(page_title="Cybercrime Monitor", layout="wide")
st.title("🕵️ Cybercrime Article Monitor")

# Fetch flagged articles from Supabase
def fetch_flagged_articles():
    response = supabase.table("clean_articles").select("*").eq("flagged", True).order("created_at", desc=True).execute()
    return response.data

# Fetch raw article metadata (title + URL) by raw_id
def fetch_raw_article(raw_id):
    response = supabase.table("raw_articles").select("title, url").eq("id", raw_id).limit(1).execute()
    return response.data[0] if response.data else {"title": "Unknown", "url": "#"}

# Load and filter articles
articles = fetch_flagged_articles()
keyword_filter = st.text_input("🔍 Filter by keyword (optional)").strip().lower()

if not articles:
    st.info("No flagged articles found.")
else:
    for article in articles:
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
        st.markdown(f"[🔗 Read full article]({raw['url']})")
        st.markdown("---")