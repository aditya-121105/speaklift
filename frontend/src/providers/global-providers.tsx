"use client";

import * as React from "react";
import { ThemeProvider } from "./theme-provider";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./auth-provider";

/**
 * GlobalProviders acts as the composition root for all application-wide contexts.
 * 
 * Included:
 * - ThemeProvider (next-themes)
 * - QueryClientProvider (TanStack Query)
 */

export function GlobalProviders({ children }: { children: React.ReactNode }) {
  // Ensure the query client is stable during rendering
  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 2,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        attribute="class"
        defaultTheme="dark"
        enableSystem
        disableTransitionOnChange
      >
        <AuthProvider>{children}</AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
