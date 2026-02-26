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
2. System shows course history and degree-progress summary.
3. System highlights requirement gaps.
4. System recommends next courses.
5. Recommendations go through advisor review checkpoints.
6. Embedded chatbot answers advising and deadline questions using a local knowledge base.

## Safety and Trust Features

- Retrieval-Augmented Generation (RAG): Answers are grounded in program documents.
- Hallucination checks: Every response is evaluated for faithfulness.
- Deadline-aware prompting: Adds stricter rules for deadline-related questions.
- Human-in-the-loop checkpoints: Students and advisors review before decisions move forward.

## Tech Stack

- Frontend: React 18, TypeScript, Vite, Tailwind CSS v4
- Backend: FastAPI, OpenAI API, ChromaDB, PyPDF
- AI Models:
  - `gpt-4o-mini` for response generation and evaluation
  - `text-embedding-3-small` for semantic retrieval

## Architecture (High Level)

1. Frontend sends user query to `POST /api/chat`.
2. Backend detects if the query is deadline-related.
3. Backend retrieves relevant knowledge chunks from ChromaDB.
4. Backend generates response with OpenAI.
5. Backend runs hallucination-faithfulness evaluation and returns metadata.

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
- Frontend (optional):
  - `VITE_API_URL` (default: `http://localhost:8000`)
  - `VITE_CHATBOT_URL` (default points to hosted ChatGPT assistant URL)

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
- `sources`
- `hallucination_score`
- `verdict`
- `flagged`
- `is_deadline_query`

## Current Scope and Limitations

- The multi-step advising UI is currently a demo workflow with mocked progression in parts.
- Knowledge-base quality depends on document freshness and completeness.
- Not production-hardened for institutional FERPA/compliance deployment yet.

## Future Improvements

- Real document parsing pipeline for uploaded planning sheets
- Advisor portal + approval workflow integration
- Authentication/SSO and role-based access control
- Better observability and evaluation dashboards

## Author

Aahish Sunar
