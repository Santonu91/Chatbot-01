from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import uvicorn

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
genai.configure()
model = genai.GenerativeModel("gemini-2.5-flash")

# ---- 5. Define FastAPI App ----
app = FastAPI(
    title="Story Question Answering API",
    description="Ask questions about a story and get AI-generated answers using Gemini and FAISS.",
    version="1.0.0"
)

# ---- Serve static files from 'static' folder ----
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# ---- 6. Pydantic model for request ----
class QuestionRequest(BaseModel):
    query: str

# ---- 7. Endpoint to answer questions ----
@app.post("/ask", summary="Ask a question about the story")
def ask_story_question(request: QuestionRequest):
    query = request.query
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
    return {"answer": response.text.strip()}

# ---- 8. Run the app ----
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
