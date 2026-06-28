// ──────────────────────────────────────────────────────────────
// @velour/types — Shared TypeScript types for the Velour platform
// ──────────────────────────────────────────────────────────────

// ── Auth ──────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  displayName: string;
  avatarUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuthSession {
  accessToken: string;
  refreshToken: string;
  user: User;
  expiresAt: number;
}

// ── Wardrobe ──────────────────────────────────────────────────

export type ClothingCategory =
  | 'shirt'
  | 't-shirt'
  | 'polo'
  | 'blouse'
  | 'sweater'
  | 'hoodie'
  | 'jacket'
  | 'coat'
  | 'blazer'
  | 'jeans'
  | 'trousers'
  | 'shorts'
  | 'skirt'
  | 'dress'
  | 'shoes'
  | 'sneakers'
  | 'boots'
  | 'sandals'
  | 'accessory'
  | 'other';

export type Season = 'spring' | 'summer' | 'autumn' | 'winter' | 'all-season';

export type Occasion = 'casual' | 'formal' | 'business' | 'sporty' | 'party' | 'date' | 'other';

export interface ClothingItem {
  id: string;
  userId: string;
  imageUrl: string;
  thumbnailUrl?: string;
  category: ClothingCategory;
  color: string;
  pattern?: string;
  season: Season[];
  occasions: Occasion[];
  brand?: string;
  name?: string;
  confidenceScore: number;
  createdAt: string;
  updatedAt: string;
}

export interface WardrobeSummary {
  totalItems: number;
  categoryCounts: Record<ClothingCategory, number>;
  recentUploads: ClothingItem[];
}

// ── AI Classification ─────────────────────────────────────────

export interface ClassificationResult {
  category: ClothingCategory;
  color: string;
  pattern?: string;
  season: Season[];
  occasions: Occasion[];
  confidenceScore: number;
}

// ── Outfit Recommendation ─────────────────────────────────────

export interface OutfitItem {
  clothingItem: ClothingItem;
  role: string; // e.g., "top", "bottom", "footwear", "outerwear", "accessory"
}

export interface OutfitRecommendation {
  id: string;
  items: OutfitItem[];
  occasion: Occasion;
  reason: string;
  confidenceScore: number;
  weather?: WeatherInfo;
  saved: boolean;
  createdAt: string;
}

export interface RecommendationRequest {
  occasion: Occasion;
  weather?: WeatherInfo;
  excludeItemIds?: string[];
}

// ── Weather ───────────────────────────────────────────────────

export interface WeatherInfo {
  temperature: number;
  unit: 'celsius' | 'fahrenheit';
  condition: string;
  humidity?: number;
  location?: string;
}

// ── Dashboard ─────────────────────────────────────────────────

export interface DashboardData {
  greeting: string;
  weather?: WeatherInfo;
  wardrobeSummary: WardrobeSummary;
  todayRecommendation?: OutfitRecommendation;
  recentUploads: ClothingItem[];
}

// ── API ───────────────────────────────────────────────────────

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: ApiMeta;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiMeta {
  page?: number;
  pageSize?: number;
  totalCount?: number;
  totalPages?: number;
}

export interface PaginationParams {
  page?: number;
  pageSize?: number;
}

// ── Filters ───────────────────────────────────────────────────

export interface WardrobeFilters {
  category?: ClothingCategory;
  color?: string;
  season?: Season;
  occasion?: Occasion;
  search?: string;
}
