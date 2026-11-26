# LitSynth - Academic Research Assistant

LitSynth is an AI-powered research assistant that helps you analyze and interact with academic research papers. Upload PDFs, ask questions, and get intelligent responses with source citations.

## Features

- **Email Registration with OTP Verification** - Secure account creation
- **Workspace Management** - Organize research by project
- **PDF Upload & Processing** - Upload and index research papers
- **AI-Powered Chat** - Ask questions about your uploaded documents
- **Source Citations** - Responses include page numbers and document references
- **Chat History** - Persistent conversation history per workspace

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Frontend | React + TypeScript + Vite |
| LLM | Google Gemini 1.5 Flash |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Vector Database | Pinecone |
| Database | SQLite + SQLModel |
| State Management | Zustand |
| Email | Gmail SMTP |

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- Google Gemini API key
- Pinecone API key
- Gmail account with App Password (for OTP)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Barde-S/LitSynth.git
cd LitSynth
```

### 2. Backend Setup

```bash
cd litsynth-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt
```

### 3. Configure Environment Variables

Create `litsynth-backend/src/.env`:

```env
# LLM Configuration (Google Gemini)
GOOGLE_API_KEY=your_gemini_api_key

# Embedding Service (Free - Runs Locally)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Vector Database (Pinecone)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=litsynth-research-index
PINECONE_ENVIRONMENT=gcp-starter

# JWT Secret Key (generate a secure random string)
JWT_SECRET_KEY=your_jwt_secret_key_min_32_chars

# Email Configuration (for OTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM_EMAIL=your_email@gmail.com

# Database
DATABASE_URL=sqlite:///./data/db/litsynth.db

# Debug Mode
DEBUG=True
```

### 4. Frontend Setup

```bash
cd litsynth-frontend

# Install dependencies
npm install
```

## Running the Application

### Start Backend

```bash
cd litsynth-backend/src
source ../venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Start Frontend

```bash
cd litsynth-frontend
npm run dev
```

### Access the Application

- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

1. **Register** - Enter your email, verify with OTP, create password
2. **Login** - Sign in with email and password
3. **Create Workspace** - Organize your research papers by project
4. **Upload PDFs** - Add research papers to your workspace
5. **Chat** - Ask questions about your uploaded documents
6. **View Sources** - See citations with page numbers for AI responses

## Project Structure

```
LitSynth/
├── litsynth-backend/
│   ├── src/
│   │   ├── main.py              # FastAPI endpoints
│   │   ├── chat.py              # Gemini LLM integration
│   │   ├── models.py            # Database models
│   │   ├── vector.py            # Pinecone integration
│   │   ├── processors.py        # PDF processing
│   │   ├── email_service.py     # OTP email service
│   │   ├── requirements.txt     # Python dependencies
│   │   └── .env                 # Environment variables
│   └── venv/                    # Python virtual environment
│
├── litsynth-frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API service
│   │   ├── store/               # Zustand state
│   │   └── types/               # TypeScript types
│   └── package.json             # Node dependencies
│
├── README.md
├── LICENSE
└── SYSTEM_WORKING_SUMMARY.md
```

## API Endpoints

### Authentication
- `POST /auth/send-otp` - Send OTP to email
- `POST /auth/verify-otp` - Verify OTP code
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Workspaces
- `GET /workspaces/` - List workspaces
- `POST /workspaces/` - Create workspace
- `GET /workspaces/{id}` - Get workspace
- `DELETE /workspaces/{id}` - Delete workspace

### Documents
- `POST /upload-papers?workspace_id={id}` - Upload PDFs
- `GET /workspaces/{id}/documents` - List documents
- `DELETE /documents/{workspace_id}/{filename}` - Delete document

### Chat
- `POST /chat` - Send message
- `GET /chat/{workspace_id}` - Get history
- `DELETE /chat/{workspace_id}` - Clear history

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Shuaibu Sani Barde - Final Year Project 2026
