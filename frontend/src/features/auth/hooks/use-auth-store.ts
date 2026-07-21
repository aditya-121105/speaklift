import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { AuthStatus, User } from "../types";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  status: AuthStatus;
  setAuth: (user: User, token: string) => void;
  setUser: (user: User) => void;
  clearSession: () => void;
  setStatus: (status: AuthStatus) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      status: "idle",

      setAuth: (user, token) =>
        set({
          user,
          accessToken: token,
          status: "authenticated",
        }),

      setUser: (user) =>
        set({
          user,
        }),

      clearSession: () =>
        set({
          user: null,
          accessToken: null,
          status: "unauthenticated",
        }),

      setStatus: (status) =>
        set({
          status,
        }),
    }),
    {
      name: "speaklift-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ accessToken: state.accessToken }), // Only persist token
    }
  )
);
