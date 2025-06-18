import json
import numpy as np
import faiss
import requests

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
AI_PIPE_URL = "https://aipipe.org/openai/v1/embeddings"
AI_PIPE_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDA0NDdAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.nQKxWWkUC1t0dVKxGuWwzlx-0xZodMpDG1rcUfN_jUQ"  # Replace this with your actual API key
AI_PIPE_EMBEDDING_MODEL = "text-embedding-3-small"

INPUT_FILE = "tds_kb_full_threads.json"
OUTPUT_INDEX = "tds_kb.index"
OUTPUT_META = "tds_kb_meta.json"

# Load threads with full discussions
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    threads = json.load(f)

texts, metadata = [], []

for thread in threads:
    title = thread.get("title", "")
    url = thread.get("url", "")
    posts = thread.get("posts", [])

    # Combine entire thread
    full_text = ""
    for post in posts:
        author = post.get("username", "user")
        created_at = post.get("created_at", "")
        content = post.get("content", "").strip()
        full_text += f"{author} ({created_at}):\n{content}\n\n"

    # Split into overlapping chunks
    for i in range(0, len(full_text), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = full_text[i:i + CHUNK_SIZE]
        texts.append(chunk)
        metadata.append({"title": title, "url": url})

print(f"📄 Total chunks to embed: {len(texts)}")

# Request embeddings from AI Pipe
headers = {
    "Authorization": f"Bearer {AI_PIPE_API_KEY}",
    "Content-Type": "application/json"
}

payload = {"input": texts,
           "model": AI_PIPE_EMBEDDING_MODEL}  # Specify the model if needed

print("📡 Sending request to AI Pipe...")
response = requests.post(AI_PIPE_URL, headers=headers, json=payload)

if response.status_code != 200:
    raise Exception(f"Failed to get embeddings: {response.status_code} {response.text}")

response_json = response.json()
embeddings = response_json.get("data", [])
embeddings = [e["embedding"] for e in embeddings]

# Create FAISS index
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))

# Save index and metadata
faiss.write_index(index, OUTPUT_INDEX)
with open(OUTPUT_META, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Saved {len(embeddings)} embeddings to {OUTPUT_INDEX}")
print(f"✅ Metadata saved to {OUTPUT_META}")
