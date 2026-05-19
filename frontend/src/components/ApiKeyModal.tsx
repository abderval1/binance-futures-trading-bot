import { useState } from 'react';
import { useApiKeysStore } from '@/store';
import Button from '@/components/ui/Button';
import type { APIKey } from '@/types';

interface ApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ApiKeyModal({ isOpen, onClose }: ApiKeyModalProps) {
  const { addKey } = useApiKeysStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    label: '',
    api_key: '',
    secret_key: '',
    leverage: 20,
    margin_type: 'ISOLATED' as 'ISOLATED' | 'CROSS',
    testnet: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await addKey(form as APIKey);
      onClose();
      // reset form
      setForm({
        label: '',
        api_key: '',
        secret_key: '',
        leverage: 20,
        margin_type: 'ISOLATED',
        testnet: false,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add API key');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Add API Key</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            &times;
          </button>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Label</label>
            <input
              type="text"
              required
              value={form.label}
              onChange={(e) => setForm({ ...form, label: e.target.value })}
              placeholder="My Binance Account"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">API Key</label>
            <input
              type="text"
              required
              value={form.api_key}
              onChange={(e) => setForm({ ...form, api_key: e.target.value })}
              className="w-full border rounded px-3 py-2 font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Secret Key</label>
            <input
              type="password"
              required
              value={form.secret_key}
              onChange={(e) => setForm({ ...form, secret_key: e.target.value })}
              className="w-full border rounded px-3 py-2 font-mono text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Leverage</label>
              <select
                value={form.leverage}
                onChange={(e) => setForm({ ...form, leverage: parseInt(e.target.value) })}
                className="w-full border rounded px-3 py-2"
              >
                {[1, 5, 10, 20, 50, 75, 100, 125].map((lev) => (
                  <option key={lev} value={lev}>{lev}x</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Margin Type</label>
              <select
                value={form.margin_type}
                onChange={(e) => setForm({ ...form, margin_type: e.target.value as any })}
                className="w-full border rounded px-3 py-2"
              >
                <option value="ISOLATED">Isolated</option>
                <option value="CROSS">Cross</option>
              </select>
            </div>
          </div>

          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={form.testnet}
                onChange={(e) => setForm({ ...form, testnet: e.target.checked })}
                className="rounded"
              />
              <span className="text-sm">Use Testnet (Paper Trading)</span>
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Adding...' : 'Add Key'}
            </Button>
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </form>

        <p className="mt-4 text-xs text-gray-500">
          <strong>Security Note:</strong> API keys are encrypted with AES-256-GCM.
          Only trade permissions are enabled. Withdrawal is permanently disabled.
        </p>
      </div>
    </div>
  );
}
