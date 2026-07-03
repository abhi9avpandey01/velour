import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";

// --- Types (aligned with backend WardrobeItemResponse schema) ---
export interface WardrobeItem {
  id: string;
  user_id: string;
  name: string;
  category: string;
  subcategory: string;
  color: string;
  secondary_color?: string | null;
  brand?: string | null;
  size?: string | null;
  material?: string | null;
  pattern?: string | null;
  season: string;
  occasion: string;
  purchase_date?: string | null;
  purchase_price?: number | null;
  image_url: string;
  thumbnail_url: string;
  notes?: string | null;
  wears_count: number;
  favorite: boolean;
  archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  email: string;
  username: string;
  first_name: string | null;
  last_name: string | null;
  profile_picture_url: string | null;
  is_verified: boolean;
  is_active: boolean;
}

// Helper to extract error message from backend's ApiResponse error format
export function getApiError(err: any, fallback = "An error occurred"): string {
  // Custom VelourException format: { success: false, error: { code, message, details } }
  const velourMsg = err?.response?.data?.error?.message;
  if (velourMsg) return velourMsg;
  // Pydantic validation errors: { detail: [...] }
  const pydanticDetail = err?.response?.data?.detail;
  if (Array.isArray(pydanticDetail)) return pydanticDetail[0]?.msg || "Validation error";
  if (typeof pydanticDetail === "string") return pydanticDetail;
  return fallback;
}

// --- Current User Query ---
export function useCurrentUser() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const res = await api.get("/users/me");
      return res.data.data as UserProfile;
    },
    retry: false,
  });
}

// --- Wardrobe Queries ---
export function useWardrobe() {
  return useQuery({
    queryKey: ["wardrobe"],
    queryFn: async () => {
      const res = await api.get("/wardrobe");
      // Backend: ApiResponse<list[WardrobeItemResponse]> → { success, data: [...] }
      return res.data.data as WardrobeItem[];
    },
    // Poll every 3 seconds while any item is still processing
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;
      return false; // Items don't have processing_status in the new schema - disable polling
    },
  });
}

// --- Upload Mutations ---
export function useUploadImage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post("/wardrobe/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      // Backend returns ApiResponse<{ item_id, asset_id, processing_status }>
      return res.data.data as { item_id: string; asset_id: string; processing_status: string };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wardrobe"] });
    },
  });
}

// --- AI Analysis Mutations ---
export interface AnalysisResult {
  item_id: string;
  asset_id: string;
  attributes: {
    caption?: string;
    category?: string;
    primary_color?: string;
    material?: string;
    pattern?: string;
    overall_confidence?: number;
    model_version?: string;
    outfit_suggestions?: string;
    [key: string]: any;
  };
}

export function useAnalyzeImage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (itemId: string) => {
      const res = await api.post(`/wardrobe/${itemId}/analyze`);
      return res.data.data as AnalysisResult;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wardrobe"] });
    },
  });
}

export function useDeleteItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (itemId: string) => {
      const res = await api.delete(`/wardrobe/${itemId}`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wardrobe"] });
    },
  });
}

export function useToggleFavorite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (itemId: string) => {
      const res = await api.post(`/wardrobe/${itemId}/favorite`);
      return res.data.data as WardrobeItem;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wardrobe"] });
    },
  });
}

// --- Auth Mutations ---
export function useLogin() {
  return useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const res = await api.post("/auth/login", credentials);
      // Backend: ApiResponse<TokenResponse> → { success, data: { access_token, refresh_token, token_type } }
      return res.data.data as { access_token: string; refresh_token: string; token_type: string };
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (data: { email: string; username: string; password: string }) => {
      const res = await api.post("/auth/register", data);
      // Backend: ApiResponse<UserResponse> → { success, data: UserProfile }
      return res.data.data as UserProfile;
    },
  });
}
