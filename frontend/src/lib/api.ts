import axios from 'axios';
import type {
  User,
  APIKey,
  Position,
  Balance,
  SubscriptionPlan,
  OrderRequest,
  OrderResponse
} from '@/types';

const api = axios.create({
  baseURL: '/_/backend',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Error interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/auth/token', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
  register: (data: { email: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  me: () => api.get<User>('/auth/me'),
  getPlans: () => api.get<SubscriptionPlan[]>('/subscription-plans'),
};

// Users (admin only)
export const usersAPI = {
  getAll: () => api.get<User[]>('/users/'),
  get: (id: number) => api.get<User>(`/users/${id}`),
  update: (id: number, data: Partial<User>) => api.put<User>(`/users/${id}`, data),
};

// API Keys
export const apiKeysAPI = {
  getAll: () => api.get<APIKey[]>('/api-keys/'),
  create: (data: APIKey) => api.post<APIKey>('/api-keys/', data),
  delete: (id: number) => api.delete(`/api-keys/${id}`),
};

// Trading
export const tradingAPI = {
  placeOrder: (apiKeyId: number, order: OrderRequest) =>
    api.post<OrderResponse>(`/trading/order?api_key_id=${apiKeyId}`, order),
  closePosition: (apiKeyId: number, symbol: string) =>
    api.post(`/trading/close-position/${symbol}?api_key_id=${apiKeyId}`),
  getPositions: (apiKeyId?: number) => {
    const url = apiKeyId !== undefined
      ? `/trading/positions?api_key_id=${apiKeyId}`
      : '/trading/positions';
    return api.get<Position[]>(url);
  },
  getBalance: (apiKeyId: number) =>
    api.get<Balance[]>(`/trading/balance/${apiKeyId}`),
};

export default api;
