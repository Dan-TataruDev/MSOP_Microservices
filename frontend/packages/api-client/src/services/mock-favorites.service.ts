/**
 * Mock Favorites Service
 * Provides mock favorites data for development.
 */
import type { Favorite, FavoriteListResponse, BulkFavoriteStatus } from './favorites.service';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock venue data to link with favorites
const MOCK_VENUES = [
  { id: '1', name: 'The Grand Hotel', type: 'hotel' },
  { id: '2', name: 'Bella Italia Restaurant', type: 'restaurant' },
  { id: '3', name: 'Coffee Corner', type: 'cafe' },
  { id: '4', name: 'Fashion Boutique', type: 'retail' },
  { id: '5', name: 'Sushi Master', type: 'restaurant' },
  { id: '6', name: 'Urban Retreat Hotel', type: 'hotel' },
];

// Store favorites per user in memory
const userFavorites: Record<string, Map<string, Favorite>> = {};

function getUserFavorites(userId: string): Map<string, Favorite> {
  if (!userFavorites[userId]) {
    userFavorites[userId] = new Map();
    // Pre-populate with some default favorites
    const defaultFavorites = [
      { placeId: '1', note: 'Beautiful hotel with amazing views!' },
      { placeId: '2', note: 'Best pasta in town' },
      { placeId: '5', note: 'Fresh sushi, must try omakase' },
    ];
    defaultFavorites.forEach((fav, idx) => {
      userFavorites[userId].set(fav.placeId, {
        user_id: userId,
        place_id: fav.placeId,
        note: fav.note,
        created_at: new Date(Date.now() - (idx + 1) * 7 * 24 * 60 * 60 * 1000).toISOString(),
        is_favorited: true,
      });
    });
  }
  return userFavorites[userId];
}

let currentUserId = 'mock-user'; // Will be set by the service

export class MockFavoritesService {
  setUserId(userId: string) {
    currentUserId = userId;
  }

  async listFavorites(page = 1, pageSize = 20): Promise<FavoriteListResponse> {
    await delay(300);
    const favorites = getUserFavorites(currentUserId);
    const items = Array.from(favorites.values());
    const total = items.length;
    const totalPages = Math.ceil(total / pageSize);
    const start = (page - 1) * pageSize;
    const paginatedItems = items.slice(start, start + pageSize);

    return {
      items: paginatedItems,
      total,
      page,
      page_size: pageSize,
      total_pages: totalPages,
      has_next: page < totalPages,
      has_prev: page > 1,
    };
  }

  async addFavorite(placeId: string, note?: string): Promise<Favorite> {
    await delay(200);
    const favorites = getUserFavorites(currentUserId);
    const favorite: Favorite = {
      user_id: currentUserId,
      place_id: placeId,
      note,
      created_at: new Date().toISOString(),
      is_favorited: true,
    };
    favorites.set(placeId, favorite);
    return favorite;
  }

  async getFavorite(placeId: string): Promise<Favorite> {
    await delay(150);
    const favorites = getUserFavorites(currentUserId);
    const favorite = favorites.get(placeId);
    if (!favorite) {
      throw new Error('Favorite not found');
    }
    return favorite;
  }

  async updateFavorite(placeId: string, note: string): Promise<Favorite> {
    await delay(200);
    const favorites = getUserFavorites(currentUserId);
    const favorite = favorites.get(placeId);
    if (!favorite) {
      throw new Error('Favorite not found');
    }
    favorite.note = note;
    favorites.set(placeId, favorite);
    return favorite;
  }

  async removeFavorite(placeId: string): Promise<{ success: boolean; message: string }> {
    await delay(200);
    const favorites = getUserFavorites(currentUserId);
    if (favorites.has(placeId)) {
      favorites.delete(placeId);
      return { success: true, message: 'Favorite removed successfully' };
    }
    return { success: false, message: 'Favorite not found' };
  }

  async checkStatus(placeId: string): Promise<{ place_id: string; is_favorited: boolean }> {
    await delay(100);
    const favorites = getUserFavorites(currentUserId);
    return {
      place_id: placeId,
      is_favorited: favorites.has(placeId),
    };
  }

  async bulkCheckStatus(placeIds: string[]): Promise<{ favorites: BulkFavoriteStatus }> {
    await delay(150);
    const favorites = getUserFavorites(currentUserId);
    const result: BulkFavoriteStatus = {};
    placeIds.forEach(id => {
      result[id] = favorites.has(id);
    });
    return { favorites: result };
  }

  async toggleFavorite(placeId: string): Promise<{ place_id: string; is_favorited: boolean }> {
    await delay(200);
    const favorites = getUserFavorites(currentUserId);
    if (favorites.has(placeId)) {
      favorites.delete(placeId);
      return { place_id: placeId, is_favorited: false };
    } else {
      favorites.set(placeId, {
        user_id: currentUserId,
        place_id: placeId,
        created_at: new Date().toISOString(),
        is_favorited: true,
      });
      return { place_id: placeId, is_favorited: true };
    }
  }
}
