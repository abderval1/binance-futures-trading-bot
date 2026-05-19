import { useEffect } from 'react';
import { useAuthStore, useApiKeysStore, usePositionsStore, useTradingStore } from '@/store';
import Button from '@/components/ui/Button';
import ApiKeyModal from '@/components/ApiKeyModal';
import { useState } from 'react';

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const { keys, selectedKeyId, fetchKeys, selectKey } = useApiKeysStore();
  const { positions, fetchPositions } = usePositionsStore();
  const { balance, fetchBalance } = useTradingStore();
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchKeys();
  }, [fetchKeys]);

  useEffect(() => {
    if (selectedKeyId) {
      fetchPositions(selectedKeyId);
      fetchBalance(selectedKeyId);
    }
  }, [selectedKeyId, fetchPositions, fetchBalance]);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-gray-900">Trading Bot</h1>
            {user?.role === 'admin' && (
              <a
                href="/admin"
                className="text-sm text-purple-600 hover:text-purple-800 font-medium"
              >
                Admin Panel
              </a>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right mr-4">
              <p className="text-sm font-medium text-gray-900">{user?.email}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
            <Button variant="secondary" size="sm" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* API Key Selector */}
        <div className="mb-8 bg-white p-6 rounded-lg shadow-sm flex justify-between items-center">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">Account:</label>
            <select
              value={selectedKeyId || ''}
              onChange={(e) => selectKey(Number(e.target.value))}
              className="mt-1 block w-64 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="">Select an account</option>
              {keys.map((key) => (
                <option key={key.id} value={key.id}>
                  {key.label} {key.testnet ? '(Testnet)' : ''}
                </option>
              ))}
            </select>
          </div>
          <Button onClick={() => setIsModalOpen(true)}>Add API Key</Button>
        </div>

        {selectedKeyId ? (
          <div className="space-y-8">
            {/* Stats Summary */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Balance</dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">
                    ${balance.length > 0 ? parseFloat(balance[0].balance).toFixed(2) : '0.00'}
                  </dd>
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <dt className="text-sm font-medium text-gray-500 truncate">Available Margin</dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">
                    ${balance.length > 0 ? parseFloat(balance[0].availableBalance).toFixed(2) : '0.00'}
                  </dd>
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <dt className="text-sm font-medium text-gray-500 truncate">Open Positions</dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">{positions.length}</dd>
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <dt className="text-sm font-medium text-gray-500 truncate">Account Status</dt>
                  <dd className="mt-1 text-lg font-medium text-green-600">Active</dd>
                </div>
              </div>
            </div>

            {/* Positions Table */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Open Positions</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entry Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mark Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unrealized PNL</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {positions.length > 0 ? (
                      positions.map((pos) => (
                        <tr key={pos.symbol}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{pos.symbol}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{(pos.quantity / 10000).toFixed(4)}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${(pos.entry_price / 10000).toFixed(2)}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${(pos.mark_price / 10000).toFixed(2)}</td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${pos.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            ${(pos.unrealized_pnl / 10000).toFixed(2)}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="px-6 py-10 text-center text-sm text-gray-500">No open positions found</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-20 bg-white rounded-lg shadow">
            <h2 className="text-xl font-medium text-gray-900">No Account Selected</h2>
            <p className="mt-2 text-gray-500">Please select an API key or add a new one to start trading.</p>
            <div className="mt-6">
              <Button onClick={() => setIsModalOpen(true)}>Add First API Key</Button>
            </div>
          </div>
        )}
      </main>

      <ApiKeyModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
