import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/features/auth/hooks/use-auth-store";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Interceptor to inject JWT token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().accessToken;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for automatic token refresh (if implemented) and error standardization
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    // Check if error is 401 and we haven't retried yet
    if (error.response?.status === 401 && originalRequest && !(originalRequest as unknown as Record<string, unknown>)._retry) {
      (originalRequest as unknown as Record<string, unknown>)._retry = true;
      
      const authStore = useAuthStore.getState();
      try {
        // Here you would typically call a refresh endpoint.
        // For SpeakLift v1, if there is no refresh token implemented in backend yet,
        // we just clear the session and force re-login.
        // Future: await authStore.refreshSession();
        
        // As backend currently doesn't have refresh token support according to docs,
        // we log out the user on 401 to prevent infinite loops.
        authStore.clearSession();
        
        // Wait, if refresh logic is added later, it goes here.
        return Promise.reject(error);
      } catch (refreshError) {
        authStore.clearSession();
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
