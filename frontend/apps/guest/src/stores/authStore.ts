import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, AuthTokens } from '@hospitality-platform/types';
import { TokenStorage } from '@hospitality-platform/utils';
import { createApiServices, type TokenStorage as ApiTokenStorage } from '@hospitality-platform/api-client';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setTokens: (tokens: AuthTokens) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

// Create token storage adapter for API client
const tokenStorageAdapter: ApiTokenStorage = {
  getAccessToken: () => TokenStorage.getAccessToken(),
  getRefreshToken: () => TokenStorage.getRefreshToken(),
  setTokens: (tokens) => TokenStorage.setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresIn),
  clearTokens: () => TokenStorage.clearTokens(),
};

// Initialize API services
export const apiServices = createApiServices(tokenStorageAdapter);

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setTokens: (tokens) => {
        TokenStorage.setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresIn);
      },
      logout: () => {
        TokenStorage.clearTokens();
        set({ user: null, isAuthenticated: false });
      },
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);

