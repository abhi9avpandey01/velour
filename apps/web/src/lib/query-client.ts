/**
 * Velour — TanStack Query client configuration.
 *
 * Provides a pre-configured QueryClient for use in both
 * client components (via Providers) and server-side prefetching.
 */

import { QueryClient } from '@tanstack/react-query';

/**
 * Create a new QueryClient with default options.
 * Each invocation returns a fresh instance — do NOT share across requests
 * on the server side.
 */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  });
}
