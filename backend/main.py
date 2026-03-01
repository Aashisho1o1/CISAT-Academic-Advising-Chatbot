"""
CISAT Academic Advising Chatbot — Backend API

FastAPI app that powers the embedded chat panel.
Integrates RAG retrieval, hallucination detection, and deadline intelligence.

Run: uvicorn main:app --reload --port 8000
"""

import logging
import os
import re
from contextlib import asynccontextmanager
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

load_dotenv()

# --- Structured logging (replaces bare print() calls) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("advising_api")

# Imports after load_dotenv() so env vars are available
from openai_client import get_async_client  # noqa: E402
from rag import init_knowledge_base, retrieve  # noqa: E402
from evaluation.hallucination_detector import check_faithfulness, log_evaluation  # noqa: E402
from evaluation.deadline_router import is_deadline_query  # noqa: E402
from evaluation.deadline_prompts import BASE_SYSTEM_PROMPT, DEADLINE_SYSTEM_PROMPT  # noqa: E402
from evaluation.deadline_personalizer import get_clarifying_question  # noqa: E402


# --- Prompt injection defense ---

_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|rules)", re.I),
    re.compile(r"(disregard|forget)\s+(everything|all|the)\s+(above|previous|prior|instructions)", re.I),
    re.compile(r"you\s+are\s+now\s+(a|an|the)\s+", re.I),
    re.compile(r"system\s*prompt", re.I),
    re.compile(r"repeat\s+(the|your)\s+(instructions|system|prompt)", re.I),
    re.compile(r"output\s+(your|the)\s+(system|initial|original)\s+(prompt|instructions|message)", re.I),
]


def sanitize_user_input(text: str) -> str:
    """Strip known prompt-injection patterns from user text."""
    cleaned = text
    for pattern in _INJECTION_PATTERNS:
        cleaned = pattern.sub("[filtered]", cleaned)
    return cleaned.strip()


# --- Rate limiting (graceful degradation if slowapi not installed) ---

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
    _HAS_RATE_LIMITER = True
except ImportError:
    limiter = None  # type: ignore[assignment]
    _HAS_RATE_LIMITER = False
    logger.warning("slowapi not installed — rate limiting disabled. Run: pip install slowapi")


# --- App setup ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load knowledge base on startup. Boots in degraded mode if indexing fails."""
    try:
        init_knowledge_base()
    except Exception as e:
        logger.error("Knowledge base init failed (degraded mode): %s", e)
    yield


app = FastAPI(
    title="CISAT Advising Chatbot API",
    description="RAG-powered academic advising with hallucination detection and deadline intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

# Register rate limiter if available
if _HAS_RATE_LIMITER:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[possibly-undefined]


# --- Security headers middleware ---

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Inject standard security headers on every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' http://localhost:* https://api.openai.com"
    )
    return response


# --- CORS — scoped to actual needs ---

ALLOWED_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# --- Global exception handler (never leak stack traces to client) ---

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Please try again later."},
    )


# --- Request / Response models (with validation) ---

MAX_MESSAGE_LENGTH = 4000
MAX_HISTORY_LENGTH = 20


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=MAX_MESSAGE_LENGTH)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)
    history: list[Message] = Field(default_factory=list, max_length=MAX_HISTORY_LENGTH)


class ChatResponse(BaseModel):
    """Client-facing response. Internal evaluation data is NOT exposed."""
    reply: str
    flagged: bool = False
    is_deadline_query: bool = False


# --- Main chat endpoint (async) ---

if _HAS_RATE_LIMITER:
    _chat_decorator = limiter.limit("20/minute")  # type: ignore[union-attr]
else:
    def _chat_decorator(fn):  # type: ignore[misc]
        return fn


@app.post("/api/chat", response_model=ChatResponse)
@_chat_decorator
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    """
    Main chat endpoint. Flow:
    1. Sanitize user input (prompt injection defense)
    2. Detect if deadline query → route to enhanced prompt or ask clarifying question
    3. Retrieve relevant chunks from knowledge base (RAG)
    4. Generate response with OpenAI gpt-4o-mini (async)
    5. Run hallucination detection (post-processing, never blocks response)
    6. Return response WITHOUT internal evaluation metadata
    """
    client = get_async_client()

    # === STEP 0: Input sanitization ===
    safe_message = sanitize_user_input(req.message)

    # === STEP 1: Deadline routing ===
    deadline_detected = is_deadline_query(safe_message)

    if deadline_detected:
        clarifying_q = get_clarifying_question(
            safe_message,
            [msg.model_dump() for msg in req.history],
        )
        if clarifying_q:
            return ChatResponse(
                reply=clarifying_q,
                is_deadline_query=True,
            )

    # === STEP 2: RAG retrieval ===
    chunks = retrieve(safe_message, k=5)

    context = (
        "\n\n".join(f"[Source {i + 1}]:\n{chunk}" for i, chunk in enumerate(chunks))
        if chunks
        else "No relevant documents found in the knowledge base."
    )

    system_prompt = (
        DEADLINE_SYSTEM_PROMPT if deadline_detected else BASE_SYSTEM_PROMPT
    )
    system_prompt_with_context = f"{system_prompt}\n\n---\nKnowledge Base Context:\n{context}"

    # === STEP 3: Generate response (async) ===
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt_with_context}]

    for msg in req.history[-10:]:  # Keep last 10 turns to avoid token bloat
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": safe_message})

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,  # type: ignore[arg-type]
        temperature=0.2,
    )
    reply = completion.choices[0].message.content or ""

    # === STEP 4: Hallucination detection (post-processing, async) ===
    faith_result = await check_faithfulness(
        user_query=safe_message,
        chatbot_response=reply,
        retrieved_chunks=chunks,
    )
    log_evaluation(safe_message, reply, faith_result)

    if faith_result.get("flagged"):
        reply += (
            "\n\n---\n"
            "⚠️ *Please verify any specific dates or policy details above with the "
            "CGU Academic Calendar or your program coordinator, as information may "
            "have changed since our knowledge base was last updated.*"
        )

    # Return ONLY client-safe fields — no sources, scores, or verdicts
    return ChatResponse(
        reply=reply,
        flagged=faith_result.get("flagged", False),
        is_deadline_query=deadline_detected,
    )


# --- Health check (no service name disclosure) ---

@app.get("/health")
def health():
    return {"status": "ok"}
