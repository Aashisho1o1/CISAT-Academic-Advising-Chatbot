"""
Centralized OpenAI client — single source of truth for API key and client creation.

Import `get_client()` instead of creating OpenAI() instances in individual modules.
Validates the API key once at startup and reuses a single client across all modules.
"""

import logging
import os
import sys

from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger(__name__)

_sync_client: OpenAI | None = None
_async_client: AsyncOpenAI | None = None


def _get_api_key() -> str:
    """Return the OpenAI API key or abort with a clear message."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        logger.critical(
            "OPENAI_API_KEY environment variable is not set. "
            "Create a backend/.env file with your key. See SETUP.md."
        )
        sys.exit(1)
    return key


def get_client() -> OpenAI:
    """Return a reusable synchronous OpenAI client."""
    global _sync_client
    if _sync_client is None:
        _sync_client = OpenAI(api_key=_get_api_key())
    return _sync_client


def get_async_client() -> AsyncOpenAI:
    """Return a reusable asynchronous OpenAI client."""
    global _async_client
    if _async_client is None:
        _async_client = AsyncOpenAI(api_key=_get_api_key())
    return _async_client
