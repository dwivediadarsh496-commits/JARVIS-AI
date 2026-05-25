# JARVIS AI

JARVIS AI transforms the original local Python voice assistant into a full-stack
AI SaaS starter with a Next.js dashboard, FastAPI streaming backend, voice mode,
AI tools, Clerk authentication, PostgreSQL, Redis, Docker, and CI.

## What Is Included

- Next.js 15 frontend with App Router, TypeScript, Tailwind, Clerk, Zustand, React Query, streaming chat UI, voice UI, tools, settings, and profile pages.
- FastAPI backend with SSE chat streaming, OpenAI and Gemini provider switching, voice transcription/synthesis endpoints, WebSocket voice text responses, tool endpoints, SQLAlchemy models, and Redis cache service.
- Preserved original script at `python-core/main.py`.
- Docker Compose stack for frontend, backend, PostgreSQL, Redis, and Nginx.
- GitHub Actions workflow for linting, type checks, tests, and Docker builds.

## Repository Layout

```text
jarvis/
├── frontend/             # Next.js 15 SaaS frontend
├── backend/              # FastAPI backend
├── python-core/          # Original Python assistant script
├── docs/                 # Architecture notes
├── nginx/                # Reverse proxy config
├── .github/workflows/    # CI/CD workflow
├── docker-compose.yml
├── Dockerfile.frontend
├── Dockerfile.backend
└── .env.example
```

## Required Services

Create `.env` files from the examples and provide the keys you want to use:

- OpenAI API key for GPT chat, Whisper transcription, and TTS.
- Google Gemini API key for Gemini chat models.
- Clerk publishable and secret keys for authentication.
- PostgreSQL and Redis connection strings. Docker Compose provides local services.

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`, with docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

The app runs at `http://localhost:3000`.

## Docker

```bash
copy .env.example .env
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Nginx: `http://localhost`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Verification

```bash
cd frontend
npm run lint
npm run type-check
npm run build

cd ../backend
ruff check .
pytest
```

## Notes

The backend includes an in-memory chat session store for local demo mode plus
SQLAlchemy models for the production database schema. Wire the chat endpoints to
the database layer when you are ready to persist sessions server-side.
