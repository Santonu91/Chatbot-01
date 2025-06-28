import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
#from google import genai

# ---- 1. Load and Split the Story ----
with open("doc1.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

# Simple split (by paragraph)
chunks = [p.strip() for p in full_text.split("\n\n") if p.strip()]

# ---- 2. Embed Each Chunk ----
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chunk_embeddings = embedder.encode(chunks)

# ---- 3. Store in FAISS ----
dimension = chunk_embeddings[0].shape[0]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(chunk_embeddings))
text_data = chunks  # Store original chunks for retrieval

# ---- 4. Configure Gemini API ----
#genai.configure(api_key="AIzaSyB7H-NQD22rQHM1-IL6RgX4Ehu8-n1Kvy8")
genai.configure()
model = genai.GenerativeModel("gemini-2.5-flash")

# ---- 5. Ask Questions ----
def ask_story_question(query):
    query_embedding = embedder.encode([query])[0]
    _, I = index.search(np.array([query_embedding]), k=3)
    relevant_chunks = [text_data[i] for i in I[0]]

    context = "\n".join(relevant_chunks)
    prompt = f"""You are an AI assistant.
    
Here is an excerpt from a story:

{context}

Now answer this question about the story:
{query}
"""

    response = model.generate_content(prompt)
    print("\n🧠 Answer:", response.text)

# ---- 6. Run Interaction Loop ----
while True:
    q = input("\n❓ Ask about the story (or 'exit'): ")
    if q.lower() == 'exit':
        break
    ask_story_question(q)
