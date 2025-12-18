import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, AuthTokens, BusinessContext } from '@hospitality-platform/types';
import { TokenStorage } from '@hospitality-platform/utils';
import { createApiServices, type TokenStorage as ApiTokenStorage } from '@hospitality-platform/api-client';

interface AuthState {
  user: User | null;
  businessContext: BusinessContext | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setBusinessContext: (context: BusinessContext | null) => void;
  setTokens: (tokens: AuthTokens) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

const tokenStorageAdapter: ApiTokenStorage = {
  getAccessToken: () => TokenStorage.getAccessToken(),
  getRefreshToken: () => TokenStorage.getRefreshToken(),
  setTokens: (tokens) => TokenStorage.setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresIn),
  clearTokens: () => TokenStorage.clearTokens(),
};

export const apiServices = createApiServices(tokenStorageAdapter);

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      businessContext: null,
      isAuthenticated: false,
      isLoading: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setBusinessContext: (context) => set({ businessContext: context }),
      setTokens: (tokens) => {
        TokenStorage.setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresIn);
      },
      logout: () => {
        TokenStorage.clearTokens();
        set({ user: null, businessContext: null, isAuthenticated: false });
      },
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'business-auth-storage',
      partialize: (state) => ({ user: state.user, businessContext: state.businessContext, isAuthenticated: state.isAuthenticated }),
    }
  )
);

