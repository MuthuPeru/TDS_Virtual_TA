import json
import time
import numpy as np
import requests
import faiss

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
AI_PIPE_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDA0NDdAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.nQKxWWkUC1t0dVKxGuWwzlx-0xZodMpDG1rcUfN_jUQ"
AI_PIPE_EMBEDDING_ENDPOINT = "https://aipipe.org/openai/v1/embeddings"  # Replace if different
AI_PIPE_EMBEDDING_MODEL = "text-embedding-3-small"

INPUT_FILE = "tds_kb_full_posts.json"
INDEX_FILE = "tds_kb.index"
META_FILE = "tds_kb_meta.json"

# Step 1: Load posts
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    posts = json.load(f)

texts, metadata = [], []

# Step 2: Chunk content
for post in posts:
    content = post["content"]
    title = post["title"]
    url = post["url"]

    for i in range(0, len(content), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = content[i:i + CHUNK_SIZE]
        texts.append(chunk)
        metadata.append({"title": title, "url": url})

print(f"📄 Total chunks to embed: {len(texts)}")

# Step 3: Request embeddings from AI Pipe
headers = {
    "Authorization": f"Bearer {AI_PIPE_API_KEY}",
    "Content-Type": "application/json"
}

payload = {"input": texts,
           "model": AI_PIPE_EMBEDDING_MODEL}  # Specify the model if needed

print("📡 Sending request to AI Pipe...")
response = requests.post(AI_PIPE_EMBEDDING_ENDPOINT, headers=headers, json=payload)

if response.status_code != 200:
    raise Exception(f"Failed to get embeddings: {response.status_code} {response.text}")

data = response.json()
embeddings = [item["embedding"] for item in data["data"]]

print(f"✅ Received {len(embeddings)} embeddings")

# Step 4: Create FAISS index
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))

# Step 5: Save index and metadata
faiss.write_index(index, INDEX_FILE)

with open(META_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"🎉 Saved FAISS index to {INDEX_FILE} and metadata to {META_FILE}")
