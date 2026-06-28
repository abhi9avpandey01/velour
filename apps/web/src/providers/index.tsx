'use client';

/**
 * Velour — Client-side providers.
 *
 * Wraps the application with:
 * - TanStack Query's QueryClientProvider for data fetching
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';

interface ProvidersProps {
  readonly children: ReactNode;
}

/**
 * Application providers component.
 * Creates a stable QueryClient instance per session.
 */
export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
