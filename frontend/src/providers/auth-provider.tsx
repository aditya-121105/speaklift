"use client";

import { useEffect } from "react";
import { useAuth } from "@/features/auth/hooks/use-auth";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { initialize } = useAuth();

  useEffect(() => {
    initialize();
  }, [initialize]);

  // Optional: Return a full screen loader during initial mount/hydration
  // if (isLoading) return <FullPageLoader />

  return <>{children}</>;
}
