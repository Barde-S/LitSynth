# LitSynth - RAG-Based Research Assistant

> An intelligent research assistant that enables researchers to query academic literature using natural language and receive accurate, cited responses.

---

## 🎯 Project Overview

LitSynth is a Retrieval-Augmented Generation (RAG) system designed for academic research. It allows users to:

- Upload research papers (PDF format)
- Ask questions in natural language
- Receive well-sourced answers with citations
- Maintain conversation history
- Organize papers into workspaces

---

## ✨ Key Features

### 🔍 Intelligent Document Processing
- **PDF Parsing**: Automatic text extraction from academic papers
- **OCR Support**: Fallback OCR for scanned documents
- **Smart Chunking**: 700-character segments with overlap for context preservation
- **Vector Indexing**: Pinecone-based similarity search

### 💬 Conversational Interface
- **Natural Language Queries**: Ask questions as you would to a colleague
- **Context-Aware Responses**: Maintains conversation history
- **Multi-Turn Conversations**: Follow-up questions understand previous context
- **Persistent History**: All conversations saved per workspace

### 📚 Citation System
- **Automatic Citations**: Every response includes source references
- **Source Metadata**: Filename, page number, and text snippets
- **Verifiable Claims**: Track where information comes from
- **Snippet Preview**: See relevant excerpts from source papers

### 🗂️ Workspace Management
- **Project Organization**: Create separate workspaces for different research areas
- **Document Collections**: Upload multiple papers per workspace
- **Isolated Contexts**: Each workspace maintains independent document sets
- **Easy Cleanup**: Delete workspaces with all associated data

---

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │
│   (React)   │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────────┐
│              FastAPI Backend                     │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Workspace │  │Document  │  │   Chat   │     │
│  │Management│  │Processing│  │  System  │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└───┬────────┬────────┬─────────────┬────────────┘
    │        │        │             │
┌───▼───┐ ┌─▼──────┐ ┌▼────────┐ ┌─▼─────────┐
│SQLite │ │Pinecone│ │LangChain│ │Perplexity │
│  DB   │ │ Vector │ │   PDF   │ │   AI      │
└───────┘ │  Store │ │ Loaders │ └───────────┘
          └────────┘ └─────────┘
```

---

## 💻 Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.10+** - Programming language
- **SQLModel** - SQL database ORM (Object-Relational Mapping)
- **LangChain** - Framework for document processing and RAG implementation
- **Perplexity AI** - Large Language Model for chat responses
- **Sentence Transformers** - Free local embedding models (Hugging Face)

### Frontend
- **React 18** - UI library for building interactive interfaces
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and development server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **React Query (@tanstack/react-query)** - Data fetching and caching
- **Zustand** - Lightweight state management
- **Axios** - HTTP client for API requests
- **Lucide React** - Icon library
- **React Markdown** - Markdown rendering for chat messages
- **date-fns** - Date utility library

### Storage & Caching
- **Pinecone** - Vector database for semantic search (free tier: 100K vectors)
- **SQLite** - Lightweight database for metadata and user data
- **Redis** - In-memory caching for improved performance

### Document Processing
- **PyPDF** - PDF parsing and text extraction
- **PyMuPDF** - Advanced PDF processing
- **Adobe PDF Services** - OCR for scanned documents (optional)
- **RecursiveCharacterTextSplitter** - Intelligent text chunking

### DevOps & Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Traefik** - Reverse proxy and load balancer
- **Uvicorn** - ASGI server for FastAPI

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Redis server
- Perplexity API key
- Pinecone account (free tier)

### Quick Setup

1. **Clone and navigate:**
```bash
cd litsynth-backend/src
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
Create `.env` file in `litsynth-backend/src/`:
```env
PERPLEXITY_API_KEY=your-perplexity-key
EMBEDDING_MODEL=all-MiniLM-L6-v2
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=litsynth-research-index
LITSYNTH_MASTER_TOKEN=secure-token
DEBUG=true
```

4. **Start Redis:**
```bash
redis-server
```

5. **Run the backend:**
```bash
uvicorn main:app --reload --port 8000
```

6. **Run the frontend:**
```bash
cd ../../litsynth-frontend
npm install
npm run dev
```

7. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md)**

---

## 📖 Usage

