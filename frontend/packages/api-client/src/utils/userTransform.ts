/**
 * Utility to transform backend user response to frontend User type.
 * Backend returns 'role' (string), frontend expects 'roles' (array).
 */
import type { User } from '@hospitality-platform/types';

export function transformBackendUser(backendUser: any): User {
  return {
    ...backendUser,
    id: String(backendUser.id),
    roles: backendUser.roles || (backendUser.role ? [backendUser.role] : ['guest']),
    preferences: backendUser.preferences || {
      notificationPreferences: {
        email: true,
        push: false,
        sms: false,
        marketing: false,
      },
      personalizationEnabled: true,
    },
    createdAt: backendUser.createdAt || backendUser.created_at || new Date().toISOString(),
    updatedAt: backendUser.updatedAt || backendUser.updated_at || new Date().toISOString(),
  };
}


