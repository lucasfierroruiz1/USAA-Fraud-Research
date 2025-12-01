import re

def summarize_text(text, max_sentences=3):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return ' '.join(sentences[:max_sentences])

def extract_keywords(text, keywords):
    return [kw for kw in keywords if kw in text.lower()]