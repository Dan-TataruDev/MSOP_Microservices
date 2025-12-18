export class SecureStorage {
  private static isAvailable(): boolean {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  }

  static setItem(key: string, value: string): boolean {
    if (!this.isAvailable()) {
      return false;
    }
    try {
      localStorage.setItem(key, value);
      return true;
    } catch {
      return false;
    }
  }

  static getItem(key: string): string | null {
    if (!this.isAvailable()) {
      return null;
    }
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  }

  static removeItem(key: string): boolean {
    if (!this.isAvailable()) {
      return false;
    }
    try {
      localStorage.removeItem(key);
      return true;
    } catch {
      return false;
    }
  }

  static clear(): boolean {
    if (!this.isAvailable()) {
      return false;
    }
    try {
      localStorage.clear();
      return true;
    } catch {
      return false;
    }
  }
}

export class TokenStorage {
  private static readonly ACCESS_TOKEN_KEY = 'auth_access_token';
  private static readonly REFRESH_TOKEN_KEY = 'auth_refresh_token';
  private static readonly TOKEN_EXPIRY_KEY = 'auth_token_expiry';

  static setTokens(accessToken: string, refreshToken: string, expiresIn: number): void {
    const expiryTime = Date.now() + expiresIn * 1000;
    SecureStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
    SecureStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
    SecureStorage.setItem(this.TOKEN_EXPIRY_KEY, expiryTime.toString());
  }

  static getAccessToken(): string | null {
    return SecureStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static getRefreshToken(): string | null {
    return SecureStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static isTokenExpired(): boolean {
    const expiryStr = SecureStorage.getItem(this.TOKEN_EXPIRY_KEY);
    if (!expiryStr) return true;
    const expiryTime = parseInt(expiryStr, 10);
    return Date.now() >= expiryTime;
  }

  static clearTokens(): void {
    SecureStorage.removeItem(this.ACCESS_TOKEN_KEY);
    SecureStorage.removeItem(this.REFRESH_TOKEN_KEY);
    SecureStorage.removeItem(this.TOKEN_EXPIRY_KEY);
  }
}

