import { useEffect, useState, useCallback } from 'react';
import type { Application } from './types';
import { getApplications, createApplication, updateApplication, deleteApplication, getAuthStatus, getAuthUrl } from './api';
import { ApplicationTable } from './components/ApplicationTable';
import { AddEditModal } from './components/AddEditModal';
import { SyncButton } from './components/SyncButton';
import './index.css';

export default function App() {
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [gmailConnected, setGmailConnected] = useState<boolean | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Application | null>(null);

  const loadApps = useCallback(async () => {
    try {
      const data = await getApplications();
      setApps(data);
    } catch {
      setError('Failed to load applications. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadApps();
    getAuthStatus().then(s => setGmailConnected(s.connected)).catch(() => setGmailConnected(false));

    const params = new URLSearchParams(window.location.search);
    if (params.get('auth') === 'success') {
      setGmailConnected(true);
      window.history.replaceState({}, '', '/');
    }
  }, [loadApps]);

  async function handleConnectGmail() {
    try {
      const url = await getAuthUrl();
      window.location.href = url;
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Could not connect to Gmail');
    }
  }

  function openAdd() {
    setEditTarget(null);
    setModalOpen(true);
  }

  function openEdit(app: Application) {
    setEditTarget(app);
    setModalOpen(true);
  }

  async function handleSave(data: Partial<Application>) {
    if (editTarget) {
      await updateApplication(editTarget.id, data);
    } else {
      await createApplication(data as Parameters<typeof createApplication>[0]);
    }
    await loadApps();
  }

  async function handleDelete(id: number) {
    await deleteApplication(id);
    setApps(prev => prev.filter(a => a.id !== id));
  }

  const stats = {
    total: apps.length,
    interviewing: apps.filter(a => a.status === 'Interviewing').length,
    offers: apps.filter(a => a.status === 'Offer Received').length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 m-0">Job Application Tracker</h1>
            <p className="text-sm text-gray-500 mt-1">
              {stats.total} total · {stats.interviewing} interviewing · {stats.offers} offer{stats.offers !== 1 ? 's' : ''}
            </p>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            {gmailConnected === false && (
              <button
                onClick={handleConnectGmail}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-lg hover:bg-red-600 transition-colors"
              >
                Connect Gmail
              </button>
            )}
            {gmailConnected === true && (
              <SyncButton onDone={loadApps} />
            )}
            <button
              onClick={openAdd}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gray-800 rounded-lg hover:bg-gray-900 transition-colors"
            >
              + Add
            </button>
          </div>
        </div>

        {/* Gmail notice */}
        {gmailConnected === false && (
          <div className="mb-6 bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
            <strong>Gmail not connected.</strong> Click "Connect Gmail" to authorize access. Make sure{' '}
            <code className="bg-amber-100 px-1 rounded">backend/credentials.json</code> exists first (download from Google Cloud Console).
          </div>
        )}

        {/* Content */}
        {loading ? (
          <div className="flex justify-center py-20 text-gray-400 text-sm">Loading…</div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>
        ) : (
          <ApplicationTable applications={apps} onEdit={openEdit} onDelete={handleDelete} />
        )}
      </div>

      {modalOpen && (
        <AddEditModal
          initial={editTarget}
          onSave={handleSave}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  );
}
