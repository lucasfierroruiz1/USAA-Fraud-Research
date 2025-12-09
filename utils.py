import re

# --- Existing functions ---
def summarize_text(text, max_sentences=3):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return ' '.join(sentences[:max_sentences])

def extract_keywords(text, keywords):
    return [kw for kw in keywords if kw in text.lower()]

# --- New embedding function ---
from sentence_transformers import SentenceTransformer

# Load model once at import time
_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    """
    Generate an embedding vector for the given text.
    Returns a Python list (so it can be stored in Supabase as JSON).
    """
    return _embedding_model.encode(text).tolist()