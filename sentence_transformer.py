import streamlit as st
from sentence_transformers import SentenceTransformer

st.title("🚀 Model Load Test")

try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    st.success("Model loaded successfully!")
except Exception as e:
    st.error(f"Failed to load model: {e}")
