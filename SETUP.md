# CISAT Academic Advising Chatbot - Setup Instructions

## Prerequisites

- Node.js 18+ installed
- Python 3.10+
- npm, pnpm, or yarn package manager
- OpenAI API key

## Installation Steps

1. Install frontend dependencies:

```bash
npm install
```

2. Run the frontend:

```bash
npm run dev
```

3. Install backend dependencies:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Create `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

5. Optional backend settings:

```env
CORS_ORIGINS=http://localhost:5173
ALLOWED_HOSTS=localhost,127.0.0.1
DEMO_USERNAME=demo
DEMO_PASSWORD=change-this
ENABLE_API_DOCS=1
ENABLE_RESPONSE_EVALUATION=1
```

6. Run the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

7. Open the app at `http://localhost:5173`

## Project Structure

- `/src/app/` - Main application code
- `/src/app/screens/` - Screen components
- `/src/app/components/` - Reusable components
- `/src/styles/` - CSS and theme files
- `/backend/` - FastAPI chat API, retrieval logic, and evaluation

## Notes

- The multi-step advising workflow is currently a demo walkthrough
- The live backend feature today is `POST /api/chat`
- FastAPI docs are disabled by default unless `ENABLE_API_DOCS=1`
- While the deadline knowledge base still has placeholder values, deadline questions return a safe fallback instead of a date answer
- If `DEMO_USERNAME` and `DEMO_PASSWORD` are set, the app uses a shared browser login suitable for short-lived internal demos

## Quick Split Deployment

Preferred fast demo setup:

- Frontend: Vercel
- Backend: Railway

Vercel:
- Import the repo as a Vite project
- Build command: `npm run build`
- Output directory: `dist`
- Set `VITE_API_URL=https://your-railway-backend.up.railway.app`

Railway:
- Deploy the same repo as a backend service
- Railway will use the root `Dockerfile`
- Set:
  - `OPENAI_API_KEY`
  - `CORS_ORIGINS=https://your-vercel-app.vercel.app`
  - `ALLOWED_HOSTS=your-railway-backend.up.railway.app`
  - `ENABLE_API_DOCS=0`
  - `ENABLE_RESPONSE_EVALUATION=0`

Optional:
- Add `DEMO_USERNAME` and `DEMO_PASSWORD` only if you want browser-level protection on the backend itself
- For a separate Vercel frontend, backend Basic Auth is usually more annoying than helpful during quick team testing
