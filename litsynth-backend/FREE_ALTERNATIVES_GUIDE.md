# LitSynth - Free Alternatives & Changes Guide

## 🎯 Overview
This document details all the changes made to use free/open-source alternatives instead of paid services, rename all Pi/Pano references to LitSynth, and remove all financial/insurance terminology.

---

## 🔄 Major Changes Summary

### 1. **LLM Provider: OpenAI → Perplexity AI**

**Why Changed:**
- OpenAI charges per token (can get expensive)
- Perplexity offers competitive pricing and online search capabilities
- Better for academic research with real-time information

**Before:**
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", temperature=0)
```

**After:**
```python
from openai import OpenAI

perplexity_client = OpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)

class PerplexityLLM:
    def __init__(self, model="llama-3.1-sonar-small-128k-online", temperature=0):
        # Perplexity implementation
```

**Environment Variable:**
```bash
# Old
OPENAI_API_KEY=sk-...

# New
PERPLEXITY_API_KEY=pplx-...
```

**Cost Comparison:**
- OpenAI GPT-4o: ~$0.03/1K tokens
- Perplexity Sonar Small: ~$0.001/1K tokens (30x cheaper!)
- Get API key: https://www.perplexity.ai/settings/api

**Models Available:**
- `llama-3.1-sonar-small-128k-online` (Recommended - fastest, cheapest)
- `llama-3.1-sonar-large-128k-online` (More powerful)
- `llama-3.1-sonar-huge-128k-online` (Most capable)

---

### 2. **Embeddings: Azure OpenAI → Sentence Transformers (FREE)**

**Why Changed:**
- Azure OpenAI requires paid subscription
- Sentence Transformers runs locally - completely FREE
- No API calls, no rate limits, no costs
- Privacy: your data never leaves your server

**Before:**
```python
from langchain_openai import AzureOpenAIEmbeddings

embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-3-large",
    dimensions=1536,
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_EMBD"],
    api_key=os.environ["AZURE_OPENAI_API_KEY_EMBD"],
)
```

**After:**
```python
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
```

**Environment Variable:**
```bash
# No API key needed!
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**Free Model Options:**
1. **all-MiniLM-L6-v2** (Recommended)
   - Dimension: 384
   - Speed: Very fast
   - Quality: Good for most tasks
   - Size: ~80MB

2. **all-mpnet-base-v2**
   - Dimension: 768
   - Speed: Medium
   - Quality: Better accuracy
   - Size: ~420MB

3. **paraphrase-multilingual-MiniLM-L12-v2**
   - Dimension: 384
   - Speed: Fast
   - Quality: Good for multiple languages
   - Size: ~110MB

**Performance Comparison:**
- Azure OpenAI: $0.00013/1K tokens, 1536 dims
- Sentence Transformers: **$0.00/1K tokens**, 384 dims, runs locally

**Vector Dimension Change:**
```python
# Old: 1536 dimensions (Azure)
# New: 384 dimensions (all-MiniLM-L6-v2)

# Updated in vector.py:
pc.create_index(
    name=index_name,
    dimension=384,  # Changed from 1536
    metric="cosine"
)
```

---

### 3. **Vector Database: Pinecone (FREE TIER)**

**Why Kept:**
- Pinecone offers a generous free tier
- 1 index, 100K vectors free forever
- Excellent for academic projects

**Free Tier Details:**
- **Storage:** 100,000 vectors
- **Queries:** Unlimited
- **Namespaces:** Unlimited
- **Cost:** $0/month
- **Signup:** https://www.pinecone.io/

**Configuration:**
```bash
PINECONE_API_KEY=your_key_here
PINECONE_INDEX_NAME=litsynth-research-index
PINECONE_ENVIRONMENT=gcp-starter  # Free tier
```

**Alternative (If you need more):**
- **Weaviate** (Open source, self-hosted)
- **Qdrant** (Open source, self-hosted)
- **FAISS** (Completely free, local only)

---

### 4. **Database: SQLite (FREE)**

**Why Kept:**
- Already free and open source
- No setup required
- Perfect for single-user applications
- File-based, no server needed

**Configuration:**
```bash
# Old
DATABASE_URL=sqlite:///./data/db/database.db

# New
DATABASE_URL=sqlite:///./data/db/litsynth.db
```

**Alternative (For production):**
- **PostgreSQL** (Free, open source)
- **Supabase** (Free tier: 500MB, PostgreSQL)

---

### 5. **Caching: Redis (FREE OPTIONS)**

**Local (Recommended for Development):**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

