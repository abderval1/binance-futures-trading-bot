import { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AdminDashboardPage from './pages/AdminDashboardPage';

export default function App() {
  const { isAuthenticated, user, token, fetchMe } = useAuthStore();
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token && !isAuthenticated) {
        await fetchMe();
      }
      setIsInitializing(false);
    };
    initAuth();
  }, [token, isAuthenticated, fetchMe]);

  if (isInitializing) {
    return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  }

  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />
      } />
      <Route path="/dashboard" element={
        isAuthenticated ? <DashboardPage /> : <Navigate to="/login" />
      } />
      <Route path="/admin" element={
        isAuthenticated && user?.role === 'admin' ? <AdminDashboardPage /> : <Navigate to="/dashboard" />
      } />
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}
