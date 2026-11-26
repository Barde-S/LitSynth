import os
# Must be set before any HuggingFace/tokenizers/numpy imports to prevent semaphore leaks
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import time
import json
import shutil
import secrets
import asyncio
from uuid import uuid4
from datetime import datetime, timedelta
from typing import Annotated, Optional
from pydantic import BaseModel

from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi.responses import FileResponse, StreamingResponse

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, UploadFile, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlmodel import Session, SQLModel, create_engine, select

from passlib.context import CryptContext
from jose import JWTError, jwt

from aiocache import Cache
from aiocache.serializers import PickleSerializer

from processors import FileProcessor, get_prefix, _sync_embed_texts, _sync_store_preembedded
from chat import get_chat_chain, get_relevant_context
from progress_manager import progress_manager

from vector import init_chroma_client, delete_all_namespace, delete_document, get_raw_collection, get_workspace_document_names, embeddings as embedding_model


from dotenv import load_dotenv
# Load .env from parent directory (litsynth-backend/)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)
DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']
MASTER_TOKEN = os.getenv("LITSYNTH_MASTER_TOKEN", "")
INSECURE_MODE = os.getenv('LITSYNTH_INSECURE_MODE', 'false').lower() in ['true', '1', 'yes']
INSECURE_MODE = INSECURE_MODE and DEBUG # force disable insecure mode in production

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if not MASTER_TOKEN:
    print("WARNING: No master token is set for LitSynth")
    print("Please set LITSYNTH_MASTER_TOKEN in .env")

# Debug: Print JWT key status
if DEBUG:
    print(f"JWT_SECRET_KEY loaded: {'Yes (from env)' if os.getenv('JWT_SECRET_KEY') else 'No (random generated)'}")
    print(f"JWT_SECRET_KEY (first 20 chars): {JWT_SECRET_KEY[:20]}...")

if INSECURE_MODE:
    print("WARNING: INSECURE_MODE is active, endpoints are not secure!")

# CACHE SETUP --------------------
# Redis configuration from environment
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

cache = Cache(
    Cache.REDIS,
    endpoint=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    serializer=PickleSerializer(),
    namespace="litsynth"
)

# DATABASE SETUP --------------
from models import *
from models import User, UserCreate, UserLogin, UserPublic, Workspace, WorkspaceCreate, WorkspacePublic, Chat, ChatPublic, ChatMessage, ChatMessageCreate, ChatMessagePublic, OTP, OTPRequest, OTPVerify, RegisterWithOTP
from email_service import generate_otp, get_otp_expiry, send_otp_email

# Use absolute path for database and document storage
BASE_DIR = Path(__file__).resolve().parent.parent

# Document storage directory
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
# Use PostgreSQL in production (from DATABASE_URL), SQLite for local development
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Production: PostgreSQL (Render provides DATABASE_URL)
    # Render provides postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    if DEBUG:
        print(f"DATABASE: Using PostgreSQL (production)")

    engine = create_engine(DATABASE_URL, echo=DEBUG, pool_pre_ping=True)
