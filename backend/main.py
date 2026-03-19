"""
CISAT Academic Advising Chatbot — Backend API

FastAPI app that powers the embedded chat panel.
Integrates RAG retrieval, hallucination detection, and deadline intelligence.

Run: uvicorn main:app --reload --port 8000
"""

import asyncio
import base64
import binascii
import hmac
import json
import logging
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

load_dotenv()


def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DEFAULT_RATE_LIMIT = os.environ.get("DEFAULT_RATE_LIMIT", "30/minute")
CHAT_RATE_LIMIT = os.environ.get("CHAT_RATE_LIMIT", "10/minute")
ENABLE_API_DOCS = env_flag("ENABLE_API_DOCS")
ENABLE_RESPONSE_EVALUATION = env_flag("ENABLE_RESPONSE_EVALUATION")
DEMO_USERNAME = os.environ.get("DEMO_USERNAME")
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD")
DEMO_AUTH_ENABLED = bool(DEMO_USERNAME and DEMO_PASSWORD)
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    ).split(",")
    if origin.strip()
]
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
for env_host in (
    os.environ.get("RENDER_EXTERNAL_HOSTNAME"),
    os.environ.get("RAILWAY_PUBLIC_DOMAIN"),
):
    if env_host and env_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(env_host)

FRONTEND_DIST_DIR = Path(__file__).parent.parent / "dist"


def _unauthorized_response() -> PlainTextResponse:
    return PlainTextResponse(
        "Authentication required.",
        status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="Demo Access"'},
    )


def is_authorized(auth_header: str | None) -> bool:
    if not DEMO_AUTH_ENABLED:
        return True
    if not auth_header or not auth_header.startswith("Basic "):
        return False

    try:
        decoded = base64.b64decode(auth_header.split(" ", 1)[1]).decode("utf-8")
        username, password = decoded.split(":", 1)
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return False

    return hmac.compare_digest(username, DEMO_USERNAME or "") and hmac.compare_digest(
        password,
        DEMO_PASSWORD or "",
    )


# --- Structured logging (replaces bare print() calls) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("advising_api")

# Imports after load_dotenv() so env vars are available
from openai_client import MissingAPIKeyError, get_async_client  # noqa: E402
from assistant import get_or_create_assistant # noqa: E402


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

    def get_real_ip(request: Request) -> str:
        if forwarded_for := request.headers.get("X-Forwarded-For"):
            return forwarded_for.split(",")[0].strip()
        if real_ip := request.headers.get("X-Real-IP"):
            return real_ip.strip()
        return request.client.host if request.client else "127.0.0.1"

    limiter = Limiter(key_func=get_real_ip, default_limits=[DEFAULT_RATE_LIMIT])
    _HAS_RATE_LIMITER = True
except ImportError:
    limiter = None  # type: ignore[assignment]
    _HAS_RATE_LIMITER = False
    logger.warning("slowapi not installed — rate limiting disabled. Run: pip install slowapi")


# --- App setup ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize OpenAI Assistant on startup."""
    logger.info("Initializing application lifespan...")
    try:
        get_or_create_assistant()
        logger.info("OpenAI Assistant initialized successfully.")
    except Exception as e:
        logger.critical("FATAL: Could not initialize OpenAI Assistant: %s", e, exc_info=True)
        # In a real-world scenario, you might want the app to fail to start
        # if the assistant is critical. For now, we log it as critical.
        raise e
    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title="CISAT Advising Chatbot API",
    description="RAG-powered academic advising with hallucination detection and deadline intelligence",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if ENABLE_API_DOCS else None,
    redoc_url="/redoc" if ENABLE_API_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_API_DOCS else None,
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


@app.middleware("http")
async def demo_basic_auth(request: Request, call_next):
    if not DEMO_AUTH_ENABLED or request.method == "OPTIONS" or request.url.path == "/health":
        return await call_next(request)
    if not is_authorized(request.headers.get("Authorization")):
        return _unauthorized_response()
    return await call_next(request)


# --- CORS — scoped to actual needs ---

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
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

class UploadPlanResponse(BaseModel):
    """Response model for uploading a graduation plan."""
    thread_id: str
    file_id: str

class ChatRequest(BaseModel):
    """Request model for the main chat endpoint, using a thread ID."""

    thread_id: str
    message: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)
    # The frontend should send the file_id only with the first message.
    file_ids: list[str] = Field(default_factory=list)


class ToolCall(BaseModel):
    """Model for a tool call command to be sent to the frontend."""

    name: str
    args: dict


