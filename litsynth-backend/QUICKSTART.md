# LitSynth Quick Start Guide

This guide will help you set up and test your LitSynth system.

---

## Prerequisites

1. Python 3.10+
2. Redis server (local or free cloud)
3. **Perplexity API key** (replaces OpenAI - cheaper!)
4. **Pinecone free tier account** (100K vectors free)
5. **No Azure required!** (using free Sentence Transformers)

**💰 Cost: ~$5-10/month** (down from $60-230/month with OpenAI+Azure!)

---

## Setup

### 1. Get Free/Cheap API Keys

**Perplexity AI (Required - ~$5-10/month):**
1. Sign up at https://www.perplexity.ai/
2. Go to Settings → API
3. Generate API key
4. Add credits ($5-10 is plenty for testing)

**Pinecone (Free Tier):**
1. Sign up at https://www.pinecone.io/
2. Create a project
3. Copy API key
4. 100K vectors free forever!

### 2. Install Dependencies

```bash
cd litsynth-backend/src
pip install -r requirements.txt
```

**Note:** On first run, the embedding model (~80MB) will download automatically. This is free and runs locally!

### 3. Configure Environment

Create a `.env` file in `litsynth-backend/src/`:

```bash
# ===== LLM Configuration (Perplexity - Cheap!) =====
PERPLEXITY_API_KEY=pplx-your-api-key-here

# ===== FREE Local Embeddings (No API key needed!) =====
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ===== Pinecone (Free Tier) =====
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=litsynth-research-index
PINECONE_ENVIRONMENT=gcp-starter

# ===== Redis (Local or Free Cloud) =====
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# ===== Application Security =====
LITSYNTH_MASTER_TOKEN=your-secure-master-token
DEBUG=true
LITSYNTH_INSECURE_MODE=false
```

### 4. Start Redis (if not using Docker)

```bash
# macOS (via Homebrew)
brew services start redis

# Linux
sudo systemctl start redis

# Or run directly
redis-server
```

### 5. Start the Application

```bash
cd litsynth-backend/src
uvicorn main:app --reload --port 8000
```

You should see:
```
==================================================
Starting LitSynth - Academic Research Assistant
==================================================
VECTOR: Using free embedding model: all-MiniLM-L6-v2
VECTOR: Model will be downloaded on first run (~100MB)
VECTOR: Index litsynth-research-index already exists, using it...
LitSynth started successfully!
==================================================
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**First Run:** The embedding model will download (~1-2 minutes). Future starts are instant!

---

## Testing the API

### Step 1: Create an Authentication Token

```bash
curl -X POST "http://localhost:8000/tokens/?token_name=researcher1" \
  -H "Authorization: Bearer your-secure-master-token"
```

**Response:**
```json
{
  "name": "researcher1",
  "token": "vB8rX2jK9mN4pQ7sT1wY5zC3fH6kL0dA8eR2uI9oP4"
}
```

**Save this token!** You'll need it for all subsequent requests.

---

### Step 2: Create a Workspace

```bash
export USER_TOKEN="vB8rX2jK9mN4pQ7sT1wY5zC3fH6kL0dA8eR2uI9oP4"

curl -X POST "http://localhost:8000/workspaces/" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RAG Systems Research",
    "description": "Papers on Retrieval-Augmented Generation",
    "token_name": "researcher1"
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "RAG Systems Research",
  "description": "Papers on Retrieval-Augmented Generation",
  "token_name": "researcher1",
  "workspace_id": "a3f5c8d2-9e14-4b76-8a21-3c9f7d5e2b1a",
  "created_at": "2025-10-15T14:30:00",
  "updated_at": "2025-10-15T14:30:00"
}
```

**Save the `workspace_id`!**

---

### Step 3: Upload Research Papers

```bash
export WORKSPACE_ID="a3f5c8d2-9e14-4b76-8a21-3c9f7d5e2b1a"

curl -X POST "http://localhost:8000/upload-papers?workspace_id=$WORKSPACE_ID" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -F "files=@/path/to/paper1.pdf" \
  -F "files=@/path/to/paper2.pdf"
```

**Response:**
```json
{
  "message": "ok",
  "workspace_id": "a3f5c8d2-9e14-4b76-8a21-3c9f7d5e2b1a",
  "files_processed": 2,
  "indexed_results": [true, true],
  "processing_time": 12.345
}
```

**Note:** Processing may take several seconds per file, especially with OCR.

---

### Step 4: Ask Questions

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main findings in these papers?",
    "workspace_id": "'$WORKSPACE_ID'"
  }'
```

**Response:**
```json
{
  "message": "Based on the research papers, the main findings are:\n\n[Source 1] demonstrates that RAG systems significantly improve response accuracy by combining retrieval with generation. The study shows a 23% improvement in factual correctness compared to baseline LLMs.\n\n[Source 2] presents evidence that vector similarity search is crucial for effective retrieval, with cosine similarity outperforming other metrics by 15%.",
  "sources": [
    {
      "id": 1,
      "filename": "paper1.pdf",
      "page": 5,
      "snippet": "Our experiments demonstrate that RAG systems achieve 23% higher accuracy in factual responses compared to baseline large language models..."
    },
    {
      "id": 2,
      "filename": "paper2.pdf",
      "page": 12,
      "snippet": "Vector similarity search using cosine distance proved most effective, outperforming Euclidean and Manhattan distances by 15% in retrieval accuracy..."
    }
  ]
}
```

---

### Step 5: View Chat History

