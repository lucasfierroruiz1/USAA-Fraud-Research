import os
import streamlit as st
from supabase import create_client, Client

if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
else:
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
raise RuntimeError("Supabase credentials are not configured")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
