/**
 * App-wide constants and environment-driven configuration.
 * Import from here instead of hardcoding values directly in components.
 */

/**
 * External ChatGPT-based CISAT advising assistant.
 * Set VITE_CHATBOT_URL in .env to override. Do NOT hardcode GPT URLs in source.
 */
export const CHATBOT_URL = import.meta.env.VITE_CHATBOT_URL ?? '';

/** Backend API base URL */
export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
