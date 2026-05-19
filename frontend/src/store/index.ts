import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, APIKey, Position, Trade, Balance } from '@/types';
import { authAPI, apiKeysAPI, tradingAPI } from '@/lib/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const response = await authAPI.login(email, password);
        const token = response.data.access_token;
        localStorage.setItem('token', token);
        const userResponse = await authAPI.me();
        set({ user: userResponse.data, token, isAuthenticated: true });
      },

      register: async (email, password, fullName) => {
        await authAPI.register({ email, password, full_name: fullName });
        await get().login(email, password);
      },

      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
      },

      fetchMe: async () => {
        const token = get().token;
        if (!token) return;
        try {
          const response = await authAPI.me();
          set({ user: response.data, isAuthenticated: true });
        } catch {
          set({ user: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);

// API Keys Store
interface ApiKeysState {
  keys: APIKey[];
  selectedKeyId: number | null;
  loading: boolean;
  fetchKeys: () => Promise<void>;
  addKey: (data: APIKey) => Promise<void>;
  removeKey: (id: number) => Promise<void>;
  selectKey: (id: number) => void;
}

export const useApiKeysStore = create<ApiKeysState>((set, get) => ({
  keys: [],
  selectedKeyId: null,
  loading: false,

  fetchKeys: async () => {
    set({ loading: true });
    try {
      const response = await apiKeysAPI.getAll();
      // Mask keys in frontend
      const keys = response.data.map((k: APIKey) => ({
        ...k,
        api_key: null,
        secret_key: null,
      }));
      set({ keys, loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  addKey: async (data: APIKey) => {
    const response = await apiKeysAPI.create(data);
    set({ keys: [...get().keys, response.data] });
  },

  removeKey: async (id: number) => {
    await apiKeysAPI.delete(id);
    set({ keys: get().keys.filter(k => k.id !== id) });
  },

  selectKey: (id: number) => set({ selectedKeyId: id }),
}));

// Positions Store
interface PositionsState {
  positions: Position[];
  selectedSymbol: string | null;
  fetchPositions: (apiKeyId?: number) => Promise<void>;
  selectSymbol: (symbol: string) => void;
}

export const usePositionsStore = create<PositionsState>((set) => ({
  positions: [],
  selectedSymbol: null,

  fetchPositions: async (apiKeyId) => {
    const response = await tradingAPI.getPositions(apiKeyId);
    set({ positions: response.data });
  },

  selectSymbol: (symbol) => set({ selectedSymbol: symbol }),
}));

// Trading Store
interface TradingState {
  balance: Balance[];
  recentTrades: Trade[];
  fetchBalance: (apiKeyId: number) => Promise<void>;
}

export const useTradingStore = create<TradingState>((set) => ({
  balance: [],
  recentTrades: [],

  fetchBalance: async (apiKeyId) => {
    const response = await tradingAPI.getBalance(apiKeyId);
    set({ balance: response.data });
  },
}));