```bash
curl -X GET "http://localhost:8000/chat/$WORKSPACE_ID" \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "workspace_id": "a3f5c8d2-9e14-4b76-8a21-3c9f7d5e2b1a",
    "role": "user",
    "content": "What are the main findings in these papers?",
    "sources": null,
    "created_at": "2025-10-15T14:35:00"
  },
  {
    "id": 2,
    "workspace_id": "a3f5c8d2-9e14-4b76-8a21-3c9f7d5e2b1a",
    "role": "assistant",
    "content": "Based on the research papers, the main findings are...",
    "sources": "[{\"id\": 1, \"filename\": \"paper1.pdf\", \"page\": 5, ...}]",
    "created_at": "2025-10-15T14:35:03"
  }
]
```

---

### Step 6: List Workspaces

```bash
curl -X GET "http://localhost:8000/workspaces/" \
  -H "Authorization: Bearer $USER_TOKEN"
```

---

### Step 7: Delete Chat History (Optional)

```bash
curl -X DELETE "http://localhost:8000/chat/$WORKSPACE_ID" \
  -H "Authorization: Bearer $USER_TOKEN"
```

---

### Step 8: Delete Document (Optional)

```bash
curl -X DELETE "http://localhost:8000/documents/$WORKSPACE_ID/paper1.pdf" \
  -H "Authorization: Bearer $USER_TOKEN"
```

---

### Step 9: Delete Workspace (Optional)

```bash
curl -X DELETE "http://localhost:8000/workspaces/$WORKSPACE_ID" \
  -H "Authorization: Bearer $USER_TOKEN"
```

---

## Using the Interactive API Documentation

FastAPI provides interactive documentation at:

**Swagger UI:** http://localhost:8000/docs

Here you can:
1. Click on any endpoint to expand it
2. Click "Try it out"
3. Fill in the parameters
4. Click "Execute"
5. View the response

**Note:** Remember to authenticate first using the "Authorize" button in the top right.

---

## Testing with Python

Create a test script `test_litsynth.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"
MASTER_TOKEN = "your-secure-master-token"

# 1. Create user token
response = requests.post(
    f"{BASE_URL}/tokens/",
    params={"token_name": "test_user"},
    headers={"Authorization": f"Bearer {MASTER_TOKEN}"}
)
user_token = response.json()["token"]
print(f"User token: {user_token}")

# 2. Create workspace
headers = {"Authorization": f"Bearer {user_token}"}
workspace_data = {
    "name": "Test Workspace",
    "description": "Testing LitSynth",
    "token_name": "test_user"
}
response = requests.post(
    f"{BASE_URL}/workspaces/",
    headers=headers,
    json=workspace_data
)
workspace_id = response.json()["workspace_id"]
print(f"Workspace ID: {workspace_id}")

# 3. Upload papers
files = [
    ("files", open("paper1.pdf", "rb")),
    ("files", open("paper2.pdf", "rb"))
]
response = requests.post(
    f"{BASE_URL}/upload-papers",
    params={"workspace_id": workspace_id},
    headers=headers,
    files=files
)
print(f"Upload result: {response.json()}")

# 4. Ask question
query_data = {
    "query": "What methodologies are used in these papers?",
    "workspace_id": workspace_id
}
response = requests.post(
    f"{BASE_URL}/chat",
    headers=headers,
    json=query_data
)
result = response.json()
print(f"\nAnswer: {result['message']}")
print(f"\nSources: {json.dumps(result['sources'], indent=2)}")

# 5. Get chat history
response = requests.get(
    f"{BASE_URL}/chat/{workspace_id}",
    headers=headers
)
print(f"\nChat history: {len(response.json())} messages")
```

Run it:
```bash
python test_litsynth.py
```

---

## Common Issues

### Issue: "PINECONE_API_KEY not found"
**Solution:** Make sure `.env` file is in the correct location and contains all required variables.

### Issue: "Connection refused" for Redis
**Solution:** Start Redis server:
```bash
redis-server
```

### Issue: "Index not found" in Pinecone
**Solution:** The app will create the index automatically on first run. Wait a few seconds and try again.

### Issue: "OCR failed"
**Solution:** This is normal for some PDFs. The system will try multiple OCR providers. If all fail, the document may be empty or corrupted.

### Issue: "No relevant context found"
**Solution:**
1. Verify documents were uploaded successfully
2. Check that the workspace_id is correct
3. Try rephrasing your query

---

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
cd litsynth-backend

# Development
docker compose -f docker-compose-dev.yml up --build

# Production
docker compose -f docker-compose-prod.yml up --build
```

---

## Next Steps

1. **Test thoroughly**: Try different types of queries
2. **Use the frontend**: The React frontend is already built in `litsynth-frontend/`
3. **Add features**: Implement additional enhancements as needed
4. **Deploy**: Set up production environment
5. **Document**: Create user documentation and tutorials

---

## Support

- **API Documentation**: See `LITSYNTH_API.md`
- **Free Alternatives**: See `FREE_ALTERNATIVES_GUIDE.md`
- **Interactive Docs**: http://localhost:8000/docs
- **Code Comments**: Check inline comments in source files

---

## Quick Reference

**Environment Variables:**
```bash
export USER_TOKEN="your-user-token"
export WORKSPACE_ID="your-workspace-id"
export MASTER_TOKEN="your-master-token"
```

**Essential Endpoints:**
- Create workspace: `POST /workspaces/`
- Upload papers: `POST /upload-papers`
- Chat: `POST /chat`
- Get history: `GET /chat/{workspace_id}`
- Delete workspace: `DELETE /workspaces/{workspace_id}`

**Headers:**
```bash
-H "Authorization: Bearer $USER_TOKEN"
-H "Content-Type: application/json"
```

---

Good luck with your LitSynth implementation! 🎓🤖
