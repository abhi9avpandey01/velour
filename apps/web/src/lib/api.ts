import axios from "axios";
import { useAuthStore } from "./auth-store";

function getInitialBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;
    return envUrl.endsWith("/api/v1") ? envUrl : `${envUrl.replace(/\/+$/, "")}/api/v1`;
  }
  // In production / deployed builds, default to Render backend
  if (process.env.NODE_ENV === "production") {
    return "https://velour-bfz1.onrender.com/api/v1";
  }
  return "http://localhost:8000/api/v1";
}

export const api = axios.create({
  baseURL: getInitialBaseUrl(),
});

// Add a request interceptor to attach the JWT token and guarantee the correct backend URL
api.interceptors.request.use(
  (config) => {
    // Dynamic client-side origin safety:
    // When running on a deployed domain (like Vercel / HTTPS), never call localhost
    if (typeof window !== "undefined") {
      const isLocalhost =
        window.location.hostname === "localhost" ||
        window.location.hostname === "127.0.0.1";

      if (!isLocalhost && (!config.baseURL || config.baseURL.includes("localhost"))) {
        config.baseURL = "https://velour-bfz1.onrender.com/api/v1";
      } else if (isLocalhost && (!config.baseURL || config.baseURL.includes("onrender.com"))) {
        config.baseURL = "http://localhost:8000/api/v1";
      }
    }

    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle global errors (like 401 Unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      // Optionally redirect to login, handled in components generally
    }
    return Promise.reject(error);
  }
);
