// ──────────────────────────────────────────────────────────────
// @velour/config — Environment configuration and validation
// ──────────────────────────────────────────────────────────────

/**
 * Application configuration interface.
 * Defines all environment-dependent settings.
 */
export interface AppConfig {
  /** Base URL for the API backend. */
  readonly apiUrl: string;
  /** Current environment name. */
  readonly environment: 'development' | 'production' | 'test';
  /** Whether the app is running in development mode. */
  readonly isDevelopment: boolean;
  /** Whether the app is running in production mode. */
  readonly isProduction: boolean;
}

/**
 * Validated application configuration.
 * Reads from environment variables with sensible defaults.
 */
export const APP_CONFIG: AppConfig = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  environment:
    (process.env.NODE_ENV as AppConfig['environment']) ?? 'development',
  get isDevelopment() {
    return this.environment === 'development';
  },
  get isProduction() {
    return this.environment === 'production';
  },
};
