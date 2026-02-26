/**
 * App-wide constants and environment-driven configuration.
 * Import from here instead of hardcoding values directly in components.
 */

/** External ChatGPT-based CISAT advising assistant */
export const CHATBOT_URL =
  import.meta.env.VITE_CHATBOT_URL ??
  'https://chatgpt.com/g/g-68f72859a0288191afe57daa9afecd90-cisat-advising-assistant';

/** Backend API base URL */
export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
