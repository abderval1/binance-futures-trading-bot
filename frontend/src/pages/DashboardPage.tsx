export default function DashboardPage() {
  // Existing dashboard code remains
  // This will be enhanced with admin features

  // Add admin link in header if user is admin
  const { user } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
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
            <span className="text-sm text-gray-600">
              {user?.email} ({user?.role})
            </span>
            <Button variant="secondary" size="sm" onClick={() => useAuthStore.getState().logout()}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Rest of dashboard content... */}
    </div>
  );
}
