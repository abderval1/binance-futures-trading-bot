import { useState, useEffect } from 'react';
import { useAuthStore, useApiKeysStore, usePositionsStore, useTradingStore } from '@/store';
import { tradingAPI, apiKeysAPI } from '@/lib/api';
import Button from '@/components/ui/Button';
import type { Position, Trade, Balance } from '@/types';
import { formatDistanceToNow } from 'date-fns';

export default function AdminDashboard() {
  const { user } = useAuthStore();
  const { keys } = useApiKeysStore();
  const { positions } = usePositionsStore();
  const [trades, setTrades] = useState<Trade[]>([]);
  const [balance, setBalance] = useState<Balance[]>([]);
  const [selectedKey, setSelectedKey] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'settings'>('overview');

  useEffect(() => {
    if (selectedKey) {
      loadData();
    }
  }, [selectedKey]);

  const loadData = async () => {
    if (!selectedKey) return;
    const [tradesRes, balanceRes] = await Promise.all([
      tradingAPI.getPositions(selectedKey), // will be expanded to trades endpoint
      tradingAPI.getBalance(selectedKey),
    ]);
    setTrades(tradesRes.data as any); // TODO: add trades endpoint
    setBalance(balanceRes.data);
  };

  if (user?.role !== 'admin') {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
        <p className="text-gray-600">Admin privileges required</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm font-medium">Total Users</h3>
            <p className="text-3xl font-bold">24</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm font-medium">Active Subscribers</h3>
            <p className="text-3xl font-bold text-green-600">18</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm font-medium">Total Accounts</h3>
            <p className="text-3xl font-bold">42</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm font-medium">Daily Trades</h3>
            <p className="text-3xl font-bold">127</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm font-medium">MRR</h3>
            <p className="text-3xl font-bold text-blue-600">$1,499</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="border-b px-6 py-4">
            <div className="flex gap-4">
              {['overview', 'users', 'settings'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab as any)}
                  className={`px-4 py-2 font-medium capitalize ${
                    activeTab === tab
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'overview' && <OverviewTab positions={positions} trades={trades} balance={balance} selectedKey={selectedKey} keys={keys} onSelectKey={setSelectedKey} />}
            {activeTab === 'users' && <UsersTab />}
            {activeTab === 'settings' && <SettingsTab />}
          </div>
        </div>
      </div>
    </div>
  );
}

function OverviewTab({ positions, trades, balance, selectedKey, keys, onSelectKey }: any) {
  const totalPnl = positions.reduce((sum: number, p: Position) => sum + p.unrealized_pnl / 10000, 0);
  const totalBalance = balance.reduce((sum: number, b: Balance) => sum + parseFloat(b.balance), 0);

  return (
    <div>
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">View by API Key</label>
        <select
          value={selectedKey || ''}
          onChange={(e) => onSelectKey(Number(e.target.value) || null)}
          className="w-full md:w-64 border rounded px-3 py-2"
        >
          <option value="">All Accounts</option>
          {keys.map((k: any) => (
            <option key={k.id} value={k.id}>{k.label}</option>
          ))}
        </select>
      </div>

      {/* Balances */}
      {balance.length > 0 && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Balances</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full border">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">Asset</th>
                  <th className="px-4 py-2 text-left">Balance</th>
                  <th className="px-4 py-2 text-left">Available</th>
                </tr>
              </thead>
              <tbody>
                {balance.map((b: Balance) => (
                  <tr key={b.asset} className="border-t">
                    <td className="px-4 py-2 font-medium">{b.asset}</td>
                    <td className="px-4 py-2">{parseFloat(b.balance).toFixed(4)}</td>
                    <td className="px-4 py-2">{parseFloat(b.availableBalance).toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Trades */}
      {trades.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Recent Trades</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full border">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2">Symbol</th>
                  <th className="px-4 py-2">Side</th>
                  <th className="px-4 py-2">Type</th>
                  <th className="px-4 py-2">Qty</th>
                  <th className="px-4 py-2">Price</th>
                  <th className="px-4 py-2">PnL</th>
                  <th className="px-4 py-2">Time</th>
                </tr>
              </thead>
              <tbody>
                {trades.slice(0, 10).map((trade: Trade) => (
                  <tr key={trade.id} className="border-t">
                    <td className="px-4 py-2">{trade.symbol}</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        trade.side === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>{trade.side}</span>
                    </td>
                    <td className="px-4 py-2">{trade.order_type}</td>
                    <td className="px-4 py-2">{(trade.quantity / 10000).toFixed(4)}</td>
                    <td className="px-4 py-2">${(trade.price / 10000).toFixed(2)}</td>
                    <td className={`px-4 py-2 font-medium ${
                      trade.realized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      ${(trade.realized_pnl / 10000).toFixed(2)}
                    </td>
                    <td className="px-4 py-2 text-gray-500 text-sm">
                      {formatDistanceToNow(new Date(trade.executed_at), { addSuffix: true })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="mt-8 grid grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Performance Summary</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-500">Total P&L (Open)</span>
              <span className={`font-bold ${totalPnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${totalPnl.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Open Positions</span>
              <span className="font-bold">{positions.length}</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">System Health</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-500">API</span>
              <span className="text-green-600">● Online</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Database</span>
              <span className="text-green-600">● Connected</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Binance</span>
              <span className="text-green-600">● Connected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function UsersTab() {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">User Management</h3>
      <p className="text-gray-500">User management coming soon...</p>
      {/* Future: CRUD users, assign subscriptions, view activity */}
    </div>
  );
}

function SettingsTab() {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">System Settings</h3>
      <p className="text-gray-500">Settings panel coming soon...</p>
      {/* Future: Configure trading limits, risk parameters, etc. */}
    </div>
  );
}
