# AGENTS.md

This file gives AI agents durable project context for this repository.

Sync rule: `AGENTS.md` and `CLAUDE.md` must stay in sync. When one file is updated, update the other in the same change. The project-truth sections below should remain text-identical unless there is a deliberate reason to change both.

Last updated: 2026-03-10

## Project Purpose

This repository is an MVP academic advising assistant for CISAT MS students at Claremont Graduate University.

Current user-facing goals:
- Let a student walk through a demo advising workflow for uploads, progress review, gap analysis, recommendations, and advisor checkpoints.
- Let a student use a real chat panel that sends questions to a FastAPI backend.
- Answer deadline and advising questions using a local knowledge base plus OpenAI-backed retrieval and evaluation.

## Current Launch Goal

Planned near-term launch assumption:
- Public anonymous web app
- No real auth or SSO before launch

This means agents should prioritize:
- Public-internet abuse resistance
- Cost control on AI-backed endpoints
- Clear demo labeling
- Avoiding false product claims

## Actual Architecture And Entry Points

The architecture is now a "Headless Assistant" model.

Frontend:
- Entry point: `src/main.tsx`
- App shell: `src/app/App.tsx`
- Router: `src/app/routes.ts`
- Runtime config: `src/config.ts`
- Real backend integration currently happens in `src/app/components/ChatPanel.tsx` and `src/app/screens/Upload.tsx`.

Backend:
- Entry point: `backend/main.py`
- OpenAI client wrapper: `backend/openai_client.py`
- Assistant management: `backend/assistant.py` (handles creation, configuration, and tool definitions)

Current API surface in repo:
- `POST /api/upload-plan`
- `POST /api/chat`
- `GET /health`

Config locations:
- Frontend env config via `VITE_API_URL` in `src/config.ts`
- Backend secret via `backend/.env` / `OPENAI_API_KEY`
- Assistant ID is stored in `backend/assistant.json` or `OPENAI_ASSISTANT_ID` env var.
- Other backend runtime controls via `backend/main.py`.

## Implemented Vs Demo-Only

Implemented for real:
- React app routing and screen transitions.
- Floating chatbot button and chat panel.
- **File upload to backend (`/api/upload-plan`).**
- **Backend uploads file to OpenAI and creates a Thread.**
- **Chat panel uses the new Assistants API via `/api/chat`.**
- Frontend `fetch()` calls to backend.
- FastAPI endpoints for upload and chat with request validation.
- Prompt-injection string filtering.
- **OpenAI Assistant creation and persistence.**
- **Assistant uses `file_search` for retrieval.**
- **Assistant uses `function_calling` for UI navigation and simulated backend actions.**
- Backend handles polling the Assistant Run status.
- Basic rate limiting, security middleware, and optional Basic Auth.

Mostly mocked or demo-only:
- The `email_supervisor` function only logs to the console; it doesn't send a real email.
- Course history, gap analysis, recommendations, etc., are still mostly static demo screens, but can now be triggered by the Assistant.
- No auth or SSO exists.

Agents must not describe mocked flows as implemented features.

## Current Progress Snapshot

What exists today:
- The application has been migrated from a manual RAG pipeline to the OpenAI Assistants API.
- The backend is now a "headless" router that manages Assistant runs.
- The frontend uploads a file and then interacts with the Assistant through threads.
- Document retrieval is handled by OpenAI's `file_search` tool.
- The Assistant can trigger UI navigation and backend actions using Function Calling.
- The old, complex RAG-related code (`rag.py`, `chromadb`, etc.) has been removed.

What is missing for a production-like launch:
- Authentication / authorization.
- Real implementation of the `email_supervisor` tool.
- Real student-specific state and persistence.
- Full dynamic population of the UI screens (GapAnalysis, etc.) from `extracted_data`.
- Formal observability and deployment hardening.

## Review Snapshot And Launch Priorities

Highest-priority issues before public sharing:
1. `POST /api/chat` is anonymous and connected to paid model calls, so abuse can create direct cost and availability risk.
2. The `email_supervisor` function is just a log entry. It needs a real email transport.
3. The UI, while triggerable by the assistant, still relies heavily on static data.
4. FastAPI docs are disabled by default now; keep them off in production.
5. Demo Basic Auth is only appropriate for short-lived internal testing.

Important medium-priority concerns:
- No tests are present for the new architecture.
- Python dependencies are pinned but there is no visible lockfile or audit workflow.
- README, SETUP, `AGENTS.md`, and `CLAUDE.md` need to stay synced.

## Working Conventions For Future Agents

- Start from repo truth, not README marketing.
- The new architecture is simpler. The core logic is in `backend/main.py` (`chat` endpoint) and `backend/assistant.py`.
- For this repo, the most security-sensitive files are now `backend/main.py` and `backend/assistant.py`.
- If architecture or behavior changes, update `README.md`, `SETUP.md`, `AGENTS.md`, and `CLAUDE.md` together when relevant.

## Recommended Near-Term Priorities

Before public sharing:
- Tighten abuse controls on `/api/chat` and `/api/upload-plan`.
- Implement the `email_supervisor` tool to send real emails.
- Connect the `extracted_data` from the `trigger_ui_navigation` tool to the frontend components to make them dynamic.
- Document deployment/security assumptions.
- Add smoke tests for the new API endpoints.

## Known Documentation Drift

- The response shape of `/api/chat` has changed significantly. All docs should reflect this.
- The removal of the local knowledge base and the RAG pipeline should be noted in all architectural docs.
