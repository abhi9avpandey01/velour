/**
 * Velour — Application state store.
 *
 * Zustand store for client-side state management.
 * Provides a foundation for UI state (sidebar, modals, etc.)
 */

import { create } from 'zustand';

interface AppState {
  /** Whether the sidebar/navigation is open (mobile). */
  isSidebarOpen: boolean;
  /** Toggle the sidebar open/closed state. */
  toggleSidebar: () => void;
  /** Explicitly set the sidebar state. */
  setSidebarOpen: (open: boolean) => void;
}

/**
 * Global application state store.
 * Manages UI state that needs to be shared across components.
 */
export const useAppStore = create<AppState>((set) => ({
  isSidebarOpen: false,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (open: boolean) => set({ isSidebarOpen: open }),
}));
