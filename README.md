# CISAT Academic Advising Chatbot

An AI-assisted advising experience that helps CISAT MS students understand degree progress, choose next courses, and avoid deadline mistakes, while keeping faculty in the loop.

## Why This Project Matters

Students often struggle to answer three high-stakes questions:
- Am I on track to graduate?
- What should I take next?
- What happens if I miss a deadline?

This project turns those questions into a guided workflow and a chatbot that gives grounded, plain-language answers.

## Meaning and Impact (Non-Technical Summary)

- Students: Get faster clarity on progress, remaining requirements, and deadlines.
- Advisors: Spend less time on repetitive questions and more time on high-value mentoring.
- University programs: Improve advising consistency with AI support plus human checkpoints.

This is not "AI replacing advisors." It is AI helping students prepare better questions and helping advisors review recommendations faster.

## What the Product Does

1. Student uploads a planning sheet (demo flow).
2. System walks through a demo course-history and degree-progress summary.
3. System previews requirement gaps and next-course suggestions.
4. Demo recommendations and advisor checkpoints are shown in the UI.
5. Embedded chatbot answers advising questions using a local knowledge base.

## Safety and Trust Features

- Retrieval-Augmented Generation (RAG): Answers are grounded in program documents.
- Optional hallucination checks: Responses can be evaluated for faithfulness when explicitly enabled.
- Deadline-aware prompting: Adds stricter rules for deadline-related questions.
- Demo human-in-the-loop checkpoints: The UI previews where student and advisor review could happen in a future version.

## Tech Stack

- Frontend: React 18, TypeScript, Vite, Tailwind CSS v4
- Backend: FastAPI, OpenAI API, ChromaDB, PyPDF
- AI Models:
  - `gpt-4o-mini` for response generation and evaluation
  - `text-embedding-3-small` for semantic retrieval

## Architecture (High Level)

1. Frontend sends user query to `POST /api/chat`.
2. Backend detects if the query is deadline-related and returns a safe fallback if the deadline source is still incomplete.
3. Backend retrieves relevant knowledge chunks from ChromaDB.
4. Backend generates response with OpenAI.
5. Backend can optionally run hallucination-faithfulness evaluation before returning a reply.

## Project Structure

```text
.
├── src/                          # React frontend
├── backend/
│   ├── main.py                   # FastAPI app
│   ├── rag.py                    # RAG indexing + retrieval
│   ├── knowledge_base/           # Advising/deadline source docs
│   └── evaluation/               # Hallucination + deadline logic
├── SETUP.md
└── README.md
```

## Local Setup

### Prerequisites

- Node.js 18+
- Python 3.10+
- OpenAI API key

### 1. Frontend

```bash
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Run backend:

```bash
uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`.

## Environment Variables

- Backend:
  - `OPENAI_API_KEY` (required)
  - `DEMO_USERNAME` and `DEMO_PASSWORD` (optional shared browser login for quick demos)
  - `CORS_ORIGINS` (optional)
  - `ALLOWED_HOSTS` (optional)
  - `DEFAULT_RATE_LIMIT` (optional)
  - `CHAT_RATE_LIMIT` (optional)
  - `ENABLE_API_DOCS` (optional, default: disabled)
  - `ENABLE_RESPONSE_EVALUATION` (optional, default: disabled)
- Frontend (optional):
  - `VITE_API_URL` (optional override; default is same-origin, with the Vite dev proxy used locally)

## API

### `POST /api/chat`

Request body:

```json
{
  "message": "When is the graduation application deadline?",
  "history": [{ "role": "user", "content": "..." }]
}
```

Response includes:
- `reply`
- `flagged`
- `is_deadline_query`

## Current Scope and Limitations

- The multi-step advising UI is currently a demo workflow with mocked progression in parts.
- While the current-semester deadline knowledge base still contains placeholders, deadline queries return a safe fallback instead of a date answer.
- Not production-hardened for institutional FERPA/compliance deployment yet.

## Quick Demo Deployment

Fastest path:

1. Push this repo to GitHub.
2. In Render, create a new Blueprint from the repo.
3. Render will read [render.yaml](/Users/aahishsunar/Desktop/CGU/Academic%20Advising%20Chatbot/render.yaml).
4. Set:
   - `OPENAI_API_KEY`
   - `DEMO_USERNAME`
   - `DEMO_PASSWORD`
5. Open the deployed URL and sign in with the shared browser prompt.

Notes:
- The backend now serves the built React app, so one URL handles both UI and API.
- `DEMO_USERNAME` and `DEMO_PASSWORD` are only for short-lived demo access, not real production auth.

## Preferred Demo Deployment

For this codebase, the cleaner quick setup is:

- Vercel for the frontend
- Railway for the backend

Why this split:
- Vercel is a good fit for the Vite frontend
- Railway is a better fit for the current FastAPI + local Chroma backend than Vercel Functions

### Vercel Frontend

- Import the repo into Vercel
- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Set `VITE_API_URL=https://your-railway-backend.up.railway.app`
- `vercel.json` is already included for SPA routing and basic headers

### Railway Backend

- Import the same repo into Railway
- Railway will use [Dockerfile](/Users/aahishsunar/Desktop/CGU/Academic%20Advising%20Chatbot/Dockerfile#L1)
- Set:
  - `OPENAI_API_KEY`
  - `CORS_ORIGINS=https://your-vercel-app.vercel.app`
  - `ALLOWED_HOSTS=your-railway-backend.up.railway.app`
  - `ENABLE_API_DOCS=0`
  - `ENABLE_RESPONSE_EVALUATION=0`

Optional:
- `DEMO_USERNAME`
- `DEMO_PASSWORD`

Recommendation:
- For quick boss/team testing, skip backend Basic Auth unless you really need it. It protects the API, but it is awkward when the frontend and backend are on separate domains.

## Future Improvements

- Real document parsing pipeline for uploaded planning sheets
- Advisor portal + approval workflow integration
- Authentication/SSO and role-based access control
- Better observability and evaluation dashboards

## Author

Aahish Sunar
