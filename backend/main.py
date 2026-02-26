"""
CISAT Academic Advising Chatbot — Backend API

FastAPI app that powers the embedded chat panel.
Integrates RAG retrieval, hallucination detection, and deadline intelligence.

Run: uvicorn main:app --reload --port 8000
"""

import os
from contextlib import asynccontextmanager
from typing import Literal
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

from rag import init_knowledge_base, retrieve
from evaluation.hallucination_detector import check_faithfulness, log_evaluation
from evaluation.deadline_router import is_deadline_query
from evaluation.deadline_prompts import BASE_SYSTEM_PROMPT, DEADLINE_SYSTEM_PROMPT
from evaluation.deadline_personalizer import get_clarifying_question


# --- App setup ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load knowledge base on startup. Boots in degraded mode if indexing fails."""
    try:
        init_knowledge_base()
    except Exception as e:
        print(f"[STARTUP] Knowledge base init failed (degraded mode): {e}")
    yield


app = FastAPI(
    title="CISAT Advising Chatbot API",
    description="RAG-powered academic advising with hallucination detection and deadline intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# --- Request / Response models ---

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    sources: list[str] = Field(default_factory=list)
    hallucination_score: float | None = None
    verdict: str | None = None
    flagged: bool = False
    is_deadline_query: bool = False


# --- Main chat endpoint ---

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint. Flow:
    1. Detect if deadline query → route to enhanced prompt or ask clarifying question
    2. Retrieve relevant chunks from knowledge base (RAG)
    3. Generate response with OpenAI gpt-4o-mini
    4. Run hallucination detection (post-processing, never blocks response)
    5. Return response with faithfulness metadata
    """

    # === STEP 1: Deadline routing ===
    deadline_detected = is_deadline_query(req.message)

    if deadline_detected:
        clarifying_q = get_clarifying_question(
            req.message,
            [msg.model_dump() for msg in req.history],
        )
        if clarifying_q:
            # Return the clarifying question directly — skip RAG + generation for now
            return ChatResponse(
                reply=clarifying_q,
                is_deadline_query=True,
            )

    # === STEP 2: RAG retrieval ===
    chunks = retrieve(req.message, k=5)

    context = (
        "\n\n".join(f"[Source {i + 1}]:\n{chunk}" for i, chunk in enumerate(chunks))
        if chunks
        else "No relevant documents found in the knowledge base."
    )

    system_prompt = (
        DEADLINE_SYSTEM_PROMPT if deadline_detected else BASE_SYSTEM_PROMPT
    )
    system_prompt_with_context = f"{system_prompt}\n\n---\nKnowledge Base Context:\n{context}"

    # === STEP 3: Generate response ===
    messages = [{"role": "system", "content": system_prompt_with_context}]

    for msg in req.history[-10:]:  # Keep last 10 turns to avoid token bloat
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": req.message})

    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
    )
    reply = completion.choices[0].message.content or ""

    # === STEP 4: Hallucination detection (post-processing) ===
    faith_result = check_faithfulness(
        user_query=req.message,
        chatbot_response=reply,
        retrieved_chunks=chunks,
        client=openai_client,
    )
    log_evaluation(req.message, reply, faith_result)

    if faith_result.get("flagged"):
        reply += (
            "\n\n---\n"
            "⚠️ *Please verify any specific dates or policy details above with the "
            "CGU Academic Calendar or your program coordinator, as information may "
            "have changed since our knowledge base was last updated.*"
        )

    return ChatResponse(
        reply=reply,
        sources=chunks,
        hallucination_score=faith_result.get("overall_faithfulness_score"),
        verdict=faith_result.get("overall_verdict"),
        flagged=faith_result.get("flagged", False),
        is_deadline_query=deadline_detected,
    )


# --- Health check ---

@app.get("/health")
def health():
    return {"status": "ok", "service": "CISAT Advising Chatbot API"}
