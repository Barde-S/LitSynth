import { useAuthStore } from '@/store/authStore';
import Layout from '@/components/Layout';
import { User, Mail, Calendar } from 'lucide-react';
import { format } from 'date-fns';

export default function ProfilePage() {
  const user = useAuthStore((state) => state.user);

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Profile Settings</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your account settings and preferences</p>
        </div>

        {/* User Profile Section */}
        <div className="card bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
              <User className="text-primary-600 dark:text-primary-500" size={24} />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Account Information</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">Your personal account details</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center space-x-3 py-3 border-b border-gray-200 dark:border-gray-700">
              <Mail className="text-gray-400 dark:text-gray-500" size={20} />
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Email</p>
                <p className="font-medium text-gray-900 dark:text-gray-100">{user?.email || 'Not available'}</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 py-3">
              <Calendar className="text-gray-400 dark:text-gray-500" size={20} />
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Account Created</p>
                <p className="font-medium text-gray-900 dark:text-gray-100">
                  {user?.created_at
                    ? format(new Date(user.created_at), 'MMMM dd, yyyy')
                    : 'Not available'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* API Information */}
        <div className="card bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">API Information</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between py-2 border-b border-gray-200 dark:border-gray-700">
              <span className="text-gray-600 dark:text-gray-400">API Base URL</span>
              <span className="font-mono text-gray-900 dark:text-gray-100">http://localhost:8000</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-200 dark:border-gray-700">
              <span className="text-gray-600 dark:text-gray-400">Authentication</span>
              <span className="font-mono text-gray-900 dark:text-gray-100">JWT Bearer Token</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-gray-600 dark:text-gray-400">Documentation</span>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 dark:text-primary-500 hover:text-primary-700 dark:hover:text-primary-400 underline"
              >
                View API Docs
              </a>
            </div>
          </div>
        </div>

        {/* About LitSynth */}
        <div className="card bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">About LitSynth</h2>
          <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
            <p>
              LitSynth is an intelligent research assistant that helps you analyze and understand
              academic papers. Upload your research documents, ask questions, and get insights
              backed by citations.
            </p>
            <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Features:</h3>
              <ul className="list-disc list-inside space-y-1">
                <li>Upload and organize research papers in workspaces</li>
                <li>Chat with AI about your documents</li>
                <li>Get answers with source citations</li>
                <li>Manage multiple research projects</li>
              </ul>
            </div>
          </div>
        </div>

        {/* System Information */}
        <div className="card bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">System Information</h3>
          <div className="grid grid-cols-2 gap-4 text-xs text-gray-600 dark:text-gray-400">
            <div>
              <p className="font-medium">Version</p>
              <p className="text-gray-900 dark:text-gray-100">1.0.0</p>
            </div>
            <div>
              <p className="font-medium">LLM Provider</p>
              <p className="text-gray-900 dark:text-gray-100">Google Gemini 2.0 Flash</p>
            </div>
            <div>
              <p className="font-medium">Embedding Model</p>
              <p className="text-gray-900 dark:text-gray-100">nomic-embed-text-v1.5</p>
            </div>
            <div>
              <p className="font-medium">Vector Database</p>
              <p className="text-gray-900 dark:text-gray-100">ChromaDB</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
