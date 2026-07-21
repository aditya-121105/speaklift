import { useCallback } from "react";
import { AxiosError } from "axios";
import { useAuthStore } from "./use-auth-store";
import { AuthService } from "../services/auth.service";
import { LoginFormData, SignupFormData } from "../schemas/auth.schema";
import { User } from "../types";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export function useAuth() {
  const router = useRouter();
  const { user, accessToken, status, setAuth, clearSession, setStatus, setUser } = useAuthStore();

  const initialize = useCallback(async () => {
    // If no token in storage, we are unauthenticated
    if (!useAuthStore.getState().accessToken) {
      setStatus("unauthenticated");
      return;
    }

    try {
      setStatus("loading");
      const currentUser = await AuthService.getCurrentUser();
      setUser(currentUser);
      setStatus("authenticated");
    } catch {
      // 401 will trigger clearSession from Axios interceptor
      setStatus("unauthenticated");
    }
  }, [setUser, setStatus]);

  const login = async (data: LoginFormData) => {
    try {
      const response = await AuthService.login(data);
      setAuth({} as User, response.access_token); // Set token first
      const currentUser = await AuthService.getCurrentUser(); // Fetch user
      setAuth(currentUser, response.access_token);
      toast.success("Welcome back!");
      router.push("/dashboard"); // Future dashboard route
    } catch (error: unknown) {
      const err = error as AxiosError<{ detail: string }>;
      toast.error(err.response?.data?.detail || "Failed to login. Please check your credentials.");
      throw error;
    }
  };

  const register = async (data: SignupFormData) => {
    try {
      await AuthService.register(data);
      // Auto-login after register
      await login({ email: data.email, password: data.password });
    } catch (error: unknown) {
      const err = error as AxiosError<{ detail: string }>;
      toast.error(err.response?.data?.detail || "Registration failed. Please try again.");
      throw error;
    }
  };

  const logout = () => {
    clearSession();
    toast.success("Logged out successfully");
    router.push("/login");
  };

  return {
    user,
    accessToken,
    status,
    isAuthenticated: status === "authenticated",
    isLoading: status === "loading" || status === "idle",
    initialize,
    login,
    register,
    logout,
  };
}