else:
    # Development: SQLite
    sqlite_file_name = BASE_DIR / "data" / "db" / "litsynth.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    if DEBUG:
        print(f"DATABASE: Using SQLite (development): {sqlite_url}")

    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, echo=DEBUG, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    get DB session
    """
    with Session(engine) as session:
        yield session


# INIT THE APP ---------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 50)
    print("Starting LitSynth - Academic Research Assistant")
    print("=" * 50)

    # Increase default thread pool so background embedding tasks don't get starved by request handlers
    import concurrent.futures
    loop = asyncio.get_event_loop()
    loop.set_default_executor(concurrent.futures.ThreadPoolExecutor(max_workers=8))

    create_db_and_tables()
    # app.index_db = init_pinecone_index()  # PINECONE (OLD)
    app.chroma_client = init_chroma_client()  # CHROMADB (NEW)

    print("LitSynth started successfully!")
    print("=" * 50)

    yield

    # Shutdown Clean up
    print("LitSynth shutting down...")

if DEBUG:
    app = FastAPI(lifespan=lifespan)
else:
    app = FastAPI(
        lifespan=lifespan,
        openapi_url="/mridSuF5ztpc8Q/openapi.json",
        redoc_url=None,
        docs_url="/EKfxgVHG1WPJMA/docs"
    )

# INIT server wide stuff (config, index .. ) -------------------


# SECURITY ----------------------------------
security = HTTPBearer()

# CORS Configuration
# NOTE: Cannot use ["*"] with allow_credentials=True
# Must specify exact origins when using credentials
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
origins = [
    "https://litsynth.duckdns.org",  # Production HTTPS (custom domain)
    "http://litsynth.duckdns.org",   # Production HTTP (redirects to HTTPS)
    "http://34.118.199.221",         # Production frontend (Nginx, IP)
    "http://34.118.199.221:8000",    # Direct backend access
    "http://localhost:3000",         # Development frontend
    "http://localhost:5173",         # Development frontend (Vite default)
    "http://localhost:5174",         # Development frontend (Vite alternate)
    "http://localhost:8000",         # Development backend
]

# Add FRONTEND_URL from environment if different
if FRONTEND_URL not in origins:
    origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def validate_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
    ):
    if INSECURE_MODE:
        return True

    if credentials.credentials != MASTER_TOKEN:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return True

def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Session = Depends(get_session),
) -> User:
    """
    Validate JWT token and return the current user.
    """
    if INSECURE_MODE:
        # Return or create a dev user for insecure mode
        dev_user = session.exec(select(User).where(User.email == "dev@local")).first()
        if not dev_user:
            dev_user = User(email="dev@local", hashed_password=get_password_hash("devpass"))
            session.add(dev_user)
            session.commit()
            session.refresh(dev_user)
        return dev_user

    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

# ENDPOINTS --------------------------

@app.get('/')
def get_root():
    return {'message': 'Go to /docs to view the API documentation.'}

@app.get('/health', tags=["system"])
async def health_check():
    """
    Health check endpoint for monitoring and deployment platforms (e.g., Render)
    Returns service status and basic system info
    """
    return {
        "status": "healthy",
        "service": "litsynth-backend",
        "version": "1.0.0"
    }

# AUTH RESPONSE MODEL
class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic

class OTPResponse(BaseModel):
    message: str
    email: str

# AUTH ENDPOINTS --------------------------

@app.post("/auth/send-otp", tags=["auth"], response_model=OTPResponse)
async def send_otp(
    request: OTPRequest,
    session: Session = Depends(get_session),
):
    """
    Send OTP to email for registration verification.
    """
    email = request.email.lower()

    # Validate email format (basic)
    if "@" not in email or "." not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Check if email already registered and verified
    existing_user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing_user and existing_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Invalidate any existing OTPs for this email
    existing_otps = session.exec(
        select(OTP).where(OTP.email == email, OTP.is_used == False)
    ).all()
    for otp in existing_otps:
        otp.is_used = True
    session.commit()

    # Generate new OTP
    otp_code = generate_otp()
    otp_record = OTP(
        email=email,
        otp_code=otp_code,
        purpose="registration",
        expires_at=get_otp_expiry()
    )
    session.add(otp_record)
    session.commit()

    # Send OTP email
    email_sent = send_otp_email(email, otp_code, "registration")

    if not email_sent and not DEBUG:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email"
        )

    return OTPResponse(
        message="OTP sent successfully. Please check your email.",
        email=email
    )

@app.post("/auth/verify-otp", tags=["auth"])
async def verify_otp(
    request: OTPVerify,
    session: Session = Depends(get_session),
):
    """
    Verify OTP code (for checking before registration).
    """
    email = request.email.lower()

    # Find valid OTP
    otp_record = session.exec(
        select(OTP).where(
            OTP.email == email,
            OTP.otp_code == request.otp_code,
            OTP.is_used == False,
            OTP.expires_at > datetime.utcnow()
        )
    ).first()

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    return {"message": "OTP verified successfully", "valid": True}

@app.post("/auth/register", tags=["auth"], response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterWithOTP,
    session: Session = Depends(get_session),
):
    """
    Register a new user with email, password, and verified OTP.
    """
    email = user_data.email.lower()

    # Validate email format (basic)
    if "@" not in email or "." not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Validate password strength (basic)
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    # Verify OTP
    otp_record = session.exec(
        select(OTP).where(
            OTP.email == email,
            OTP.otp_code == user_data.otp_code,
            OTP.is_used == False,
            OTP.expires_at > datetime.utcnow()
        )
    ).first()

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP. Please request a new one."
        )

    # Mark OTP as used
    otp_record.is_used = True
    session.commit()

    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing_user:
        if existing_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        else:
            # Update existing unverified user
            existing_user.hashed_password = get_password_hash(user_data.password)
            existing_user.is_verified = True
            session.commit()
            session.refresh(existing_user)
            db_user = existing_user
    else:
        # Create new verified user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=email,
            hashed_password=hashed_password,
            is_verified=True
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(db_user.id)})

    return AuthResponse(
        access_token=access_token,
        user=UserPublic.model_validate(db_user)
    )

@app.post("/auth/login", tags=["auth"], response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    session: Session = Depends(get_session),
):
    """
    Login with email and password.
    """
    user = session.exec(
        select(User).where(User.email == credentials.email.lower())
    ).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please complete registration first."
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return AuthResponse(
        access_token=access_token,
        user=UserPublic.model_validate(user)
    )

@app.get("/auth/me", tags=["auth"], response_model=UserPublic)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user.
    """
    return current_user

