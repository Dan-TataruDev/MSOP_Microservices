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

// Helper to ensure user has roles array (for backward compatibility)
function normalizeUser(user: any): User | null {
  if (!user) return null;
  
  // If user already has roles array, return as is
  if (Array.isArray(user.roles)) {
    return user as User;
  }
  
  // Transform role (string) to roles (array)
  return {
    ...user,
    id: String(user.id),
    roles: user.role ? [user.role] : (user.roles || ['guest']),
    preferences: user.preferences || {
      notificationPreferences: {
        email: true,
        push: false,
        sms: false,
        marketing: false,
      },
      personalizationEnabled: true,
    },
    createdAt: user.createdAt || user.created_at || new Date().toISOString(),
    updatedAt: user.updatedAt || user.updated_at || new Date().toISOString(),
  } as User;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      businessContext: null,
      isAuthenticated: false,
      isLoading: false,
      setUser: (user) => {
        const normalizedUser = normalizeUser(user);
        set({ user: normalizedUser, isAuthenticated: !!normalizedUser });
      },
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
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, businessContext: state.businessContext, isAuthenticated: state.isAuthenticated }),
      // Transform persisted user on rehydration
      onRehydrateStorage: () => (state) => {
        if (state?.user) {
          state.user = normalizeUser(state.user);
        }
      },
    }
  )
);

