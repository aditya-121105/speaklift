import { apiClient } from "@/lib/api-client";
import { AuthResponse, User } from "../types";
import { LoginFormData, SignupFormData, ForgotPasswordFormData, ResetPasswordFormData } from "../schemas/auth.schema";

export const AuthService = {
  async login(data: LoginFormData): Promise<AuthResponse> {
    // The backend uses OAuth2PasswordRequestForm which expects form data, 
    // or standard JSON depending on implementation. Let's use standard JSON or URL encoded if needed.
    // Based on standard FastAPI OAuth2, it expects `username` and `password` as application/x-www-form-urlencoded
    const formData = new URLSearchParams();
    formData.append("username", data.email);
    formData.append("password", data.password);

    const response = await apiClient.post<AuthResponse>("/auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    return response.data;
  },

  async register(data: SignupFormData): Promise<User> {
    const response = await apiClient.post<User>("/auth/register", data);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>("/auth/me");
    return response.data;
  },

  async forgotPassword(data: ForgotPasswordFormData): Promise<void> {
    await apiClient.post("/auth/forgot-password", data);
  },

  async resetPassword(token: string, data: ResetPasswordFormData): Promise<void> {
    await apiClient.post(`/auth/reset-password/${token}`, { password: data.password });
  },

  async verifyEmail(token: string): Promise<void> {
    await apiClient.get(`/auth/verify-email/${token}`);
  },
};
