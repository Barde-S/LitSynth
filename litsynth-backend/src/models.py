from __future__ import annotations
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional


# User Models
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field()
    is_verified: bool = Field(default=False)  # Email verification status
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(SQLModel):
    email: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserPublic(UserBase):
    id: int
    is_verified: bool
    created_at: datetime


# OTP Models
class OTP(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    otp_code: str = Field()
    purpose: str = Field()  # 'registration' or 'password_reset'
    expires_at: datetime = Field()
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OTPRequest(SQLModel):
    email: str

class OTPVerify(SQLModel):
    email: str
    otp_code: str

class RegisterWithOTP(SQLModel):
    email: str
    password: str
    otp_code: str


# Workspace Models
class WorkspaceBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None

class Workspace(WorkspaceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)  # Links workspace to user
    workspace_id: str = Field(unique=True, index=True)  # UUID for pinecone namespace
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkspaceCreate(SQLModel):
    name: str
    description: Optional[str] = None

class WorkspacePublic(WorkspaceBase):
    id: int
    user_id: int
    workspace_id: str
    created_at: datetime
    updated_at: datetime


# Chat Models (conversation threads within workspaces)
class ChatBase(SQLModel):
    title: str = Field(default="New Chat")
    workspace_id: str = Field(index=True)  # Links chat to workspace
    chat_id: str = Field(unique=True, index=True)  # UUID for chat

class Chat(ChatBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0)  # Cached count for performance

class ChatPublic(ChatBase):
    id: int
    created_at: datetime
    updated_at: datetime
    message_count: int


# Chat History Models (messages within chats)
class ChatMessageBase(SQLModel):
    # Migration-friendly: both fields optional temporarily
    # After migration complete, chat_id will be required and workspace_id removed
    chat_id: Optional[str] = Field(default=None, index=True)  # Links message to chat (NEW)
    workspace_id: Optional[str] = Field(default=None, index=True)  # OLD field, for migration
    role: str = Field()  # 'user' or 'assistant'
    content: str = Field()
    sources: Optional[str] = None  # JSON string with citation sources

class ChatMessage(ChatMessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessagePublic(ChatMessageBase):
    id: int
    created_at: datetime
