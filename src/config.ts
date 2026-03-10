/**
 * App-wide constants and environment-driven configuration.
 * Import from here instead of hardcoding values directly in components.
 */

/** Backend API base URL */
export const API_URL = import.meta.env.VITE_API_URL ?? '';
