# LitSynth API Documentation

## Overview
LitSynth is a RAG-based research assistant that enables researchers to upload academic papers and query them using natural language. The system provides cited responses based on the content of uploaded documents.

## Base URL
```
http://localhost:8000  (Development)
```

## Authentication
All endpoints (except root) require Bearer token authentication.

```http
Authorization: Bearer <your-token>
```

---

## API Endpoints

### 1. Workspace Management

#### Create Workspace
Create a new workspace for organizing research papers.

**Endpoint:** `POST /workspaces/`

**Request Body:**
```json
{
  "name": "My Research Project",
  "description": "Papers on RAG systems",
  "token_name": "your-token-name"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "My Research Project",
  "description": "Papers on RAG systems",
  "token_name": "your-token-name",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-10-15T12:00:00",
  "updated_at": "2025-10-15T12:00:00"
}
```

#### List Workspaces
Get all workspaces for the authenticated user.

**Endpoint:** `GET /workspaces/`

**Query Parameters:**
- `offset` (optional): Pagination offset (default: 0)
- `limit` (optional): Number of results (default: 100, max: 100)

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Research Project",
    "description": "Papers on RAG systems",
    "token_name": "user1",
    "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-10-15T12:00:00",
    "updated_at": "2025-10-15T12:00:00"
  }
]
```

#### Get Workspace Details
Get details of a specific workspace.

**Endpoint:** `GET /workspaces/{workspace_id}`

**Response:**
```json
{
  "id": 1,
  "name": "My Research Project",
  "description": "Papers on RAG systems",
  "token_name": "user1",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-10-15T12:00:00",
  "updated_at": "2025-10-15T12:00:00"
}
```

#### Delete Workspace
Delete a workspace and all associated data (documents, chat history).

**Endpoint:** `DELETE /workspaces/{workspace_id}`

**Response:**
```json
{
  "ok": true,
  "message": "Workspace 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

---

### 2. Document Management

#### Upload Research Papers
Upload PDF research papers to a workspace for analysis.

**Endpoint:** `POST /upload-papers`

**Request Parameters:**
- `workspace_id`: The workspace ID (form data)
- `overwrite_index`: Whether to overwrite existing documents (optional, default: false)
- `files`: List of PDF files (multipart/form-data)

**Response:**
```json
{
  "message": "ok",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "files_processed": 3,
  "indexed_results": [true, true, true],
  "processing_time": 15.432
}
```

#### Delete Document
Remove a specific document from a workspace.

**Endpoint:** `DELETE /documents/{workspace_id}/{file_name}`

**Response:**
```json
{
  "file_name": "research_paper.pdf",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "deleted successfully"
}
```

---

### 3. Chat Interface

#### Send Chat Message
Ask a question about uploaded research papers. Chat history is automatically managed.

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "query": "What are the main findings of these studies?",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "message": "Based on the research papers, the main findings are...\n\n[Source 1] indicates that...\n[Source 2] shows that...",
  "sources": [
    {
      "id": 1,
      "filename": "paper1.pdf",
      "page": 5,
      "snippet": "The study demonstrates that RAG systems improve accuracy by 23%..."
    },
    {
      "id": 2,
      "filename": "paper2.pdf",
      "page": 12,
      "snippet": "Our experiments show significant improvements in retrieval..."
    }
  ]
}
```

#### Get Chat History
Retrieve all chat messages for a workspace.

**Endpoint:** `GET /chat/{workspace_id}`

**Query Parameters:**
- `limit` (optional): Maximum messages to return (default: 100, max: 500)

**Response:**
```json
[
  {
    "id": 1,
    "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "user",
    "content": "What are the main findings?",
    "sources": null,
    "created_at": "2025-10-15T12:05:00"
  },
  {
    "id": 2,
    "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "assistant",
    "content": "The main findings indicate...",
    "sources": "[{\"id\": 1, \"filename\": \"paper1.pdf\", \"page\": 5}]",
    "created_at": "2025-10-15T12:05:05"
  }
]
```

#### Delete Chat History
Clear all chat history for a workspace.

**Endpoint:** `DELETE /chat/{workspace_id}`

**Response:**
```json
{
  "ok": true,
  "deleted_count": 24,
  "message": "Deleted 24 messages"
}
```

---

### 4. Token Management (Admin Only)

#### Create Token
Create a new authentication token (requires master token).

**Endpoint:** `POST /tokens/`

**Request Parameters:**
- `token_name`: Name for the token (query parameter)

**Response:**
```json
{
  "name": "user1",
  "token": "actual-token-string-here"
}
```

#### List Tokens
Get all tokens (requires master token).

**Endpoint:** `GET /tokens/`

**Response:**
```json
[
  {
    "name": "user1"
  }
]
```

#### Delete Token
Remove a token (requires master token).

**Endpoint:** `DELETE /tokens/{token_name}`

---

## Typical Workflow

### 1. Setup
```bash
# Create a token (admin only)
curl -X POST "http://localhost:8000/tokens/?token_name=researcher1" \
  -H "Authorization: Bearer MASTER_TOKEN"
```

### 2. Create Workspace
```bash
curl -X POST "http://localhost:8000/workspaces/" \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "NLP Research",
    "description": "Papers on transformer models",
    "token_name": "researcher1"
  }'
```

### 3. Upload Papers
```bash
curl -X POST "http://localhost:8000/upload-papers?workspace_id=WORKSPACE_ID" \
  -H "Authorization: Bearer USER_TOKEN" \
  -F "files=@paper1.pdf" \
  -F "files=@paper2.pdf"
```

### 4. Ask Questions
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What methodologies do these papers use?",
    "workspace_id": "WORKSPACE_ID"
  }'
```

### 5. View Chat History
```bash
curl -X GET "http://localhost:8000/chat/WORKSPACE_ID" \
  -H "Authorization: Bearer USER_TOKEN"
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Environment Variables

Required environment variables (set in `.env` file):

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Azure OpenAI for Embeddings
AZURE_OPENAI_ENDPOINT_EMBD=your-azure-endpoint
AZURE_OPENAI_API_KEY_EMBD=your-azure-key

# Pinecone Configuration
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=litsynth-index

# Application Configuration
PI_MASTER_TOKEN=your-master-token-for-admin-operations
DEBUG=false
PI_INSECURE_MODE=false
```

---

## Citation System

The citation system automatically:
1. Retrieves the 5 most relevant document chunks for each query
2. Provides source information (filename, page number, snippet)
3. Instructs the LLM to cite sources in responses using `[Source X]` markers
4. Returns structured source data with each response

**Source Data Structure:**
```json
{
  "id": 1,
  "filename": "paper_name.pdf",
  "page": 5,
  "snippet": "First 200 characters of the relevant text..."
}
```

---

## Notes

1. **Document Processing**: PDF files are automatically processed with OCR fallback if text extraction fails
2. **Vector Storage**: Documents are chunked into 700-character segments with 100-character overlap
3. **Chat History**: Automatically maintained per workspace, no manual management needed
4. **Workspace Isolation**: Each workspace maintains separate documents and chat history
5. **Deletion Cascade**: Deleting a workspace removes all associated documents and chat history

---

## Development

**Running the Server:**
```bash
cd litsynth-backend/src
uvicorn main:app --reload --port 8000
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs (in DEBUG mode)
- ReDoc: http://localhost:8000/redoc (disabled in production)
