# CISAT Academic Advising Chatbot

Full-stack academic advising assistant with:
- Flask backend API (`backend/`)
- React + TypeScript frontend (`frontend/`)
- SQLite storage for users, courses, and advising sheet extraction results

## Architecture

- Backend: session-based auth with Flask-Login, SQLAlchemy models, file upload + extraction endpoints.
- Frontend: route-guarded React app for login, advising sheet upload, and journey visualization.
- Data store: SQLite (default local dev DB).

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set required values in `backend/.env`:
- `SECRET_KEY`
- `SQLALCHEMY_DATABASE_URI`
- `VISION_AGENT_API_KEY`

Run backend:

```bash
cd backend
python app.py
```

Backend default URL: `http://localhost:8000`

## Frontend Setup

```bash
cd frontend
cp .env.example .env
npm ci
npm start
```

Frontend default URL: `http://localhost:3000`

`frontend/.env` supports:
- `REACT_APP_API_BASE_URL` (default `http://localhost:8000/api`)

## Database Migrations (Flask-Migrate)

Migration framework is initialized in `backend/migrations`.

Typical commands:

```bash
cd backend
python -m flask --app app db upgrade
python -m flask --app app db migrate -m "describe schema change"
python -m flask --app app db upgrade
```

For this repo, an initial baseline migration has been created and the existing development DB was stamped to head.

## Test Commands

Backend:

```bash
cd backend
python -m pytest -q tests
```

Frontend:

```bash
cd frontend
CI=true npm test -- --watchAll=false
npm run build
```

## Security Notes

- Do not commit `backend/.env`.
- Rotate any credentials previously committed to git history.
- Production deployment should set strong `SECRET_KEY`, controlled CORS origins, and proper HTTPS cookie settings.
- Upload endpoints enforce file type and size validation.

## CI

GitHub Actions workflow: `.github/workflows/ci.yml`
- backend dependency install + pytest
- frontend install + tests + build
