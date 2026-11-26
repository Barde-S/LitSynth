// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

// User Types
export interface User {
  id: number;
  email: string;
  is_verified: boolean;
  created_at: string;
}

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  otp_code: string;
}

export interface OTPRequest {
  email: string;
}

export interface OTPVerifyRequest {
  email: string;
  otp_code: string;
}

export interface OTPResponse {
  message: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

// Workspace Types
export interface Workspace {
  id: number;
  workspace_id: string;
  name: string;
  description: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  document_count?: number;
}

export interface CreateWorkspaceRequest {
  name: string;
  description: string;
}

// Chat Types (conversation threads within workspaces)
export interface Chat {
  id: number;
  chat_id: string;
  workspace_id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateChatRequest {
  title?: string;
}

export interface UpdateChatRequest {
  title: string;
}

// Document Types
export interface Document {
  id: string;
  filename: string;
  workspace_id: string;
  uploaded_at: string;
  file_size?: number;
  page_count?: number;
}

export interface UploadDocumentResponse {
  message: string;
  workspace_id: string;
  files_processed: number;
  indexed_results: any[];
  processing_time: number;
}

// Batch Upload Types
export interface UploadFileResult {
  filename: string;
  status: 'success' | 'error';
  pages: number;
  chunks: number;
  index: number;
  error: string | null;
}

export interface BatchUploadResponse {
  total: number;
  successful: number;
  failed: number;
  results: UploadFileResult[];
  workspace_id: string;
  processing_time: number;
}

export interface FileUploadProgress {
  filename: string;
  status: 'uploading' | 'processing' | 'success' | 'error';
  progress: number;
  error?: string;
  stage?: 'pending' | 'ocr' | 'chunking' | 'embedding' | 'indexing' | 'complete' | 'error';
  pages?: number;
  chunks?: number;
}

// New upload response (returns immediately with upload_id)
export interface UploadStartResponse {
  upload_id: string;
  workspace_id: string;
  files: string[];
  total: number;
  message: string;
}

// SSE progress update
export interface ProgressUpdate {
  upload_id: string;
  files: Record<string, {
    stage: 'pending' | 'ocr' | 'chunking' | 'embedding' | 'indexing' | 'complete' | 'error';
    progress: number;
    error?: string | null;
    pages?: number | null;
    chunks?: number | null;
  }>;
  completed: boolean;
}

// Chat Message Types
export interface ChatMessage {
  id: string;
  chat_id: string;  // NEW: Links message to chat
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[];
}

export interface Source {
  source: string;
  page: number | string;
  snippet: string;
  highlightText?: string;  // First 20 chars for text highlighting in PDF
}

export interface ChatRequest {
  query: string;
  history?: ChatMessage[];
}

export interface ChatResponse {
  message: string;
  sources: Source[];
}