class ChatResponse(BaseModel):
    """
    Response model that can contain either a text reply or a frontend tool call.
    """

    reply: str | None = None
    tool_call: ToolCall | None = None
    # The following fields from the old response are no longer needed
    # with the new Assistant-based logic, but are kept for compatibility
    # if you need a phased rollout. For this migration, they are optional.
    flagged: bool = False
    is_deadline_query: bool = False



# --- Main API endpoints (async) ---

if _HAS_RATE_LIMITER:
    _chat_decorator = limiter.limit(CHAT_RATE_LIMIT)  # type: ignore[union-attr]
else:

    def _chat_decorator(fn):  # type: ignore[misc]
        return fn


@app.post("/api/upload-plan", response_model=UploadPlanResponse)
@_chat_decorator
async def upload_plan(request: Request, file: UploadFile = File(...)):
    """
    Accepts a student's graduation plan file, uploads it to OpenAI,
    and creates a new conversation thread. The file is NOT yet attached
    to the thread; the returned file_id must be passed to the /chat
    endpoint with the first message to create the attachment.
    """
    try:
        client = get_async_client()

        file_content = await file.read()
        if not file.filename:
            # Provide a fallback filename if it's missing
            file.filename = "student_plan"

        # Upload the file to OpenAI. The 'purpose' is crucial for Assistants API.
        uploaded_file = await client.files.create(
            file=(file.filename, file_content, file.content_type), purpose="assistants"
        )

        # Create a new thread for the user session.
        # Messages and attachments will be added in the /chat endpoint.
        thread = await client.beta.threads.create()

        logger.info(
            f"New plan uploaded and thread created. File ID: {uploaded_file.id}, Thread ID: {thread.id}"
        )

        return UploadPlanResponse(thread_id=thread.id, file_id=uploaded_file.id)

    except MissingAPIKeyError as exc:
        logger.error("Upload plan failed: %s", exc)
        raise HTTPException(status_code=503, detail="Chat service is not configured.")
    except Exception:
        logger.exception("Error during file upload and thread creation.")
        # Do not leak internal exception details to the client
        raise HTTPException(status_code=500, detail="Failed to process file.")


