import ApiClient from '../client';

export interface Favorite {
  user_id: string;
  place_id: string;
  note?: string;
  created_at: string;
  is_favorited: boolean;
}

export interface FavoriteListResponse {
  items: Favorite[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface BulkFavoriteStatus {
  [placeId: string]: boolean;
}

export class FavoritesService {
  constructor(private client: ApiClient) {}

  async listFavorites(page = 1, pageSize = 20): Promise<FavoriteListResponse> {
    return this.client.get('/v1/favorites', {
      params: { page, page_size: pageSize },
    });
  }

  async addFavorite(placeId: string, note?: string): Promise<Favorite> {
    return this.client.post('/v1/favorites', { place_id: placeId, note });
  }

  async getFavorite(placeId: string): Promise<Favorite> {
    return this.client.get(`/v1/favorites/${placeId}`);
  }

  async updateFavorite(placeId: string, note: string): Promise<Favorite> {
    return this.client.patch(`/v1/favorites/${placeId}`, { note });
  }

  async removeFavorite(placeId: string): Promise<{ success: boolean; message: string }> {
    return this.client.delete(`/v1/favorites/${placeId}`);
  }

  async checkStatus(placeId: string): Promise<{ place_id: string; is_favorited: boolean }> {
    return this.client.get(`/v1/favorites/${placeId}/status`);
  }

  async bulkCheckStatus(placeIds: string[]): Promise<{ favorites: BulkFavoriteStatus }> {
    return this.client.post('/v1/favorites/bulk-status', { place_ids: placeIds });
  }

  async toggleFavorite(placeId: string): Promise<{ place_id: string; is_favorited: boolean }> {
    return this.client.post(`/v1/favorites/${placeId}/toggle`);
  }
}
