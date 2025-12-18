import ApiClient from '../client';
import { getServiceUrl } from '../config';
import { MockPersonalizationService } from './mock-personalization.service';
import type {
  GuestProfile,
  GuestPreference,
  PreferenceCategory,
  PreferenceHistory,
  GuestInteraction,
  InteractionType,
  GuestSegment,
  BehaviorSignal,
  PersonalizationContext,
  GuestDataExport,
  CreateGuestRequest,
  UpdateGuestRequest,
  CreatePreferenceRequest,
  UpdatePreferenceRequest,
  CreateInteractionRequest,
  InteractionFilter,
  ConsentPreferences,
  ApiResponse,
  PaginatedResponse,
} from '@hospitality-platform/types';

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL;
const mockService = new MockPersonalizationService();

export class PersonalizationService {
  constructor(private client: ApiClient) {}

  // Guest Profile Management
  async getGuestProfile(guestId: string): Promise<ApiResponse<GuestProfile>> {
    if (USE_MOCK) return mockService.getGuestProfile(guestId) as any;
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/profile`));
  }

  async getCurrentGuestProfile(): Promise<ApiResponse<GuestProfile>> {
    if (USE_MOCK) return mockService.getCurrentGuestProfile() as any;
    return this.client.get(getServiceUrl('personalization', '/api/v1/guests/me/profile'));
  }

  async createGuest(data: CreateGuestRequest): Promise<ApiResponse<GuestProfile>> {
    return this.client.post(getServiceUrl('personalization', '/api/v1/guests'), data);
  }

  async updateGuestProfile(
    guestId: string,
    data: UpdateGuestRequest
  ): Promise<ApiResponse<GuestProfile>> {
    return this.client.patch(getServiceUrl('personalization', `/api/v1/guests/${guestId}/profile`), data);
  }

  // Preferences Management
  async getGuestPreferences(
    guestId: string,
    activeOnly: boolean = true
  ): Promise<ApiResponse<GuestPreference[]>> {
    if (USE_MOCK) return mockService.getGuestPreferences(guestId) as any;
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/preferences`), {
      params: { active_only: activeOnly },
    });
  }

  async getGuestPreferenceByKey(
    guestId: string,
    preferenceKey: string
  ): Promise<ApiResponse<GuestPreference>> {
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/preferences/${preferenceKey}`));
  }

  async createPreference(
    guestId: string,
    data: CreatePreferenceRequest
  ): Promise<ApiResponse<GuestPreference>> {
    if (USE_MOCK) return mockService.createPreference(guestId, data) as any;
    return this.client.post(getServiceUrl('personalization', `/api/v1/guests/${guestId}/preferences`), data);
  }

  async updatePreference(
    guestId: string,
    preferenceId: string,
    data: UpdatePreferenceRequest
  ): Promise<ApiResponse<GuestPreference>> {
    return this.client.put(
      getServiceUrl('personalization', `/api/v1/guests/${guestId}/preferences/${preferenceId}`),
      data
    );
  }

  async getPreferenceHistory(
    guestId: string,
    preferenceId: string,
    limit: number = 100
  ): Promise<ApiResponse<PreferenceHistory[]>> {
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/preferences/history`), {
      params: { preference_id: preferenceId, limit },
    });
  }

  async getPreferenceCategories(): Promise<ApiResponse<PreferenceCategory[]>> {
    if (USE_MOCK) return mockService.getPreferenceCategories() as any;
    return this.client.get(getServiceUrl('personalization', '/api/v1/preference-categories'));
  }

  // Interaction History
  async createInteraction(
    guestId: string,
    data: CreateInteractionRequest
  ): Promise<ApiResponse<GuestInteraction>> {
    return this.client.post(getServiceUrl('personalization', `/api/v1/guests/${guestId}/interactions`), data);
  }

  async getGuestInteractions(
    guestId: string,
    filters?: InteractionFilter
  ): Promise<ApiResponse<GuestInteraction[]>> {
    if (USE_MOCK) return mockService.getGuestInteractions(guestId, filters) as any;
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/interactions`), {
      params: filters,
    });
  }

  async getInteractionTypes(): Promise<ApiResponse<InteractionType[]>> {
    return this.client.get(getServiceUrl('personalization', '/api/v1/interaction-types'));
  }

  // Personalization Data
  async getPersonalizationContext(
    guestId: string
  ): Promise<ApiResponse<PersonalizationContext>> {
    if (USE_MOCK) return mockService.getPersonalizationContext(guestId) as any;
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/personalization-context`));
  }

  async getGuestSegments(
    guestId: string,
    activeOnly: boolean = true
  ): Promise<ApiResponse<GuestSegment[]>> {
    if (USE_MOCK) return mockService.getGuestSegments(guestId) as any;
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/segments`), {
      params: { active_only: activeOnly },
    });
  }

  async getBehaviorSignals(
    guestId: string,
    activeOnly: boolean = true
  ): Promise<ApiResponse<BehaviorSignal[]>> {
    if (USE_MOCK) return mockService.getBehaviorSignals(guestId) as any;
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/behavior-signals`), {
      params: { active_only: activeOnly },
    });
  }

  async recomputePersonalizationContext(
    guestId: string
  ): Promise<ApiResponse<PersonalizationContext>> {
    return this.client.post(
      getServiceUrl('personalization', `/api/v1/guests/${guestId}/personalization-context/recompute`)
    );
  }

  // GDPR & Privacy
  async exportGuestData(guestId: string): Promise<ApiResponse<GuestDataExport>> {
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/data-export`));
  }

  async deleteGuestData(guestId: string): Promise<void> {
    return this.client.delete(getServiceUrl('personalization', `/api/v1/guests/${guestId}/data`));
  }

  async getGuestConsent(guestId: string): Promise<ApiResponse<ConsentPreferences>> {
    return this.client.get(getServiceUrl('personalization', `/api/v1/guests/${guestId}/consent`));
  }

  async updateGuestConsent(
    guestId: string,
    consent: Partial<ConsentPreferences>
  ): Promise<ApiResponse<ConsentPreferences>> {
    return this.client.put(getServiceUrl('personalization', `/api/v1/guests/${guestId}/consent`), consent);
  }
}
