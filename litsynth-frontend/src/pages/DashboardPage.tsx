import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { Workspace, CreateWorkspaceRequest } from '@/types';
import Layout from '@/components/Layout';
import Modal from '@/components/Modal';
import LoadingSpinner from '@/components/LoadingSpinner';
import { Plus, Folder, MessageSquare, Trash2, Calendar } from 'lucide-react';
import { format } from 'date-fns';

export default function DashboardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [_deleteWorkspaceId, setDeleteWorkspaceId] = useState<string | null>(null);
  const [formData, setFormData] = useState<CreateWorkspaceRequest>({
    name: '',
    description: '',
  });

  // Fetch workspaces
  const { data: workspaces, isLoading } = useQuery<Workspace[]>({
    queryKey: ['workspaces'],
    queryFn: () => apiService.getWorkspaces(),
  });

  // Create workspace mutation
  const createMutation = useMutation({
    mutationFn: (data: CreateWorkspaceRequest) => {
      console.log('Creating workspace with data:', data);
      return apiService.createWorkspace(data);
    },
    onSuccess: (data) => {
      console.log('Workspace created successfully:', data);
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      setIsCreateModalOpen(false);
      setFormData({ name: '', description: '' });
    },
    onError: (error: any) => {
      console.error('Failed to create workspace:', error);
      console.error('Error response:', error.response?.data);
    },
  });

  // Delete workspace mutation
  const deleteMutation = useMutation({
    mutationFn: (workspaceId: string) => apiService.deleteWorkspace(workspaceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      setDeleteWorkspaceId(null);
    },
  });

  const handleCreateWorkspace = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleDeleteWorkspace = (workspaceId: string) => {
    if (window.confirm('Are you sure you want to delete this workspace? This action cannot be undone.')) {
      deleteMutation.mutate(workspaceId);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Workspaces</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your research workspaces</p>
          </div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>New Workspace</span>
          </button>
        </div>

        {/* Workspaces Grid */}
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner size="lg" />
          </div>
        ) : workspaces && workspaces.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {workspaces.map((workspace) => (
              <div key={workspace.id} className="card group relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                      <Folder className="text-primary-600 dark:text-primary-500" size={24} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-gray-100">{workspace.name}</h3>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteWorkspace(workspace.workspace_id)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-400"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>

                <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">{workspace.description}</p>

                <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
                  <div className="flex items-center space-x-1">
                    <Calendar size={16} />
                    <span>{format(new Date(workspace.created_at), 'MMM dd, yyyy')}</span>
                  </div>
                </div>

                <button
                  onClick={() => navigate(`/workspace/${workspace.workspace_id}/chat`)}
                  className="w-full btn-primary flex items-center justify-center space-x-2"
                >
                  <MessageSquare size={18} />
                  <span>Open Chat</span>
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Folder className="mx-auto text-gray-400 dark:text-gray-500 mb-4" size={48} />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No workspaces yet</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">Create your first workspace to get started</p>
            <button onClick={() => setIsCreateModalOpen(true)} className="btn-primary">
              Create Workspace
            </button>
          </div>
        )}
      </div>

      {/* Create Workspace Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Workspace"
      >
        <form onSubmit={handleCreateWorkspace} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Workspace Name
            </label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input-field bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
              placeholder="e.g., Machine Learning Papers"
              required
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input-field bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
              rows={3}
              placeholder="Brief description of this workspace"
              required
            />
          </div>

          {createMutation.isError && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg text-sm">
              Failed to create workspace. Please try again.
            </div>
          )}

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(false)}
              className="flex-1 btn-secondary"
              disabled={createMutation.isPending}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 btn-primary disabled:opacity-50"
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? 'Creating...' : 'Create Workspace'}
            </button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
