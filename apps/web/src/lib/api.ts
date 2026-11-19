import axios from "axios";
import { useAuthStore } from "./auth-store";

// Normalize API_URL so it always points to the versioned API base (ends with /api/v1)
const rawUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const API_URL = rawUrl.endsWith("/api/v1")
  ? rawUrl
  : `${rawUrl.replace(/\/+$/, "")}/api/v1`;

export const api = axios.create({
  baseURL: API_URL,
});

// Add a request interceptor to attach the JWT token
api.interceptors.request.use(
  (config) => {
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
