import { FileUploadProgress } from '../types';
import Modal from './Modal';
import { Loader, Check, X, FileText, Upload, Cpu } from 'lucide-react';

interface UploadProgressModalProps {
  isOpen: boolean;
  onClose: () => void;
  files: FileUploadProgress[];
}

export default function UploadProgressModal({ isOpen, onClose, files }: UploadProgressModalProps) {
  const allComplete = files.every(f => f.status === 'success' || f.status === 'error');
  const successCount = files.filter(f => f.status === 'success').length;
  const errorCount = files.filter(f => f.status === 'error').length;
  const inProgress = files.filter(f => f.status === 'uploading' || f.status === 'processing').length;

  return (
    <Modal isOpen={isOpen} onClose={allComplete ? onClose : undefined} title="Document Upload Progress">
      <div className="space-y-4">
        {/* Summary Header */}
        <div className="flex items-center justify-between p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {allComplete ? 'Upload Complete' : 'Processing Documents...'}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {allComplete
                  ? `${successCount} successful, ${errorCount} failed`
                  : `${inProgress} in progress, ${files.length} total`
                }
              </p>
            </div>
          </div>
          {!allComplete && <Loader className="w-5 h-5 animate-spin text-primary-600 dark:text-primary-400" />}
        </div>

        {/* File list */}
        <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
          {files.map((file, idx) => (
            <div
              key={idx}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800 hover:border-primary-300 dark:hover:border-primary-700 transition-all"
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <StatusIcon status={file.status} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                      {file.filename}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {getStatusText(file.status, file.stage)}
                    </p>
                    {file.status === 'success' && (file.pages || file.chunks) && (
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                        {file.pages ? `${file.pages} pages` : ''}{file.pages && file.chunks ? ' · ' : ''}{file.chunks ? `${file.chunks} chunks` : ''}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Progress bar */}
              {(file.status === 'uploading' || file.status === 'processing') && (
                <div className="space-y-2">
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        file.status === 'uploading'
                          ? 'bg-blue-600 dark:bg-blue-500'
                          : 'bg-purple-600 dark:bg-purple-500'
                      }`}
                      style={{ width: `${file.progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>{file.progress}% complete</span>
                    <span>
                      {file.status === 'uploading' ? 'Uploading' : getStageLabel(file.stage)}
                    </span>
                  </div>
                </div>
              )}

              {/* Success message */}
              {file.status === 'success' && (
                <div className="flex items-center gap-2 text-xs text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-3 py-2 rounded border border-green-200 dark:border-green-800">
                  <Check className="w-3 h-3" />
                  <span>Document successfully uploaded and indexed</span>
                </div>
              )}

              {/* Error message */}
              {file.error && (
                <div className="flex items-start gap-2 text-xs text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-900/20 px-3 py-2 rounded border border-red-200 dark:border-red-800">
                  <X className="w-3 h-3 mt-0.5 flex-shrink-0" />
                  <span>{file.error}</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Actions */}
        {allComplete && (
          <div className="flex gap-3 pt-2">
            <button
              onClick={onClose}
              className="flex-1 py-2.5 px-4 bg-primary-600 hover:bg-primary-700 dark:bg-primary-700 dark:hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
            >
              Done
            </button>
          </div>
        )}

        {/* Warning for long processing */}
        {inProgress > 0 && (
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded border border-gray-200 dark:border-gray-700">
            Processing may take 1-3 minutes per document for OCR and vectorization
          </div>
        )}
      </div>
    </Modal>
  );
}

function getStatusText(status: FileUploadProgress['status'], stage?: FileUploadProgress['stage']): string {
  // If processing, show stage-specific message
  if (status === 'processing' && stage) {
    switch (stage) {
      case 'ocr':
        return 'Running OCR text extraction...';
      case 'chunking':
        return 'Splitting document into chunks...';
      case 'embedding':
        return 'Generating vector embeddings...';
      case 'indexing':
        return 'Indexing to vector database...';
      default:
        return 'Processing document...';
    }
  }

  switch (status) {
    case 'uploading':
      return 'Uploading file to server...';
    case 'processing':
      return 'Processing document...';
    case 'success':
      return 'Ready for chat';
    case 'error':
      return 'Processing failed';
  }
}

function getStageLabel(stage?: FileUploadProgress['stage']): string {
  switch (stage) {
    case 'ocr':
      return 'OCR';
    case 'chunking':
      return 'Chunking';
    case 'embedding':
      return 'Embedding';
    case 'indexing':
      return 'Indexing';
    default:
      return 'Processing';
  }
}

function StatusIcon({ status }: { status: FileUploadProgress['status'] }) {
  switch (status) {
    case 'uploading':
      return (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
          <Upload className="w-4 h-4 text-blue-600 dark:text-blue-400" />
        </div>
      );
    case 'processing':
      return (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
          <Cpu className="w-4 h-4 animate-pulse text-purple-600 dark:text-purple-400" />
        </div>
      );
    case 'success':
      return (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
          <Check className="w-4 h-4 text-green-600 dark:text-green-400" />
        </div>
      );
    case 'error':
      return (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
          <X className="w-4 h-4 text-red-600 dark:text-red-400" />
        </div>
      );
  }
}
