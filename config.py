import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

KEYWORDS = [
    "fraud", "scam", "phishing", "cybercrime", "hacking", "data breach",
    "identity theft", "malware", "ransomware", "social engineering",
    "money laundering", "credit card fraud", "sms spam", "phishing page",
    "fake website", "stolen data", "cryptocurrency scam", "cyber attack",
    "unauthorized access", "supply chain attack", "botnet", "AI scam",
    "encrypted messaging", "deep web", "dark web"
]