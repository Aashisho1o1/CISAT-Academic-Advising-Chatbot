# CLAUDE.md

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

Frontend:
- Entry point: `src/main.tsx`
- App shell: `src/app/App.tsx`
- Router: `src/app/routes.ts`
- Runtime config: `src/config.ts`
- Real backend integration currently happens in `src/app/components/ChatPanel.tsx`

Backend:
- Entry point: `backend/main.py`
- OpenAI client wrapper: `backend/openai_client.py`
- Retrieval pipeline: `backend/rag.py`
- Deadline logic: `backend/evaluation/deadline_router.py`
- Deadline clarification logic: `backend/evaluation/deadline_personalizer.py`
- Prompt definitions: `backend/evaluation/deadline_prompts.py`
- Hallucination evaluation/logging: `backend/evaluation/hallucination_detector.py`

Current API surface in repo:
- `POST /api/chat`
- `GET /health`

Config locations:
- Frontend env config via `VITE_API_URL` in `src/config.ts`
- Backend secret via `backend/.env` / `OPENAI_API_KEY`
- Backend runtime controls via `backend/main.py`:
  - `DEMO_USERNAME`
  - `DEMO_PASSWORD`
  - `CORS_ORIGINS`
  - `ALLOWED_HOSTS`
  - `DEFAULT_RATE_LIMIT`
  - `CHAT_RATE_LIMIT`
  - `ENABLE_API_DOCS`
  - `ENABLE_RESPONSE_EVALUATION`

## Implemented Vs Demo-Only

Implemented for real:
- React app routing and screen transitions
- Floating chatbot button and chat panel
- Frontend `fetch()` call to backend chat API
- Frontend same-origin API default for single-service deployment
- FastAPI chat endpoint with request validation
- Prompt-injection string filtering
- Deadline query detection and clarifying question logic
- Safe fallback for deadline queries while the deadline knowledge base still contains placeholders
- Chroma-backed retrieval over local knowledge base docs
- OpenAI response generation
- Optional OpenAI-based faithfulness evaluation when explicitly enabled
- Redacted evaluation logging
- Basic rate limiting if `slowapi` imports successfully
- Trusted host and scoped CORS middleware
- Optional shared browser Basic Auth for short-lived demo access
- FastAPI can serve the built frontend from `dist/`

Mostly mocked or demo-only:
- Upload flow does not send files to the backend
- Processing screen uses a timer, not real document processing
- Course history, gap analysis, recommendations, advisor approval, and final action-plan screens are hardcoded demo data
- No auth or SSO exists
- Advisor email/review flow is not implemented
- Portal save, download report, and email report actions are not implemented

Agents must not describe mocked flows as implemented features.

## Current Progress Snapshot

What exists today:
- Frontend production build succeeds
- Backend Python files compile
- The chat subsystem is the main real product feature
- The multi-step advising workflow is a polished demo around static data
- Deadline queries fail closed until the deadline knowledge base is fully completed
- The repo now supports a single-service demo deployment path
- The repo now also supports a split deployment path: Vercel frontend + Railway backend

What is missing for a production-like launch:
- Authentication / authorization
- Real upload processing
- Real student-specific state and persistence
- Real advisor workflow
- Formal observability and deployment hardening
- Clear production/development configuration split

## Review Snapshot And Launch Priorities

Highest-priority issues before public sharing:
1. `POST /api/chat` is anonymous and connected to paid model calls, so abuse can create direct cost and availability risk.
2. The main deadline knowledge-base document still contains placeholder values such as `[ENTER DATE]`, `[DATE]`, and `[ENTER GPA REQUIREMENT]`, so full deadline answering remains intentionally disabled until that data is completed.
3. FastAPI docs are disabled by default now; keep them off in production unless there is an explicit reason to expose them.
4. Most of the multi-step workflow is still a demo, so new UI copy and docs must keep that boundary clear.
5. Demo Basic Auth is intentionally lightweight and only appropriate for short-lived internal testing, not real production security.

Important medium-priority concerns:
- No tests are present
- Python dependencies are pinned but there is no visible lockfile or audit workflow
- README, SETUP, `AGENTS.md`, and `CLAUDE.md` need to stay synced whenever launch behavior changes
- Some dev-only/demo copy can still drift if it is not centralized
- The frontend contains some unused/demo components that increase cognitive load
- Chat history and model output handling are simple and workable, but not yet designed for scale or strong observability

## Working Conventions For Future Agents

- Start from repo truth, not README marketing.
- Keep code and explanations lean, minimal, simple, and easy to review.
- Always state clearly whether a feature is real, partial, or mocked.
- When reviewing security, prioritize realistic public MVP risks before edge-case attacks.
- Do not add secrets to docs, code, examples, or commits.
- If architecture or behavior changes, update `README.md`, `SETUP.md`, `AGENTS.md`, and `CLAUDE.md` together when relevant.
- If one of `AGENTS.md` or `CLAUDE.md` changes, update the other in the same patch.
- Prefer simple, robust improvements over overengineering.
- Avoid large AI-style code dumps when a short, explicit change will do.
- For this repo, the most security-sensitive files are `backend/main.py`, `backend/rag.py`, `backend/openai_client.py`, and `backend/evaluation/hallucination_detector.py`.
- Treat public claims carefully: the current app is best presented as a demo workflow plus a real advising chat backend.

## Recommended Near-Term Priorities

Before public sharing:
- Tighten abuse controls on `/api/chat`
- Replace placeholder knowledge-base values with verified program data, then re-enable full deadline answering
- Keep FastAPI docs disabled in production unless explicitly needed
- Remove or clearly relabel unimplemented product claims
- Document deployment/security assumptions
- Add at least a small smoke-test/check workflow

Quick internal-demo path:
- Use the single-service deploy setup in `render.yaml`
- Set `DEMO_USERNAME` and `DEMO_PASSWORD`
- Keep `ENABLE_RESPONSE_EVALUATION=0` for lower cost and faster replies during team testing

Preferred split-demo path:
- Deploy the Vite frontend to Vercel using `vercel.json`
- Deploy the backend to Railway using the root `Dockerfile`
- Set `VITE_API_URL` on Vercel to the Railway backend URL
- Set `CORS_ORIGINS` on Railway to the Vercel frontend URL
- Keep `ENABLE_RESPONSE_EVALUATION=0` during quick demos

Can wait until after early feedback:
- Real upload parsing pipeline
- Auth/SSO
- Advisor portal
- Persistent student records
- Rich observability dashboards

## Known Documentation Drift

Likely drift to clean up soon:
- If the chat response shape changes, update `README.md`, `SETUP.md`, `AGENTS.md`, and `CLAUDE.md` together.
- If the deadline knowledge base is completed, update these docs to reflect that full deadline answers are re-enabled.
- If auth or real advisor workflow is added, remove demo-only wording only after the backend actually supports it.
