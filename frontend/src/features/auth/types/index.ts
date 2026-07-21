export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export type AuthStatus = "idle" | "loading" | "authenticated" | "unauthenticated";