**Free Cloud Options:**
1. **Redis Cloud** (https://redis.com/try-free/)
   - 30MB free
   - Perfect for caching

2. **Upstash** (https://upstash.com/)
   - 10,000 commands/day free
   - Serverless Redis

**Configuration:**
```bash
REDIS_HOST=your-redis-host.redis.io
REDIS_PORT=12345
REDIS_PASSWORD=your-password
```

---

## 📝 Naming Changes: Pi/Pano → LitSynth

### Environment Variables
```bash
# Old
PI_MASTER_TOKEN=...
PI_INSECURE_MODE=False

# New
LITSYNTH_MASTER_TOKEN=...
LITSYNTH_INSECURE_MODE=False
```

### File Prefixes
```python
# Example
with NamedTemporaryFile(prefix='litsynth_', ...) as temp_file:
```

### Cache Namespace
```python
# Example
cache = Cache(..., namespace="litsynth")
```

### Function Names
```python
# Example
async def get_research_conf():
async def set_research_conf(research_conf):
```

### Database File
```bash
# Example
../data/db/litsynth.db
```

### Configuration File
```bash
# Example
../data/conf/research_config.xlsx
```

### Index Name
```bash
# Example
PINECONE_INDEX_NAME=litsynth-research-index
```

---

## 📚 LitSynth Core Concepts

### Key Terminology

| Concept | Description | Example |
|---------|-------------|---------|
| Workspace | Organizational unit for research | "NLP Research" |
| Workspace ID | Unique identifier (UUID) | "uuid-abc-123" |
| Research Paper | Academic documents being analyzed | PDF files |
| Vector Namespace | Workspace-scoped vector storage | Workspace ID |
| Chat | Conversational interface | Q&A with citations |

### Code Examples

**Variable Names:**
```python
# LitSynth variables
workspace_id = "uuid-abc-123"
workspace_name = "NLP Research"
research_papers = ["paper1.pdf", "paper2.pdf"]
chat_history = [...]
```

**Endpoint Organization:**
```python
# API endpoints organized by feature
# Tags: "workspaces", "documents", "chat", "authentication"

@app.post('/workspaces/', tags=["workspaces"])
@app.post('/upload-papers', tags=["documents"])
@app.post('/chat', tags=["chat"])
```

**Code Comments:**
```python
# LitSynth - Academic research document analysis
# RAG-based system for querying research papers
```

---

## 💰 Total Cost Comparison

### Before (Paid Services)
| Service | Monthly Cost | Annual Cost |
|---------|-------------|-------------|
| OpenAI GPT-4o | ~$50-200 | ~$600-2400 |
| Azure OpenAI Embeddings | ~$10-30 | ~$120-360 |
| **Total** | **$60-230** | **$720-2760** |

### After (Free Alternatives)
| Service | Monthly Cost | Annual Cost |
|---------|-------------|-------------|
| Perplexity | ~$5-20* | ~$60-240* |
| Sentence Transformers | $0 | $0 |
| Pinecone Free Tier | $0 | $0 |
| Redis Free Tier | $0 | $0 |
| SQLite | $0 | $0 |
| **Total** | **$5-20** | **$60-240** |

*Perplexity costs depend on usage. For a student project: ~$5-10/month

**Savings: 90-95% cost reduction!**

---

## 🚀 Setup Instructions with Free Alternatives

### 1. Install Dependencies

```bash
cd litsynth-backend/src
pip install -r requirements.txt
```

### 2. Get Free API Keys

**Perplexity (Required):**
1. Go to https://www.perplexity.ai/
2. Sign up for free account
3. Navigate to Settings → API
4. Generate API key
5. **Cost:** ~$5-10/month for typical usage

**Pinecone (Required):**
1. Go to https://www.pinecone.io/
2. Sign up for free account
3. Create a new project
4. Copy API key
5. **Cost:** $0 (free tier)

**Optional OCR Services:**
- Adobe PDF Services: https://developer.adobe.com/document-services/ (500 pages/month free)
- ILovePDF: https://www.ilovepdf.com/ (limited free tier)

### 3. Configure Environment

Create `.env` file:

```bash
# ===== Required =====
PERPLEXITY_API_KEY=pplx-your-key-here
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=litsynth-research-index
PINECONE_ENVIRONMENT=gcp-starter

# ===== Free Local Services =====
EMBEDDING_MODEL=all-MiniLM-L6-v2  # No API key needed!
REDIS_HOST=localhost
REDIS_PORT=6379

# ===== Security =====
LITSYNTH_MASTER_TOKEN=your-secure-token
LITSYNTH_INSECURE_MODE=False
DEBUG=True
```

### 4. Start Services

```bash
# Start Redis (local)
redis-server

# Or use Docker
docker run -p 6379:6379 redis:latest

# Start LitSynth
cd litsynth-backend/src
uvicorn main:app --reload --port 8000
```

### 5. First Run Notes

**Model Download:**
On first run, Sentence Transformers will download the embedding model (~80MB for all-MiniLM-L6-v2):

```
Downloading model: all-MiniLM-L6-v2
Progress: ████████████████████ 100%
Model loaded successfully!
```

This only happens once. Future runs are instant.

---

## 🎓 Academic-Specific Improvements

### 1. System Prompt
Changed from insurance advisor to academic research assistant:

```python
system_prompt = """
You are LitSynth, an intelligent research assistant specialized in academic literature analysis.
Your role is to help researchers understand and analyze academic papers...

When answering questions:
1. Base your responses on the provided context from research papers
2. Cite sources using [Source X] markers
3. Maintain academic rigor and accuracy
...
"""
```

### 2. Startup Message
```python
print("=" * 50)
print("Starting LitSynth - Academic Research Assistant")
print("=" * 50)
```

### 3. Endpoint Descriptions
All endpoint docstrings updated for academic context:
```python
@app.post('/upload-papers', tags=["documents"])
async def upload_papers(...):
    """
    Upload research papers (PDFs) to a workspace for analysis
    """
```

### 4. Error Messages
```python
# Example
"Workspace {workspace_id} not found"
"No documents found in workspace"
"Invalid file format - PDF required"
```

---

## ⚠️ Breaking Changes

### Required Environment Variable Updates

**Must Update:**
```bash
PI_MASTER_TOKEN → LITSYNTH_MASTER_TOKEN
PI_INSECURE_MODE → LITSYNTH_INSECURE_MODE
OPENAI_API_KEY → PERPLEXITY_API_KEY
AZURE_OPENAI_ENDPOINT_EMBD → (Remove - not needed)
AZURE_OPENAI_API_KEY_EMBD → (Remove - not needed)
```

**New Required:**
```bash
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Database Migration

**If you have existing data:**
1. Old database: `data/db/database.db`
2. New database: `data/db/litsynth.db`
3. To migrate: `cp database.db litsynth.db`

### Vector Store

**Dimension change: 1536 → 384**

If you have existing Pinecone index with 1536 dimensions:
1. Create new index with 384 dimensions
2. Or keep old index and update code back to Azure embeddings

---

## 📋 Checklist for Migration

- [ ] Update `.env` file with new variable names
- [ ] Get Perplexity API key
- [ ] Get Pinecone free tier account
- [ ] Install new dependencies (`pip install -r requirements.txt`)
- [ ] Download embedding model (happens automatically)
- [ ] Start Redis server
- [ ] Update any scripts using old variable names
- [ ] Test file upload with new workspace system
- [ ] Verify citations are working
- [ ] Check chat history persistence

---

## 🔍 Recommendations

### 1. **For Students (Recommended Setup)**
```bash
# Minimal cost, good performance
PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online
EMBEDDING_MODEL=all-MiniLM-L6-v2
# Cost: ~$5-10/month
```

### 2. **For Better Quality (Higher Cost)**
```bash
# Better accuracy, higher cost
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online
EMBEDDING_MODEL=all-mpnet-base-v2
# Cost: ~$15-30/month
```

### 3. **For Production**
- Use PostgreSQL instead of SQLite
- Add monitoring (Sentry free tier)
- Use Docker for deployment
- Add rate limiting
- Implement proper logging

### 4. **To Reduce Costs Further**
- Implement response caching (reduce LLM calls)
- Add query deduplication
- Batch process documents
- Limit context to top 3-5 chunks (currently 5)

### 5. **Performance Optimization**
```python
# Use GPU for embeddings if available
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cuda'},  # Instead of 'cpu'
)
```

### 6. **Monitoring**
Track your costs:
- Perplexity Dashboard: https://www.perplexity.ai/settings/api
- Pinecone Dashboard: https://app.pinecone.io/
- Monitor token usage in logs

---

## 🆘 Troubleshooting

### "Model not found" error
```bash
# Solution: Model will auto-download on first run
# Wait ~1-2 minutes for download to complete
```

### "Dimension mismatch" error
```bash
# Solution: Delete old Pinecone index and create new one with dimension=384
# Or use environment variable to match your index dimension
```

### "Perplexity API error"
```bash
# Check API key is correct
# Verify you have credits in your account
# Check rate limits
```

### High costs
```bash
# Use smaller model: sonar-small instead of sonar-large
# Implement caching
# Reduce context chunks (k=3 instead of k=5)
```

---

## 📚 Additional Resources

- **Perplexity Docs:** https://docs.perplexity.ai/
- **Sentence Transformers:** https://www.sbert.net/
- **Pinecone Docs:** https://docs.pinecone.io/
- **LangChain Docs:** https://python.langchain.com/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

**Total Estimated Monthly Cost:** $5-20 (down from $60-230)
**Savings:** 90-95%
**Perfect for:** Academic projects, student work, research prototypes