# WORKSPACE ENDPOINTS --------------------------

@app.post("/workspaces/", tags=["workspaces"], status_code=status.HTTP_201_CREATED)
async def create_workspace(
    *,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    workspace_data: WorkspaceCreate
):
    """
    Create a new workspace for organizing research papers
    """
    workspace_id = str(uuid4())

    try:
        db_workspace = Workspace(
            name=workspace_data.name,
            description=workspace_data.description,
            user_id=user.id,
            workspace_id=workspace_id
        )
        session.add(db_workspace)
        session.commit()
        session.refresh(db_workspace)

        # AUTO-CREATE DEFAULT CHAT (NEW)
        default_chat = Chat(
            chat_id=str(uuid4()),
            workspace_id=workspace_id,
            title="General Chat",
            message_count=0
        )
        session.add(default_chat)
        session.commit()

        if DEBUG:
            print(f"Created default chat for workspace {workspace_id}")

        return WorkspacePublic.model_validate(db_workspace)
    except Exception as e:
        session.rollback()
        if DEBUG: print(f"Error creating workspace: {e}")
        raise HTTPException(status_code=409, detail="Failed to create workspace")

@app.get("/workspaces/", tags=["workspaces"], response_model=list[WorkspacePublic])
async def list_workspaces(
    *,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """
    List all workspaces for the authenticated user
    """
    workspaces = session.exec(
        select(Workspace)
        .where(Workspace.user_id == user.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return workspaces

@app.get("/workspaces/{workspace_id}", tags=["workspaces"], response_model=WorkspacePublic)
async def get_workspace(
    *,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    workspace_id: str
):
    """
    Get details of a specific workspace
    """
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace {workspace_id} not found")

    return workspace

@app.delete("/workspaces/{workspace_id}", tags=["workspaces"])
async def delete_workspace(
    *,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    workspace_id: str
):
    """
    Delete a workspace and all associated data (documents, chat history)
    """
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace {workspace_id} not found")

    # Delete all chats and their messages associated with this workspace
    chats = session.exec(
        select(Chat).where(Chat.workspace_id == workspace_id)
    ).all()

    total_messages = 0
    for chat in chats:
        # Delete all messages in this chat
        messages = session.exec(
            select(ChatMessage).where(ChatMessage.chat_id == chat.chat_id)
        ).all()
        total_messages += len(messages)
        for msg in messages:
            session.delete(msg)

        # Delete the chat
        session.delete(chat)

    if DEBUG:
        print(f"Deleted {len(chats)} chats with {total_messages} messages from workspace {workspace_id}")

    # Delete vectors from ChromaDB (delete collection)
    try:
        # app.index_db.delete(delete_all=True, namespace=workspace_id)  # PINECONE (OLD)
        app.chroma_client.delete_collection(workspace_id)  # CHROMADB (NEW)
        if DEBUG: print(f"Deleted vectors for workspace {workspace_id}")
    except Exception as e:
        if DEBUG: print(f"Error deleting vectors: {e}")

    # Delete workspace
    session.delete(workspace)
    session.commit()

    return {"ok": True, "message": f"Workspace {workspace_id} deleted successfully"}

# CHAT MANAGEMENT ENDPOINTS --------------------------

@app.post("/workspaces/{workspace_id}/chats", tags=["chats"], response_model=ChatPublic)
async def create_chat(
    workspace_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    title: Optional[str] = None
):
    """
    Create a new chat in a workspace
    - Auto-generates title if not provided (e.g., "Chat 1", "Chat 2")
    - Returns created chat with chat_id
    """
    # Verify workspace exists and belongs to user
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Auto-generate title if not provided
    if not title:
        chat_count = len(session.exec(
            select(Chat).where(Chat.workspace_id == workspace_id)
        ).all())
        title = f"Chat {chat_count + 1}"

    # Create chat
    chat = Chat(
        chat_id=str(uuid4()),
        workspace_id=workspace_id,
        title=title,
        message_count=0
    )
    session.add(chat)
    session.commit()
    session.refresh(chat)

    if DEBUG:
        print(f"Created chat {chat.chat_id} in workspace {workspace_id}")

    return chat

@app.get("/workspaces/{workspace_id}/chats", tags=["chats"], response_model=list[ChatPublic])
async def get_chats(
    workspace_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """
    Get all chats in a workspace
    - Returns chats ordered by updated_at (most recent first)
    - Includes message_count for each chat
    """
    # Verify workspace access
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Get all chats
    chats = session.exec(
        select(Chat)
        .where(Chat.workspace_id == workspace_id)
        .order_by(Chat.updated_at.desc())
    ).all()

    return chats

@app.get("/chats/{chat_id}", tags=["chats"], response_model=ChatPublic)
async def get_chat(
    chat_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """
    Get a specific chat by ID
    - Verifies user has access via workspace ownership
    """
    chat = session.exec(select(Chat).where(Chat.chat_id == chat_id)).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Verify workspace access
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == chat.workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")

    return chat

@app.patch("/chats/{chat_id}", tags=["chats"], response_model=ChatPublic)
async def update_chat(
    chat_id: str,
    title: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """
    Update chat title (rename chat)
    """
    chat = session.exec(select(Chat).where(Chat.chat_id == chat_id)).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Verify access
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == chat.workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")

    chat.title = title
    chat.updated_at = datetime.utcnow()
    session.add(chat)
    session.commit()
    session.refresh(chat)

    if DEBUG:
        print(f"Updated chat {chat_id} title to '{title}'")

    return chat

@app.delete("/chats/{chat_id}", tags=["chats"])
async def delete_chat(
    chat_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """
    Delete a chat and all its messages
    """
    chat = session.exec(select(Chat).where(Chat.chat_id == chat_id)).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Verify access
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == chat.workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")

    # Delete all messages in chat
    messages = session.exec(
        select(ChatMessage).where(ChatMessage.chat_id == chat_id)
    ).all()

    for message in messages:
        session.delete(message)

    # Delete chat
    session.delete(chat)
    session.commit()

    if DEBUG:
        print(f"Deleted chat {chat_id} with {len(messages)} messages")

    return {"ok": True, "message": f"Chat deleted with {len(messages)} messages"}

# DOCUMENT UPLOAD ENDPOINTS (SIMPLIFIED FOR RESEARCH PAPERS) --------------------------

@app.get('/upload-progress/{upload_id}', tags=["documents"])
async def stream_upload_progress(
    upload_id: str,
    user: User = Depends(get_current_user),
):
    """
    Stream upload/processing progress via Server-Sent Events (SSE).

    Connect to this endpoint after starting an upload to receive real-time
    progress updates for document processing stages (OCR, chunking, embedding, indexing).
    """
    # Verify the upload exists
    progress = progress_manager.get_progress(upload_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload {upload_id} not found or expired"
        )

    async def event_generator():
        queue = progress_manager.subscribe(upload_id)
        try:
            # Send initial state
            initial_data = {
                "upload_id": upload_id,
                "files": {
                    f: {
                        "stage": fp.stage,
                        "progress": fp.progress,
                        "error": fp.error,
                        "pages": fp.pages,
                        "chunks": fp.chunks
                    }
                    for f, fp in progress.files.items()
                },
                "completed": progress.completed
            }
            yield f"data: {json.dumps(initial_data)}\n\n"

            # Stream updates until complete
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(data)}\n\n"
                    if data.get("completed"):
                        break
                except asyncio.TimeoutError:
                    # Send keepalive comment to prevent connection timeout
                    yield f": keepalive\n\n"
        finally:
            progress_manager.unsubscribe(upload_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering for SSE
        }
    )


@app.post('/upload-papers', tags=["documents"])
async def upload_papers(
    files: list[UploadFile],
    workspace_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    overwrite_index: bool = False,
):
    """
    Upload research papers (PDFs) to a workspace for analysis.

    Returns immediately with an upload_id. Connect to /upload-progress/{upload_id}
    via SSE to receive real-time processing progress updates.
    """
    # Verify workspace exists and belongs to user
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace {workspace_id} not found"
        )

    # Generate upload ID for tracking
    upload_id = str(uuid4())

    if DEBUG:
        print(f'Upload ID: {upload_id}')
        print(f'Workspace ID: {workspace_id}')
        print(f'Number of files: {len(files)}')

    # Save files to persistent storage (single write, no temp files)
    saved_files = []
    filenames = []
    workspace_doc_dir = DOCUMENTS_DIR / workspace_id
    workspace_doc_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        try:
            file_content = await file.read()
            filenames.append(file.filename)

            # Write once to persistent storage (used for both preview and processing)
            persistent_path = workspace_doc_dir / file.filename
            with open(persistent_path, 'wb') as f:
                f.write(file_content)

            saved_files.append({
                "filename": file.filename,
                "file_path": str(persistent_path),
                "content_type": file.content_type,
            })
        except Exception as e:
            if DEBUG:
                print(f"Error saving {file.filename}: {str(e)}")
            # Continue with other files

    # Create progress tracker
    progress_manager.create_upload(upload_id, workspace_id, filenames)

    # Start background processing task
    asyncio.create_task(
        _process_files_with_progress(
            upload_id=upload_id,
            workspace_id=workspace_id,
            saved_files=saved_files,
            overwrite_index=overwrite_index,
            chroma_client=app.chroma_client,
        )
    )

    # Return immediately with upload_id
    return {
        "upload_id": upload_id,
        "workspace_id": workspace_id,
        "files": filenames,
        "total": len(filenames),
        "message": "Upload started. Connect to /upload-progress/{upload_id} for real-time updates."
    }


async def _process_files_with_progress(
    upload_id: str,
    workspace_id: str,
    saved_files: list,
    overwrite_index: bool,
    chroma_client,
):
    """
    Background task: three-phase parallel pipeline for document processing.
    Phase 1: Parse + chunk all files in parallel
    Phase 2: Embed ALL chunks in one batch (sentence-transformers optimizes internally)
    Phase 3: Store pre-embedded vectors into ChromaDB per-file
    """
    start_time = time.perf_counter()

    try:
        # --- Create all processors ---
        processors = []  # list of (filename, file_processor)
        for file_info in saved_files:
            filename = file_info["filename"]
            file_metadata = {"source": filename, "workspace_id": workspace_id}
            fp = FileProcessor.from_filetype(
                file_path=file_info["file_path"],
                file_type=file_info["content_type"],
                metadata=file_metadata
            )
            if not fp:
                await progress_manager.update_file_progress(
                    upload_id, filename, stage="error", progress=100,
                    error=f"Unsupported file type: {file_info['content_type']}"
                )
                continue
            processors.append((filename, fp))

        # --- PHASE 1: Parse + chunk all files in parallel ---
        async def parse_one(filename, fp):
            await progress_manager.update_file_progress(
                upload_id, filename, stage="chunking", progress=20
            )
            if overwrite_index:
                await asyncio.to_thread(delete_document, chroma_client, workspace_id, prefix=fp.document_prefix)
            splits = await asyncio.to_thread(fp._sync_get_tagged_splits, {})
            await progress_manager.update_file_progress(
                upload_id, filename, stage="chunking", progress=40
            )
            return splits

        parse_tasks = [parse_one(fn, fp) for fn, fp in processors]
        all_splits = await asyncio.gather(*parse_tasks, return_exceptions=True)

        # Collect valid results, mark failures
        valid = []  # (filename, fp, splits)
        for (filename, fp), splits in zip(processors, all_splits):
            if isinstance(splits, Exception):
                if DEBUG:
                    print(f"Error parsing {filename}: {splits}")
                await progress_manager.update_file_progress(
                    upload_id, filename, stage="error", progress=100, error=str(splits)
                )
                continue
            if not splits:
                await progress_manager.update_file_progress(
                    upload_id, filename, stage="error", progress=100, error="No content extracted"
                )
                continue
            valid.append((filename, fp, splits))

        if not valid:
            await progress_manager.mark_complete(upload_id)
            return

        # --- PHASE 2: Embed ALL chunks in one batch ---
        # Flatten all chunks and track boundaries per file
        all_documents = []
        file_boundaries = []  # (filename, fp, start_idx, end_idx)
        offset = 0
        for filename, fp, splits in valid:
            all_documents.extend(splits)
            file_boundaries.append((filename, fp, offset, offset + len(splits)))
            offset += len(splits)
            await progress_manager.update_file_progress(
                upload_id, filename, stage="embedding", progress=50
            )

        all_texts = [doc.page_content for doc in all_documents]
        EMBED_BATCH = 50  # Larger batches now safe with TOKENIZERS_PARALLELISM=false
        total_texts = len(all_texts)
        if DEBUG:
            print(f"Phase 2: Embedding {total_texts} chunks from {len(valid)} files in batches of {EMBED_BATCH}...")

        all_vectors = []
        for batch_start in range(0, total_texts, EMBED_BATCH):
            batch_end = min(batch_start + EMBED_BATCH, total_texts)
            batch_texts = all_texts[batch_start:batch_end]
            batch_vectors = await asyncio.to_thread(_sync_embed_texts, batch_texts, embedding_model)
            all_vectors.extend(batch_vectors)

            # Update progress for all files (50% to 85% range)
            pct = 50 + int(35 * len(all_vectors) / total_texts)
            for filename, fp, start, end in file_boundaries:
                await progress_manager.update_file_progress(
                    upload_id, filename, stage="embedding", progress=pct
                )
            await asyncio.sleep(0)  # yield to event loop

            if DEBUG:
                print(f"  Embedded batch {batch_start}-{batch_end} ({len(all_vectors)}/{total_texts})")

        if DEBUG:
            print(f"Phase 2 complete: {len(all_vectors)} embeddings computed")

        # --- PHASE 3: Store pre-embedded vectors into ChromaDB per-file ---
        collection = get_raw_collection(chroma_client, workspace_id)
        STORE_BATCH = 500

        for filename, fp, start, end in file_boundaries:
            docs_slice = all_documents[start:end]
            vecs_slice = all_vectors[start:end]

            for bs in range(0, len(docs_slice), STORE_BATCH):
                be = min(bs + STORE_BATCH, len(docs_slice))
                await asyncio.to_thread(
                    _sync_store_preembedded,
                    docs_slice[bs:be], vecs_slice[bs:be],
                    collection, fp.document_prefix
                )
                await asyncio.sleep(0)

            # Compute stats
            pages = set()
            for doc in docs_slice:
                if 'page' in doc.metadata:
                    pages.add(doc.metadata['page'])

            await progress_manager.update_file_progress(
                upload_id, filename, stage="complete", progress=100,
                pages=len(pages), chunks=len(docs_slice)
            )
            # NOTE: Do NOT call fp.cleanup() here — files are stored permanently
            # in DOCUMENTS_DIR for document viewing/preview in the frontend

    except Exception as e:
        if DEBUG:
            print(f"Pipeline error for upload {upload_id}: {e}")
        # Mark all remaining files as error
        for file_info in saved_files:
            try:
                await progress_manager.update_file_progress(
                    upload_id, file_info["filename"], stage="error", progress=100, error=str(e)
                )
            except Exception:
                pass

    # Mark upload as complete
    await progress_manager.mark_complete(upload_id)

    end_time = time.perf_counter()
    if DEBUG:
        print(f"Upload {upload_id} completed in {round(end_time - start_time, 3)}s")

    # Schedule cleanup after 5 minutes
    await asyncio.sleep(300)
    progress_manager.cleanup(upload_id)

@app.delete('/documents/{workspace_id}/{file_name}', tags=["documents"])
async def delete_document_from_workspace(
    workspace_id: str,
    file_name: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a specific document from a workspace
    """
    # Verify workspace exists and belongs to user
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace {workspace_id} not found"
        )

    # Create a simple prefix for the document
    doc_prefix = get_prefix(filename=file_name, plan_id=workspace_id)
    # deleted = delete_document(index=app.index_db, namespace=workspace_id, prefix=doc_prefix)  # PINECONE (OLD)
    deleted = delete_document(client=app.chroma_client, namespace=workspace_id, prefix=doc_prefix)  # CHROMADB (NEW)

    if deleted:
        # Also delete from file storage
        doc_path = DOCUMENTS_DIR / workspace_id / file_name
        if doc_path.exists():
            doc_path.unlink()
        return {
            'file_name': file_name,
            'workspace_id': workspace_id,
            'message': "deleted successfully"
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"{file_name} does not exist in workspace {workspace_id}"
        )


@app.get('/documents/{workspace_id}/{filename:path}', tags=["documents"])
async def get_document(
    workspace_id: str,
    filename: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get/download a document from a workspace for preview
    """
    # Verify workspace exists and belongs to user
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace {workspace_id} not found"
        )

    # Check if document exists in storage
    doc_path = DOCUMENTS_DIR / workspace_id / filename

    if not doc_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {filename} not found in workspace"
        )

    # Return the file
    return FileResponse(
        path=str(doc_path),
        filename=filename,
        media_type='application/pdf'
    )


@app.get('/workspaces/{workspace_id}/documents', tags=["documents"])
async def list_workspace_documents(
    workspace_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    List all documents in a workspace by querying Pinecone metadata
    """
    # Verify workspace exists and belongs to user
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace {workspace_id} not found"
        )

    try:
        # Query ChromaDB to get document metadata
        # PINECONE (OLD):
        # stats = app.index_db.describe_index_stats()
        # namespace_stats = stats.get('namespaces', {}).get(workspace_id, {})
        # vector_count = namespace_stats.get('vector_count', 0)

        # CHROMADB (NEW):
        try:
            collection = app.chroma_client.get_collection(workspace_id)
            vector_count = collection.count()
        except Exception:
            # Collection doesn't exist
            return []

        if vector_count == 0:
            return []

        # Get all documents from collection to extract metadata
        # PINECONE (OLD):
        # query_response = app.index_db.query(
        #     namespace=workspace_id,
        #     vector=[0.0] * 384,
        #     top_k=min(10000, vector_count),
        #     include_metadata=True
        # )

        # CHROMADB (NEW):
        query_response = collection.get(
            limit=min(10000, vector_count),
            include=['metadatas']
        )

        # Extract unique document names from metadata
        unique_docs = {}

        # PINECONE (OLD): for match in query_response.get('matches', []):
        # CHROMADB (NEW): iterate over metadatas
        for metadata in query_response.get('metadatas', []):
            # metadata = match.get('metadata', {})  # PINECONE (OLD)
            source = metadata.get('source')
            if source and source not in unique_docs:
                unique_docs[source] = {
                    'id': source,  # Use filename as ID
                    'filename': source,
                    'workspace_id': workspace_id,
                    'uploaded_at': workspace.created_at.isoformat(),  # Approximation
                }

        # Convert to list
        documents = list(unique_docs.values())

        if DEBUG:
            print(f"Found {len(documents)} unique documents in workspace {workspace_id}")

        return documents

    except Exception as e:
        if DEBUG: print(f"Error listing documents: {e}")
        # Return empty list if there's an error
        return []

# Note: All legacy insurance/financial endpoints have been removed.
# LitSynth is purely for academic research.

class Message(BaseModel):
    query: str
    chat_id: str  # CHANGED: chat_id instead of workspace_id

# CHAT HISTORY ENDPOINTS --------------------------

@app.post('/chat', tags=["chat"])
async def post_chat(
    message: Message,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send a message and get a response based on uploaded research papers.
    Chat history is automatically managed and persisted.
    """
    query = message.query
    chat_id = message.chat_id  # CHANGED: use chat_id

    if DEBUG:
        print(f'Query: {query}')
        print(f'Chat ID: {chat_id}')

    # Get chat and verify it exists
    chat = session.exec(select(Chat).where(Chat.chat_id == chat_id)).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Verify workspace exists and belongs to user
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == chat.workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get chat history for this chat (CHANGED: filter by chat_id instead of workspace_id)
    chat_messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at)
    ).all()

    # Check if this is the first message (for title generation)
    is_first_message = len(chat_messages) == 0

    # Format chat history for the LLM
    chat_history = ""
    for msg in chat_messages:
        chat_history += f"{msg.role}: {msg.content}\n"

    # Save user message (CHANGED: use chat_id)
    user_message = ChatMessage(
        chat_id=chat_id,
        workspace_id=chat.workspace_id,  # Still needed for migration compatibility
        role="user",
        content=query
    )
    session.add(user_message)
    session.commit()

    # Get relevant context and sources from vector store (UNCHANGED: uses workspace_id for document context)
    context, sources = await get_relevant_context(
        index=app.chroma_client,  # CHROMADB: client instead of index
        workspace_id=chat.workspace_id,  # Use workspace_id from chat for document context
        query=query,
        k=5
    )

    # Get full document list for this workspace (so LLM can answer "list all papers")
    all_doc_names = get_workspace_document_names(app.chroma_client, chat.workspace_id)
    document_list = "\n".join(f"- {name}" for name in all_doc_names) if all_doc_names else "(No documents uploaded yet)"

    # Get response from chat chain
    chat_chain = get_chat_chain()
    res = chat_chain.invoke({
        "context": context,
        "history": chat_history,
        "query": query,
        "document_list": document_list,
        "document_count": str(len(all_doc_names)),
    })

    # Save assistant response with sources (CHANGED: use chat_id)
    assistant_message = ChatMessage(
        chat_id=chat_id,
        workspace_id=chat.workspace_id,  # Still needed for migration compatibility
        role="assistant",
        content=res.content,
        sources=json.dumps(sources) if sources else None
    )
    session.add(assistant_message)

    # Update chat metadata (NEW)
    chat.updated_at = datetime.utcnow()
    chat.message_count += 2  # User + assistant

    # AUTO-GENERATE TITLE if first message
    if is_first_message:
        try:
            from chat import generate_chat_title, llm
            new_title = await generate_chat_title(query, llm)
            chat.title = new_title
            if DEBUG:
                print(f"CHAT: Auto-generated title: '{new_title}'")
        except Exception as e:
            if DEBUG:
                print(f"CHAT: Failed to generate title: {e}")
            # Keep existing title (Chat N)

    session.add(chat)

    session.commit()

    if DEBUG:
        print(f'Chat {chat_id} updated: message_count={chat.message_count}')

    return {
        'message': res.content,
        'sources': sources
    }

@app.get('/chat/{chat_id}/messages', tags=["chat"], response_model=list[ChatMessagePublic])
async def get_chat_history(
    chat_id: str,  # CHANGED: chat_id instead of workspace_id
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = Query(default=100, le=500)
):
    """
    Get chat history for a specific chat
    """
    # Verify chat access
    chat = session.exec(select(Chat).where(Chat.chat_id == chat_id)).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Verify workspace exists and belongs to user
    workspace = session.exec(
        select(Workspace)
        .where(Workspace.workspace_id == chat.workspace_id)
        .where(Workspace.user_id == user.id)
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get chat messages (CHANGED: filter by chat_id instead of workspace_id)
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at)
        .limit(limit)
    ).all()

    return messages

# Old DELETE /chat/{workspace_id} endpoint removed - use DELETE /chats/{chat_id} instead

@app.delete('/vectors', dependencies=[Depends(validate_admin)])
async def delete_all_vectors():
    # deleted = delete_all_namespace(app.index_db)  # PINECONE (OLD)
    deleted = delete_all_namespace(app.chroma_client)  # CHROMADB (NEW)
    return {'message': 'All vectors deleted successfully', 'deleted':deleted}
