import axios, { AxiosInstance } from 'axios';
import {
  Workspace,
  CreateWorkspaceRequest,
  Chat,
  CreateChatRequest,
  UpdateChatRequest,
  Document,
  UploadDocumentResponse,
  ChatRequest,
  ChatResponse,
  ChatMessage,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  OTPRequest,
  OTPVerifyRequest,
  OTPResponse,
} from '@/types';
import { useAuthStore } from '@/store/authStore';

// Use environment variable for API base URL
// Falls back to localhost for development if not set
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Attach token from auth store on every request
    this.client.interceptors.request.use((config) => {
      const { token } = useAuthStore.getState();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Auto-logout on 401 (expired/invalid token)
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          useAuthStore.getState().logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // OTP APIs
  async sendOTP(data: OTPRequest): Promise<OTPResponse> {
    const response = await this.client.post<OTPResponse>('/auth/send-otp', data);
    return response.data;
  }

  async verifyOTP(data: OTPVerifyRequest): Promise<{ message: string; valid: boolean }> {
    const response = await this.client.post<{ message: string; valid: boolean }>('/auth/verify-otp', data);
    return response.data;
  }

  // Auth APIs
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', data);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register', data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // Workspace APIs
  async getWorkspaces(): Promise<Workspace[]> {
    const response = await this.client.get<Workspace[]>('/workspaces/');
    return response.data;
  }

  async getWorkspace(workspaceId: string): Promise<Workspace> {
    const response = await this.client.get<Workspace>(`/workspaces/${workspaceId}`);
    return response.data;
  }

  async createWorkspace(data: CreateWorkspaceRequest): Promise<Workspace> {
    const response = await this.client.post<Workspace>('/workspaces/', data);
    return response.data;
  }

  async deleteWorkspace(workspaceId: string): Promise<void> {
    await this.client.delete(`/workspaces/${workspaceId}`);
  }

  // Chat CRUD APIs (conversation threads within workspaces)
  async createChat(
    workspaceId: string,
    data?: CreateChatRequest
  ): Promise<Chat> {
    const response = await this.client.post<Chat>(
      `/workspaces/${workspaceId}/chats`,
      data
    );
    return response.data;
  }

  async getChats(workspaceId: string): Promise<Chat[]> {
    const response = await this.client.get<Chat[]>(
      `/workspaces/${workspaceId}/chats`
    );
    return response.data;
  }

  async getChat(chatId: string): Promise<Chat> {
    const response = await this.client.get<Chat>(`/chats/${chatId}`);
    return response.data;
  }

  async updateChat(
    chatId: string,
    data: UpdateChatRequest
  ): Promise<Chat> {
    const response = await this.client.patch<Chat>(
      `/chats/${chatId}`,
      data
    );
    return response.data;
  }

  async deleteChat(chatId: string): Promise<void> {
    await this.client.delete(`/chats/${chatId}`);
  }

  // Document APIs
  async getDocuments(workspaceId: string): Promise<Document[]> {
    const response = await this.client.get<Document[]>(`/workspaces/${workspaceId}/documents`);
    return response.data;
  }

  async uploadDocument(workspaceId: string, file: File): Promise<UploadDocumentResponse> {
    const formData = new FormData();
    formData.append('files', file);

    const response = await this.client.post<UploadDocumentResponse>(
      `/upload-papers?workspace_id=${workspaceId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async uploadDocuments(
    workspaceId: string,
    formData: FormData,
    onUploadProgress?: (progress: number) => void
  ): Promise<import('../types').UploadStartResponse> {
    const response = await this.client.post<import('../types').UploadStartResponse>(
      `/upload-papers?workspace_id=${workspaceId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes for file uploads
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onUploadProgress) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onUploadProgress(percentCompleted);
          }
        },
      }
    );
    return response.data;
  }

  /**
   * Subscribe to upload processing progress via Server-Sent Events.
   * Returns a cleanup function to close the connection.
   */
  subscribeToUploadProgress(
    uploadId: string,
    onProgress: (update: import('../types').ProgressUpdate) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): () => void {
    const { token: authToken } = useAuthStore.getState();
    const token = authToken ? `Bearer ${authToken}` : '';
    const url = `${API_BASE_URL}/upload-progress/${uploadId}`;

    let abortController: AbortController | null = new AbortController();

    const fetchSSE = async () => {
      try {
        const response = await fetch(url, {
          headers: {
            'Authorization': token,
            'Accept': 'text/event-stream',
          },
          signal: abortController?.signal,
        });

        if (!response.ok) {
          throw new Error(`SSE connection failed: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('Response body is not readable');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                onProgress(data);
                if (data.completed) {
                  onComplete();
                  return;
                }
              } catch {
                // Ignore parse errors for keepalive comments
              }
            }
          }
        }
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          onError(error);
        }
      }
    };

    fetchSSE();

    // Return cleanup function
    return () => {
      if (abortController) {
        abortController.abort();
        abortController = null;
      }
    };
  }

  async deleteDocument(workspaceId: string, filename: string): Promise<void> {
    await this.client.delete(`/documents/${workspaceId}/${filename}`);
  }

  getDocumentUrl(workspaceId: string, filename: string): string {
    return `${API_BASE_URL}/documents/${workspaceId}/${encodeURIComponent(filename)}`;
  }

  async getDocumentBlob(workspaceId: string, filename: string): Promise<Blob> {
    const response = await this.client.get(
      `/documents/${workspaceId}/${encodeURIComponent(filename)}`,
      { responseType: 'blob' }
    );
    return response.data;
  }

  // Chat Message APIs
  async chat(chatId: string, data: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>(
      '/chat',
      {
        query: data.query,
        chat_id: chatId,
      },
      {
        timeout: 120000, // 2 minutes for LLM responses
      }
    );
    return response.data;
  }

  async getChatHistory(chatId: string): Promise<ChatMessage[]> {
    const response = await this.client.get<ChatMessage[]>(`/chat/${chatId}/messages`);  // CHANGED: endpoint path
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get<{ status: string }>('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
