import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />
      } />
      <Route path="/dashboard" element={
        isAuthenticated ? <DashboardPage /> : <Navigate to="/login" />
      } />
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}
