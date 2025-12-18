import axios, { AxiosInstance, AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG, getApiUrl, getServiceUrl } from './config';
import type { ApiError, AuthTokens } from '@hospitality-platform/types';

export interface TokenStorage {
  getAccessToken: () => string | null;
  getRefreshToken: () => string | null;
  setTokens: (tokens: AuthTokens) => void;
  clearTokens: () => void;
}

class ApiClient {
  private client: AxiosInstance;
  private tokenStorage: TokenStorage;
  private refreshPromise: Promise<string> | null = null;

  constructor(tokenStorage: TokenStorage) {
    this.tokenStorage = tokenStorage;
    this.client = axios.create({
      baseURL: API_CONFIG.baseURL,
      timeout: API_CONFIG.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor - attach auth token
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = this.tokenStorage.getAccessToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // Handle 401 Unauthorized - attempt token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshAccessToken();
            if (newToken && originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            this.tokenStorage.clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        // Transform error to ApiError format
        const apiError: ApiError = {
          message: error.response?.data?.message || error.message || 'An error occurred',
          code: error.response?.data?.code || 'UNKNOWN_ERROR',
          statusCode: error.response?.status || 500,
          details: error.response?.data?.details,
          requestId: error.response?.headers['x-request-id'],
        };

        return Promise.reject(apiError);
      }
    );
  }

  private async refreshAccessToken(): Promise<string> {
    // Prevent multiple simultaneous refresh attempts
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = (async () => {
      try {
        const refreshToken = this.tokenStorage.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post<{ data: AuthTokens }>(
          getServiceUrl('auth', '/auth/refresh'),
          { refreshToken }
        );

        const tokens = response.data.data;
        this.tokenStorage.setTokens(tokens);
        return tokens.accessToken;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  // Check if URL is absolute (starts with http:// or https://)
  private isAbsoluteUrl(url: string): boolean {
    return url.startsWith('http://') || url.startsWith('https://');
  }

  // Get config with auth header for absolute URL requests
  private getConfigWithAuth(config?: AxiosRequestConfig): AxiosRequestConfig {
    const token = this.tokenStorage.getAccessToken();
    return {
      ...config,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...config?.headers,
      },
    };
  }

  // Generic request methods
  // For absolute URLs, use axios directly to bypass baseURL
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    if (this.isAbsoluteUrl(url)) {
      const response = await axios.get<T>(url, this.getConfigWithAuth(config));
      return response.data;
    }
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    if (this.isAbsoluteUrl(url)) {
      const response = await axios.post<T>(url, data, this.getConfigWithAuth(config));
      return response.data;
    }
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    if (this.isAbsoluteUrl(url)) {
      const response = await axios.put<T>(url, data, this.getConfigWithAuth(config));
      return response.data;
    }
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    if (this.isAbsoluteUrl(url)) {
      const response = await axios.patch<T>(url, data, this.getConfigWithAuth(config));
      return response.data;
    }
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    if (this.isAbsoluteUrl(url)) {
      const response = await axios.delete<T>(url, this.getConfigWithAuth(config));
      return response.data;
    }
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  // Get the underlying axios instance for advanced use cases
  getInstance(): AxiosInstance {
    return this.client;
  }
}

export default ApiClient;