@app.post("/api/chat", response_model=ChatResponse)
@_chat_decorator
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    """
    Main chat endpoint, rewritten for the OpenAI Assistants API.
    Flow:
    1. Add user's message (and optional file) to the specified thread.
    2. Create a Run to process the thread with the Assistant.
    3. Poll the Run's status until it completes, fails, or requires action.
    4. Handle 'requires_action' for tool calls (backend execution or frontend forwarding).
    5. On completion, retrieve the Assistant's reply and send it to the client.
    """
    client = get_async_client()
    assistant_id = os.environ.get("OPENAI_ASSISTANT_ID")
    if not assistant_id:
        logger.error("OPENAI_ASSISTANT_ID is not set.")
        raise HTTPException(status_code=503, detail="Assistant is not configured.")

    try:
        # Sanitize user input before sending to OpenAI
        safe_message = sanitize_user_input(req.message)

        # Step 1: Add the user's message to the thread.
        # The `file_ids` list should be provided by the client on the first message.
        attachments = [
            {"file_id": file_id, "tools": [{"type": "file_search"}]}
            for file_id in req.file_ids
        ]
        await client.beta.threads.messages.create(
            thread_id=req.thread_id,
            role="user",
            content=safe_message,
            attachments=attachments or None,  # Use None if attachments list is empty
        )
        logger.info(f"Appended message to thread {req.thread_id}")

        # Step 2: Create a Run
        run = await client.beta.threads.runs.create(
            thread_id=req.thread_id, assistant_id=assistant_id
        )
        logger.info(f"Created run {run.id} for thread {req.thread_id}")

        # Step 3: Poll the Run's status
        while run.status in ["queued", "in_progress"]:
            await asyncio.sleep(1)  # Use asyncio.sleep in async functions
            run = await client.beta.threads.runs.retrieve(
                thread_id=req.thread_id, run_id=run.id
            )
            logger.info(f"Run {run.id} status: {run.status}")

        # Step 4: Handle terminal states
        if run.status == "completed":
            messages = await client.beta.threads.messages.list(thread_id=req.thread_id)
            # The latest message is the first in the list
            assistant_reply = messages.data[0].content[0].text.value
            return ChatResponse(reply=assistant_reply)

        elif run.status == "requires_action":
            if run.required_action is None:
                 raise HTTPException(status_code=500, detail="Run requires action, but no action was specified.")

            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []

            for tool in tool_calls:
                func_name = tool.function.name
                func_args = json.loads(tool.function.arguments)

                if func_name == "trigger_ui_navigation":
                    # This tool is for the frontend. We stop and return the call.
                    logger.info(f"Forwarding UI navigation tool call to frontend: {func_args}")
                    return ChatResponse(tool_call=ToolCall(name=func_name, args=func_args))

                elif func_name == "email_supervisor":
                    # Actual SMTP transport implementation
                    logger.info(f"Executing backend tool '{func_name}' with args: {func_args}")
                    
                    student_id = func_args.get('student_id', 'Unknown')
                    issue_summary = func_args.get('issue_summary', 'No summary provided')
                    
                    try:
                        import smtplib
                        from email.mime.text import MIMEText
                        
                        smtp_server = os.environ.get("SMTP_SERVER")
                        smtp_port = int(os.environ.get("SMTP_PORT", 587))
                        smtp_user = os.environ.get("SMTP_USERNAME")
                        smtp_pass = os.environ.get("SMTP_PASSWORD")
                        smtp_from = os.environ.get("SMTP_FROM", "advising-bot@example.com")
                        supervisor_email = os.environ.get("SUPERVISOR_EMAIL", "advisor@cgu.edu")
                        
                        if smtp_server and smtp_user and smtp_pass:
                            msg = MIMEText(f"An escalation has been triggered by the CISAT Advising Assistant.\n\nStudent ID: {student_id}\n\nSummary:\n{issue_summary}")
                            msg['Subject'] = f"Advising Escalation: Student {student_id}"
                            msg['From'] = smtp_from
                            msg['To'] = supervisor_email
                            
                            server = smtplib.SMTP(smtp_server, smtp_port)
                            server.starttls()
                            server.login(smtp_user, smtp_pass)
                            server.send_message(msg)
                            server.quit()
                            logger.info("Successfully sent supervisor email via SMTP.")
                            output = {"status": "success", "message": f"Supervisor has been notified via email about: {issue_summary}"}
                        else:
                            logger.warning("SMTP configuration missing. Simulating email send for now.")
                            output = {"status": "success", "message": f"(Simulated) Supervisor has been notified about: {issue_summary}"}
                    except Exception as email_exc:
                        logger.error(f"Failed to send email: {email_exc}")
                        output = {"status": "error", "message": "Failed to send the email due to an internal transport error."}
                        
                    tool_outputs.append(
                        {"tool_call_id": tool.id, "output": json.dumps(output)}
                    )

            # If there were any backend tools, submit their outputs
            if tool_outputs:
                logger.info(f"Submitting tool outputs for run {run.id}")
                run = await client.beta.threads.runs.submit_tool_outputs(
                    thread_id=req.thread_id, run_id=run.id, tool_outputs=tool_outputs
                )
                # Re-enter polling loop to get the final assistant response
                while run.status in ["queued", "in_progress"]:
                    await asyncio.sleep(1)
                    run = await client.beta.threads.runs.retrieve(
                        thread_id=req.thread_id, run_id=run.id
                    )
                    logger.info(f"Run {run.id} status after tool submission: {run.status}")

                if run.status == "completed":
                    messages = await client.beta.threads.messages.list(thread_id=req.thread_id)
                    assistant_reply = messages.data[0].content[0].text.value
                    return ChatResponse(reply=assistant_reply)

        # Handle other terminal states
        logger.error(f"Run ended with status: {run.status}. Details: {run.last_error}")
        detail = f"Assistant run failed with status: {run.status}"
        if run.last_error:
            detail += f" - {run.last_error.message}"
        raise HTTPException(status_code=500, detail=detail)

    except MissingAPIKeyError as exc:
        logger.error("Chat failed: %s", exc)
        raise HTTPException(status_code=503, detail="Chat service is not configured.")
    except Exception as e:
        logger.exception("An unexpected error occurred in the /api/chat endpoint.")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


# --- Health check (no service name disclosure) ---

@app.get("/health")
def health():
    return {"status": "ok"}


if FRONTEND_DIST_DIR.exists():
    @app.get("/", include_in_schema=False)
    async def frontend_index():
        return FileResponse(FRONTEND_DIST_DIR / "index.html")


    @app.get("/{full_path:path}", include_in_schema=False)
    async def frontend_routes(full_path: str):
        base_path = FRONTEND_DIST_DIR.resolve()
        # Normalize user-provided path segment relative to the frontend dist directory
        unsafe_segment = Path(full_path)
        try:
            # Resolve against base_path; this collapses ".." and follows symlinks
            candidate = (base_path / unsafe_segment).resolve()
            # Ensure the resolved candidate is within the frontend dist directory
            candidate.relative_to(base_path)
        except (ValueError, OSError) as exc:
            # Any attempt to escape the base path or invalid resolution results in a 404
            raise HTTPException(status_code=404) from exc

        # Only serve a file if it exists and is a regular file under base_path
        if candidate.is_file():
            return FileResponse(candidate)
        # For non-file routes, fall back to the SPA entry point
        return FileResponse(base_path / "index.html")
