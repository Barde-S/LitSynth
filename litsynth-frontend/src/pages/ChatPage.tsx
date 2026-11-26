import { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { Chat, ChatMessage, Document, Workspace, CreateWorkspaceRequest, FileUploadProgress, Source } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import Modal from '@/components/Modal';
import UploadProgressModal from '@/components/UploadProgressModal';
import PDFViewer from '@/components/PDFViewer';
import ThemeToggle from '@/components/ThemeToggle';
import { ExportService, ExportFormat } from '@/services/exportService';
import {
  // File,
  // FileText,
  // Sparkles,
  Paperclip,
  // ArrowUp,
  X,
  LogOut,
  // Folder,
  // FolderOpen,
  // PenSquare,
  // Settings,
  User,
  Plus,
  // MessageSquare,
  Trash2,
  // Edit2,
  Send,
  // BookOpen,
  Menu,
  // ChevronLeft,
  // Upload,
  Download,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAuthStore } from '@/store/authStore';

export default function ChatPage() {
  const { workspaceId, chatId } = useParams<{ workspaceId: string; chatId?: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const logout = useAuthStore((state) => state.logout);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showDocumentPanel, setShowDocumentPanel] = useState(false);
  const [previewDocument, setPreviewDocument] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewPage, setPreviewPage] = useState<number>(1);
  const [highlightText, setHighlightText] = useState<string | undefined>(undefined);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [formData, setFormData] = useState<CreateWorkspaceRequest>({
    name: '',
    description: '',
  });
  const [uploadProgress, setUploadProgress] = useState<FileUploadProgress[]>([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Fetch all workspaces for sidebar
  const { data: workspaces } = useQuery<Workspace[]>({
    queryKey: ['workspaces'],
    queryFn: () => apiService.getWorkspaces(),
  });

  // Fetch current workspace details
  const { data: workspace } = useQuery({
    queryKey: ['workspace', workspaceId],
    queryFn: () => apiService.getWorkspace(workspaceId!),
    enabled: !!workspaceId,
  });

  // Fetch documents for current workspace
  const { data: documents } = useQuery<Document[]>({
    queryKey: ['documents', workspaceId],
    queryFn: () => apiService.getDocuments(workspaceId!),
    enabled: !!workspaceId,
  });

  // Fetch chats for current workspace
  const { data: chats, isLoading: chatsLoading } = useQuery<Chat[]>({
    queryKey: ['chats', workspaceId],
    queryFn: () => apiService.getChats(workspaceId!),
    enabled: !!workspaceId,
  });

  // Get current chat from chats array
  const currentChat = chats?.find(chat => chat.chat_id === chatId);

  // Fetch chat history for current chat
  const { data: chatHistory } = useQuery<ChatMessage[]>({
    queryKey: ['chatHistory', chatId],
    queryFn: () => apiService.getChatHistory(chatId!),
    enabled: !!chatId,
  });

  // Auto-navigate to first chat when workspace is loaded
  useEffect(() => {
    if (workspaceId && !chatId && chats && chats.length > 0) {
      navigate(`/workspace/${workspaceId}/chat/${chats[0].chat_id}`, { replace: true });
    }
  }, [workspaceId, chatId, chats, navigate]);

  // Load chat history into messages state
  useEffect(() => {
    if (chatHistory && chatHistory.length > 0) {
      const formattedMessages = chatHistory.map((msg: any) => ({
        id: msg.id?.toString() || Date.now().toString(),
        chat_id: msg.chat_id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.created_at,
        sources: msg.sources ? JSON.parse(msg.sources) : undefined,
      }));
      setMessages(formattedMessages);
    } else {
      setMessages([]);
    }
  }, [chatHistory, chatId]);

  // Create workspace mutation
  const createMutation = useMutation({
    mutationFn: (data: CreateWorkspaceRequest) => apiService.createWorkspace(data),
    onSuccess: async (data) => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      setIsCreateModalOpen(false);
      setFormData({ name: '', description: '' });

      // Fetch chats for new workspace to get the default chat
      const newChats = await apiService.getChats(data.workspace_id);
      if (newChats.length > 0) {
        navigate(`/workspace/${data.workspace_id}/chat/${newChats[0].chat_id}`);
      } else {
        navigate(`/workspace/${data.workspace_id}/chat`);
      }
    },
  });

  // Create chat mutation
  const createChatMutation = useMutation({
    mutationFn: () => apiService.createChat(workspaceId!),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['chats', workspaceId] });
      navigate(`/workspace/${workspaceId}/chat/${data.chat_id}`);
    },
  });

  // Delete chat mutation
  const deleteChatMutation = useMutation({
    mutationFn: (chatId: string) => apiService.deleteChat(chatId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chats', workspaceId] });
      navigate(`/workspace/${workspaceId}/chat`);
    },
  });

  // Send message mutation
  const chatMutation = useMutation({
    mutationFn: (query: string) => apiService.chat(chatId!, { query }),
    onSuccess: (data) => {
      const assistantMessage: ChatMessage = {
        id: Date.now().toString(),
        chat_id: chatId!,
        role: 'assistant',
        content: data.message,
        timestamp: new Date().toISOString(),
        sources: data.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      queryClient.invalidateQueries({ queryKey: ['chatHistory', chatId] });
      queryClient.invalidateQueries({ queryKey: ['chats', workspaceId] });
    },
  });

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: (filename: string) => apiService.deleteDocument(workspaceId!, filename),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', workspaceId] });
    },
  });

  // Delete workspace mutation
  const deleteWorkspaceMutation = useMutation({
    mutationFn: (workspaceId: string) => apiService.deleteWorkspace(workspaceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      // Navigate to home page after deletion
      navigate('/');
    },
  });

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !chatId) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      chat_id: chatId,
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    chatMutation.mutate(inputMessage.trim());
    setInputMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0 || !workspaceId) return;

    // Check if all files are PDFs
    const nonPdfFiles = files.filter(f => !f.name.endsWith('.pdf'));
    if (nonPdfFiles.length > 0) {
      setUploadError(`Only PDF files are supported. Found ${nonPdfFiles.length} non-PDF file(s).`);
      return;
    }

    // Initialize progress tracking
    const initialProgress: FileUploadProgress[] = files.map(f => ({
      filename: f.name,
      status: 'uploading',
      progress: 0,
      stage: 'pending'
    }));
    setUploadProgress(initialProgress);
    setShowUploadModal(true);
    setIsUploading(true);
    setUploadError('');

    let cleanupSSE: (() => void) | null = null;

    try {
      // Create FormData with all files
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      // Phase 1: Upload files with progress tracking
      const response = await apiService.uploadDocuments(
        workspaceId,
        formData,
        (uploadPercent) => {
          // Update progress for all files during upload phase (0-20% of total)
          setUploadProgress(prev => prev.map(p => ({
            ...p,
            progress: Math.round(uploadPercent * 0.2),
            status: 'uploading',
            stage: 'pending'
          })));
        }
      );

      // Phase 2: Subscribe to SSE for processing progress
      cleanupSSE = apiService.subscribeToUploadProgress(
        response.upload_id,
        // onProgress
        (update) => {
          setUploadProgress(prev => prev.map(p => {
            const fileUpdate = update.files[p.filename];
            if (!fileUpdate) return p;

            // Map stage to overall progress percentage
            const stageProgress: Record<string, number> = {
              pending: 20,
              ocr: 35,
              chunking: 50,
              embedding: 65,
              indexing: 85,
              complete: 100,
              error: 100
            };

            return {
              ...p,
              status: fileUpdate.stage === 'complete' ? 'success'
                    : fileUpdate.stage === 'error' ? 'error'
                    : 'processing',
              progress: stageProgress[fileUpdate.stage] || fileUpdate.progress || p.progress,
              stage: fileUpdate.stage,
              error: fileUpdate.error || undefined,
              pages: fileUpdate.pages || p.pages,
              chunks: fileUpdate.chunks || p.chunks
            };
          }));
        },
        // onComplete
        () => {
          setIsUploading(false);
          queryClient.invalidateQueries({ queryKey: ['documents', workspaceId] });

          // Check if all files succeeded
          setUploadProgress(prev => {
            const allSuccess = prev.every(p => p.status === 'success');
            if (allSuccess) {
              setTimeout(() => setShowUploadModal(false), 3000);
            }
            return prev;
          });
        },
        // onError
        (error) => {
          console.error('SSE error:', error);
          setUploadError('Lost connection to server during processing. Files may still be processing.');
          setIsUploading(false);
        }
      );

    } catch (error) {
      // Mark all as failed
      setUploadProgress(prev => prev.map(p => ({
        ...p,
        status: 'error',
        error: 'Upload failed'
      })));
      setUploadError('Failed to upload documents. Please try again.');
      setIsUploading(false);
      if (cleanupSSE) cleanupSSE();
    } finally {
      // Reset input
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleCreateWorkspace = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputMessage(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  const handleOpenSource = (filename: string, page: number, highlightStr?: string) => {
    setPreviewDocument(filename);
    setPreviewPage(page);
    setHighlightText(highlightStr);
    setShowDocumentPanel(false); // Close document list panel if open
  };

  const handleExport = async (format: ExportFormat) => {
    if (!currentChat || !messages) return;

    try {
      await ExportService.exportChat(
        currentChat,
        messages,
        format,
        workspace?.name
      );
      setShowExportMenu(false);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export chat. Please try again.');
    }
  };

  // Component to render message content with clickable inline citations
  const MessageContent = ({ content, sources }: { content: string; sources?: Source[] }) => {
    // Replace citation patterns with placeholders, render markdown, then replace back
    const citationRegex = /\[p\.(\d+(?:-\d+)?),\s*([^\]]+)\]/g;
    const citations: Array<{ pageStr: string; filename: string }> = [];

    // Extract citations and replace with unique markers
    const contentWithMarkers = content.replace(citationRegex, (_match, pageStr, filename) => {
      const index = citations.length;
      citations.push({ pageStr, filename: filename.trim() });
      return `{{CITATION_${index}}}`;
    });

    // Render markdown
    const markdownElements: JSX.Element[] = [];
    let key = 0;

    // Split by citation markers
    const parts = contentWithMarkers.split(/({{CITATION_\d+}})/g);

    parts.forEach((part, _idx) => {
      const citationMatch = part.match(/{{CITATION_(\d+)}}/);

      if (citationMatch) {
        // This is a citation marker
        const citationIndex = parseInt(citationMatch[1]);
        const citation = citations[citationIndex];
        const pageNum = parseInt(citation.pageStr.split('-')[0]);

        // Find matching source to get highlightText (tolerant matching)
        const matchingSource = sources?.find(
          s => s.source.trim().toLowerCase() === citation.filename.trim().toLowerCase()
            && String(s.page) === String(pageNum)
        )
        // Fallback: same document, adjacent page (chunk may straddle page boundary)
        || sources?.find(
          s => s.source.trim().toLowerCase() === citation.filename.trim().toLowerCase()
            && (String(s.page) === String(pageNum - 1) || String(s.page) === String(pageNum + 1))
        )
        // Last resort: any source from the same document
        || sources?.find(
          s => s.source.trim().toLowerCase() === citation.filename.trim().toLowerCase()
        );

        markdownElements.push(
          <button
            key={`citation-${key++}`}
            onClick={() => handleOpenSource(citation.filename, pageNum, matchingSource?.highlightText)}
            className="inline text-gray-600 hover:text-blue-600 hover:bg-blue-50 hover:border-blue-200 border border-transparent px-1 py-0.5 rounded cursor-pointer transition-all hover:underline"
            title={`Open ${citation.filename} at page ${pageNum}`}
          >
            [p.{citation.pageStr}, {citation.filename}]
          </button>
        );
      } else if (part) {
        // This is regular text - render as inline markdown
        markdownElements.push(
          <span key={`text-${key++}`} className="inline">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <span>{children}</span>,
                // Keep other elements inline where possible
              }}
            >
              {part}
            </ReactMarkdown>
          </span>
        );
      }
    });

    return <>{markdownElements}</>;
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load document for preview
  useEffect(() => {
    if (previewDocument && workspaceId) {
      setIsLoadingPreview(true);
      apiService.getDocumentBlob(workspaceId, previewDocument)
        .then((blob) => {
          const url = URL.createObjectURL(blob);
          setPreviewUrl(url);
        })
        .catch((err) => {
          console.error('Failed to load document:', err);
          setPreviewDocument(null);
        })
        .finally(() => {
          setIsLoadingPreview(false);
        });
    } else {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
        setPreviewUrl(null);
      }
    }
  }, [previewDocument, workspaceId]);

  return (
    <div className="h-screen flex bg-white dark:bg-gray-900">
      {/* Sidebar */}
      {showSidebar && (
        <div className="w-56 flex flex-col bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
          {/* Header */}
          <div className="p-4">
            <h1 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-3">LitSynth</h1>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="w-full py-2 px-3 bg-black hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 text-white text-sm rounded-md"
            >
              New Workspace
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto px-3 pb-3">
            {/* Workspaces */}
            <div className="mb-4">
              <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 px-2">
                WORKSPACES
              </div>
              {workspaces && workspaces.length > 0 ? (
                <div className="space-y-0.5">
                  {workspaces.map((ws) => (
                    <div
                      key={ws.workspace_id}
                      className={`group flex items-center justify-between px-2 py-1.5 rounded text-sm ${
                        ws.workspace_id === workspaceId
                          ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 font-medium'
                          : 'text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
                      }`}
                    >
                      <button
                        onClick={() => navigate(`/workspace/${ws.workspace_id}/chat`)}
                        className="flex-1 text-left truncate"
                      >
                        {ws.name}
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (window.confirm(`Delete workspace "${ws.name}"? This will delete all chats and messages in this workspace.`)) {
                            deleteWorkspaceMutation.mutate(ws.workspace_id);
                          }
                        }}
                        className="opacity-0 group-hover:opacity-100 p-0.5 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-500"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4 text-gray-400 dark:text-gray-500 text-xs">
                  No workspaces
                </div>
              )}
            </div>

            {/* Chats */}
            {workspaceId && (
              <div>
                <div className="flex items-center justify-between mb-2 px-2">
                  <div className="text-xs font-medium text-gray-500 dark:text-gray-400">
                    CHATS
                  </div>
                  <button
                    onClick={() => createChatMutation.mutate()}
                    disabled={createChatMutation.isPending}
                    className="p-0.5 text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                  >
                    <Plus size={14} />
                  </button>
                </div>
                {chatsLoading ? (
                  <div className="flex justify-center py-4">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : chats && chats.length > 0 ? (
                  <div className="space-y-0.5">
                    {chats.map((chat) => (
                      <div
                        key={chat.chat_id}
                        className={`group flex items-center justify-between px-2 py-1.5 rounded text-sm ${
                          chat.chat_id === chatId
                            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 font-medium'
                            : 'text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
                        }`}
                      >
                        <button
                          onClick={() => navigate(`/workspace/${workspaceId}/chat/${chat.chat_id}`)}
                          className="flex-1 text-left truncate"
                        >
                          {chat.title}
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (window.confirm(`Delete chat "${chat.title}"? This will delete all messages in this chat.`)) {
                              deleteChatMutation.mutate(chat.chat_id);
                            }
                          }}
                          className="opacity-0 group-hover:opacity-100 p-0.5 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-500"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-400 dark:text-gray-500 text-xs">
                    No chats
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-3 space-y-2 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Theme</span>
              <ThemeToggle />
            </div>
            <button
              onClick={() => navigate('/profile')}
              className="flex items-center space-x-2 w-full px-2 py-1.5 rounded hover:bg-white dark:hover:bg-gray-700 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
            >
              <User size={14} />
              <span>Profile</span>
            </button>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 w-full px-2 py-1.5 rounded hover:bg-white dark:hover:bg-gray-700 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
            >
              <LogOut size={14} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="h-12 flex items-center justify-between pl-3 pr-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <Menu size={16} />
            </button>
            {workspace && (
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{workspace.name}</span>
            )}
          </div>

          {workspaceId && (
            <div className="flex items-center space-x-2">
              {/* Export Chat Button */}
              {currentChat && messages.length > 0 && (
                <div className="relative">
                  <button
                    onClick={() => setShowExportMenu(!showExportMenu)}
                    className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
                    title="Export chat"
                  >
                    <Download size={16} />
                  </button>

                  {showExportMenu && (
                    <>
                      <div
                        className="fixed inset-0 z-10"
                        onClick={() => setShowExportMenu(false)}
                      />
                      <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-20">
                        <div className="py-1">
                          <button
                            onClick={() => handleExport('markdown')}
                            className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
                          >
                            Export as Markdown
                          </button>
                          <button
                            onClick={() => handleExport('json')}
                            className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
                          >
                            Export as JSON
                          </button>
                          <button
                            onClick={() => handleExport('txt')}
                            className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
                          >
                            Export as Text
                          </button>
                          <button
                            onClick={() => handleExport('pdf')}
                            className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
                          >
                            Export as PDF
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}

              {documents && documents.length > 0 && (
                <button
                  onClick={() => setShowDocumentPanel(!showDocumentPanel)}
                  className="px-2 py-1 text-xs text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700 rounded"
                >
                  {documents.length} doc{documents.length !== 1 ? 's' : ''}
                </button>
              )}
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-white dark:bg-gray-900">
          {!workspaceId ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">
                <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Welcome to LitSynth</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  Your research assistant for academic papers
                </p>
                <button
                  onClick={() => setIsCreateModalOpen(true)}
                  className="px-4 py-2 bg-black hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 text-white text-sm rounded-md"
                >
                  Create Workspace
                </button>
              </div>
            </div>
          ) : !chatId ? (
            <div className="h-full flex items-center justify-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Select a chat or create a new one</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Ask anything about your documents</p>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto py-6 pl-3 pr-4">
              {messages.map((message) => (
                <div key={message.id} className="mb-6">
                  {message.role === 'user' ? (
                    <div className="flex justify-end">
                      <div className="bg-black dark:bg-gray-700 text-white px-3 py-2 rounded-lg max-w-[80%] text-sm">
                        {message.content}
                      </div>
                    </div>
                  ) : (
                    <div className="prose prose-sm max-w-none text-gray-700 dark:text-gray-300 text-sm">
                      <MessageContent content={message.content} sources={message.sources} />
                    </div>
                  )}
                </div>
              ))}
              {chatMutation.isPending && (
                <div className="mb-6">
                  <LoadingSpinner size="sm" />
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        {chatId && (
          <div className="py-4 pl-3 pr-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
            <div className="max-w-4xl mx-auto">
              {uploadError && (
                <div className="mb-2 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 px-2 py-1.5 rounded">
                  {uploadError}
                </div>
              )}
              {isUploading && (
                <div className="mb-2 text-xs text-gray-600 dark:text-gray-400 flex items-center space-x-1.5">
                  <LoadingSpinner size="sm" />
                  <span>Uploading...</span>
                </div>
              )}
              <div className="flex items-end gap-2">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                  title="Upload PDF"
                >
                  <Paperclip size={18} />
                </button>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".pdf"
                  multiple
                  className="hidden"
                />
                <div className="flex-1 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus-within:border-gray-400 dark:focus-within:border-gray-500">
                  <textarea
                    ref={textareaRef}
                    value={inputMessage}
                    onChange={handleTextareaChange}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    placeholder="Message..."
                    className="w-full px-3 py-2 resize-none outline-none bg-transparent text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                    rows={1}
                    disabled={chatMutation.isPending}
                  />
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || chatMutation.isPending}
                  className="p-2 bg-black hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 disabled:bg-gray-200 dark:disabled:bg-gray-800 text-white rounded-lg"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Documents Panel */}
      {showDocumentPanel && workspaceId && (
        <div className="w-64 flex flex-col bg-gray-50 dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700">
          <div className="p-3 flex items-center justify-between border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">Documents</h3>
            <button
              onClick={() => setShowDocumentPanel(false)}
              className="p-1 text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              <X size={16} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto px-3 pb-3">
            {documents && documents.length > 0 ? (
              <div className="space-y-1.5">
                {documents.map((doc) => (
                  <div
                    key={doc.filename}
                    className="group bg-white dark:bg-gray-700 p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-600"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-gray-900 dark:text-gray-100 truncate">
                          {doc.filename}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                          {new Date(doc.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={() => {
                          if (window.confirm(`Delete document "${doc.filename}"? This will remove it from the workspace.`)) {
                            deleteMutation.mutate(doc.filename);
                          }
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-500"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400 dark:text-gray-500 text-xs">
                No documents
              </div>
            )}
          </div>
        </div>
      )}

      {/* PDF Preview Modal */}
      {previewDocument && previewUrl && (
        <Modal
          isOpen={true}
          onClose={() => {
            setPreviewDocument(null);
            setPreviewPage(1);
            setHighlightText(undefined);
          }}
          className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-5xl w-full mx-4 h-[90vh] flex flex-col"
          hideHeader={true}
        >
          <div className="p-3 flex items-center justify-between border-b dark:border-gray-700">
            <h2 className="text-sm font-medium text-gray-900 dark:text-gray-100">{previewDocument} • Page {previewPage}</h2>
            <button
              onClick={() => {
                setPreviewDocument(null);
                setPreviewPage(1);
                setHighlightText(undefined);
              }}
              className="p-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
            >
              <X size={18} />
            </button>
          </div>
          <div className="flex-1 overflow-hidden">
            {isLoadingPreview ? (
              <div className="flex items-center justify-center h-full">
                <LoadingSpinner />
              </div>
            ) : (
              <PDFViewer
                url={previewUrl}
                initialPage={previewPage}
                highlightText={highlightText}
              />
            )}
          </div>
        </Modal>
      )}

      {/* Upload Progress Modal */}
      <UploadProgressModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        files={uploadProgress}
      />

      {/* Create Workspace Modal */}
      <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Create Workspace">
          <form onSubmit={handleCreateWorkspace} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-md focus:ring-1 focus:ring-black focus:border-black outline-none"
                placeholder="Machine Learning Research"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-md focus:ring-1 focus:ring-black focus:border-black outline-none resize-none"
                placeholder="Papers on ML and AI"
                rows={3}
              />
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setIsCreateModalOpen(false)}
                className="px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 rounded-md"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-3 py-1.5 bg-black hover:bg-gray-800 disabled:bg-gray-200 text-white text-sm rounded-md"
              >
                Create
              </button>
            </div>
          </form>
      </Modal>
    </div>
  );
}
