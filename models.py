from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def train_keyword_model(keywords):
    # Fraud examples
    X_fraud = keywords
    y_fraud = [1] * len(keywords)

    # Non-fraud examples (clean tech terms)
    X_clean = [
        "startup", "funding", "AI innovation", "cloud computing", "venture capital",
        "product launch", "developer tools", "open source", "tech trends", "user experience"
    ]
    y_clean = [0] * len(X_clean)

    # Combine both
    X = X_fraud + X_clean
    y = y_fraud + y_clean

    vectorizer = TfidfVectorizer()
    X_tfidf = vectorizer.fit_transform(X)
    model = LogisticRegression()
    model.fit(X_tfidf, y)

    return vectorizer, model