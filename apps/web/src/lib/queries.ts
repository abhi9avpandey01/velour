import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";

// --- Types ---
export interface WardrobeItem {
  id: string;
  category: string;
  color: string;
  season: string;
  occasion: string;
  image_url: string;
  processing_status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  ai_status: string;
  confidence_score?: number;
  metadata?: any;
}

// --- Wardrobe Queries ---
export function useWardrobe() {
  return useQuery({
    queryKey: ["wardrobe"],
    queryFn: async () => {
      const res = await api.get("/wardrobe");
      return res.data.data as WardrobeItem[];
    },
    // Poll every 3 seconds if any item is not COMPLETED or FAILED
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;
      const isProcessing = data.some(
        (item: WardrobeItem) => item.processing_status === "PENDING" || item.processing_status === "PROCESSING"
      );
      return isProcessing ? 3000 : false;
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
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return res.data;
    },
    onSuccess: () => {
      // Invalidate the wardrobe query to trigger a refetch immediately
      queryClient.invalidateQueries({ queryKey: ["wardrobe"] });
    },
  });
}

// --- Auth Mutations ---
export function useLogin() {
  return useMutation({
    mutationFn: async (credentials: { username: string; password: string }) => {
      // The API uses OAuth2 password bearer format (form data)
      const formData = new URLSearchParams();
      formData.append("username", credentials.username);
      formData.append("password", credentials.password);
      
      const res = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      return res.data;
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (data: { email: string; username: string; password: string }) => {
      const res = await api.post("/auth/register", data);
      return res.data;
    },
  });
}