### 1. Create Workspace
```bash
curl -X POST "http://localhost:8000/workspaces/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "NLP Research", "description": "Transformer papers", "token_name": "user1"}'
```

### 2. Upload Papers
```bash
curl -X POST "http://localhost:8000/upload-papers?workspace_id=WORKSPACE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@paper1.pdf" \
  -F "files=@paper2.pdf"
```

### 3. Ask Questions
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main findings?", "workspace_id": "WORKSPACE_ID"}'
```

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step setup and testing guide
- **[LITSYNTH_API.md](LITSYNTH_API.md)** - Complete API reference
- **[FREE_ALTERNATIVES_GUIDE.md](FREE_ALTERNATIVES_GUIDE.md)** - Cost-effective deployment options

---

## 🔧 API Endpoints

### Workspace Management
- `POST /workspaces/` - Create workspace
- `GET /workspaces/` - List workspaces
- `GET /workspaces/{id}` - Get workspace details
- `DELETE /workspaces/{id}` - Delete workspace

### Document Management
- `POST /upload-papers` - Upload research papers
- `DELETE /documents/{workspace_id}/{filename}` - Delete document

### Chat Interface
- `POST /chat` - Send message and get cited response
- `GET /chat/{workspace_id}` - Get conversation history
- `DELETE /chat/{workspace_id}` - Clear chat history

### Authentication
- `POST /tokens/` - Create user token (admin)
- `GET /tokens/` - List tokens (admin)
- `DELETE /tokens/{name}` - Delete token (admin)

---

## 🎓 Example Use Cases

### Literature Review
**Query:** "What methodologies are commonly used in RAG systems?"
**Response:** LitSynth analyzes all papers and provides a summary with citations to specific papers and page numbers.

### Comparative Analysis
**Query:** "How do these papers compare method X and method Y?"
**Response:** Identifies relevant sections across papers and compares approaches with source citations.

### Concept Explanation
**Query:** "Explain the concept of retrieval-augmented generation"
**Response:** Synthesizes definitions and explanations from uploaded papers with proper citations.

### Finding Specific Information
**Query:** "What datasets were used in these studies?"
**Response:** Extracts dataset information from all papers with source references.

---

## 🔒 Security

- **Token-based authentication** for all endpoints
- **User isolation** - users can only access their workspaces
- **Master token** for admin operations
- **Workspace-level access control**
- **Secure credential storage** (bcrypt hashed)

---

## ⚠️ Known Limitations

1. **File Format**: Currently supports PDF and TXT only
2. **OCR Accuracy**: May struggle with complex layouts or low-quality scans
3. **Context Window**: Limited to top 5 most relevant chunks per query
4. **Citation Consistency**: LLM may not always use citation markers uniformly

---

## 🚀 Future Enhancements

### Planned Features
- Support for DOCX, HTML, Markdown
- Citation export (BibTeX, APA, MLA)
- Advanced search filters
- Document tagging and categorization
- Collaborative workspaces
- Export conversations to PDF/Word
- Integration with reference managers (Zotero, Mendeley)

### Technical Improvements
- Streaming responses for real-time feedback
- Enhanced caching strategies
- Multi-language support
- Fine-tuned embeddings for academic content
- Document versioning

---

## 🤝 Contributing

This is a final year project. For issues or suggestions:
1. Test thoroughly using the provided documentation
2. Check existing documentation for solutions
3. Review code comments in modified files

---

## 📝 License

Academic project - All rights reserved

---

## 👨‍💻 Author

**Shuaibu Sani Barde**
Final Year Project - A RAG-Based Research Assistant for Academic Literature

---

## 🙏 Acknowledgments

This project builds upon:
- LangChain for document processing
- Perplexity AI for language models
- Pinecone for vector storage
- FastAPI for the web framework
- React and modern web technologies

---

## 📞 Support

- **Interactive API Docs**: http://localhost:8000/docs
- **Quick Start Guide**: See [QUICKSTART.md](QUICKSTART.md)
- **API Reference**: See [LITSYNTH_API.md](LITSYNTH_API.md)

---

## 🎯 Project Goals

This project demonstrates:
✅ RAG implementation on academic content
✅ Vector embeddings and document indexing
✅ LLM integration with citation tracking
✅ Practical tool for academic research
✅ RESTful API design
✅ Modern full-stack development
✅ Document processing pipelines

---

**Built for researchers by researchers**
