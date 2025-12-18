import ApiClient from '../client';
import { getServiceUrl } from '../config';
import type {
  AuthTokens,
  LoginCredentials,
  RegisterData,
  User,
  ApiResponse,
} from '@hospitality-platform/types';

export class AuthService {
  constructor(private client: ApiClient) {}

  async login(credentials: LoginCredentials): Promise<ApiResponse<{ user: User; tokens: AuthTokens }>> {
    // Use service-specific URL for auth endpoints
    const url = getServiceUrl('auth', '/auth/login');
    return this.client.post(url, credentials);
  }

  async register(data: RegisterData): Promise<ApiResponse<{ user: User; tokens: AuthTokens }>> {
    // Use service-specific URL for auth endpoints
    const url = getServiceUrl('auth', '/auth/register');
    return this.client.post(url, data);
  }

  async logout(): Promise<void> {
    const url = getServiceUrl('auth', '/auth/logout');
    return this.client.post(url);
  }

  async refreshToken(refreshToken: string): Promise<ApiResponse<AuthTokens>> {
    const url = getServiceUrl('auth', '/auth/refresh');
    return this.client.post(url, { refreshToken });
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    const url = getServiceUrl('auth', '/auth/me');
    return this.client.get(url);
  }

  async updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
    const url = getServiceUrl('auth', '/auth/profile');
    return this.client.patch(url, data);
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    const url = getServiceUrl('auth', '/auth/change-password');
    return this.client.post(url, { currentPassword, newPassword });
  }

  async requestPasswordReset(email: string): Promise<void> {
    const url = getServiceUrl('auth', '/auth/password-reset/request');
    return this.client.post(url, { email });
  }

  async resetPassword(token: string, newPassword: string): Promise<void> {
    const url = getServiceUrl('auth', '/auth/password-reset/confirm');
    return this.client.post(url, { token, newPassword });
  }
}

