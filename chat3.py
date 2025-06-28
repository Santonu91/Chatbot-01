import streamlit as st
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Setup
#genai.configure(api_key="YOUR_GEMINI_API_KEY")
genai.configure()
model = genai.GenerativeModel("gemini-2.5-flash")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

st.title("📚 Smart Document Chatbot (Gemini + FAISS)")

# Session state to keep index and data
if 'index' not in st.session_state:
    st.session_state.index = None
    st.session_state.text_data = None

uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

if uploaded_file is not None:
    # Load and split text
    text = uploaded_file.read().decode("utf-8")
    chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
    st.session_state.text_data = chunks

    # Embed and build FAISS index
    embeddings = embedder.encode(chunks)
    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    st.session_state.index = index

    st.success("✅ Document processed and indexed!")

# Chat interface
query = st.text_input("Ask a question about the uploaded document:")

if query and st.session_state.index is not None:
    query_embedding = embedder.encode([query])[0]
    D, I = st.session_state.index.search(np.array([query_embedding]), k=3)
    retrieved_chunks = [st.session_state.text_data[i] for i in I[0]]

    context = "\n".join(retrieved_chunks)
    prompt = f"""
You are a helpful assistant. Here is a document:

{context}

Now answer this question: {query}
"""
    response = model.generate_content(prompt)
    st.markdown("### 🧠 Answer:")
    st.write(response.text)
