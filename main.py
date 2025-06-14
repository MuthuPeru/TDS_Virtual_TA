from fastapi import FastAPI, Request
from pydantic import BaseModel
import json
import faiss
import numpy as np
import requests

# Load FAISS index and metadata
index = faiss.read_index("tds_kb.index")
with open("tds_kb_meta.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# AI Pipe API details
AI_PIPE_EMBEDDING_ENDPOINT = "https://aipipe.org/openrouter/v1/embeddings"
AI_PIPE_CHAT_ENDPOINT = "https://aipipe.org/openrouter/v1/chat"
#AI_PIPE_API_KEY = "your-aipipe-api-key"  # Replace with your actual key
AI_PIPE_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDA0NDdAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.nQKxWWkUC1t0dVKxGuWwzlx-0xZodMpDG1rcUfN_jUQ"


app = FastAPI()

class Query(BaseModel):
    question: str

def get_embedding_from_aipipe(text: str):
    headers = {
        "Authorization": f"Bearer {AI_PIPE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "input": [text]
    }
    response = requests.post(AI_PIPE_EMBEDDING_ENDPOINT, json=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Embedding error: {response.status_code} {response.text}")
    return response.json()["data"][0]["embedding"]

def retrieve_top_k_chunks(query_vector, k=5):
    D, I = index.search(np.array([query_vector]).astype("float32"), k)
    return [metadata[i] for i in I[0]]

def call_aipipe_chat(question: str, context: str):
    headers = {
        "Authorization": f"Bearer {AI_PIPE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful teaching assistant."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    }
    response = requests.post(AI_PIPE_CHAT_ENDPOINT, json=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Chat error: {response.status_code} {response.text}")
    return response.json()["choices"][0]["message"]["content"]

@app.post("/ask")
async def ask(query: Query):
    question = query.question
    query_embedding = get_embedding_from_aipipe(question)
    top_chunks = retrieve_top_k_chunks(query_embedding)
    context_text = "\n---\n".join([chunk["title"] + ": " + chunk.get("url", "") for chunk in top_chunks])
    answer = call_aipipe_chat(question, context_text)
    return {"answer": answer, "sources": top_chunks}
