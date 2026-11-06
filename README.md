# CodePilot AI

AI-powered code review and repository assistant. Connect GitHub, import a repo, chat with it using
retrieval-augmented generation (RAG), get AI code reviews, and generate a README — all in one app.

Built as a learning/portfolio project. See `backend/app/` for the FastAPI service and `frontend/` for
the Next.js app.

## Features

- Email/password auth (JWT, Argon2 password hashing)
- GitHub OAuth, repository import and sync
- File explorer with syntax highlighting and search
- Incremental indexing pipeline (chunk → embed → ChromaDB)
- Repository chat (RAG) with streamed answers and cited sources
- AI code review with structured, severity-tagged findings
- AI README generator with Markdown preview/export
- Dashboard stats and account settings

## Tech stack

**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic, ChromaDB, Sentence Transformers / Gemini embeddings, Gemini LLM
**Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, React Query, React Hook Form + Zod

## Quick start (macOS)

You'll need: **Python 3.12+**, **Node.js 20+**, and **PostgreSQL** (via Homebrew or Docker).

### 1. Clone and set up Postgres

```bash
# Option A: Homebrew
brew install postgresql@16
brew services start postgresql@16
createuser -s codepilot
psql postgres -c "ALTER USER codepilot WITH PASSWORD 'codepilot';"
createdb -O codepilot codepilot

# Option B: just the database, via Docker
docker run --name codepilot-db -e POSTGRES_USER=codepilot -e POSTGRES_PASSWORD=codepilot \
  -e POSTGRES_DB=codepilot -p 5432:5432 -d postgres:16-alpine
```

### 2. Get a Gemini API key

Go to [Google AI Studio](https://aistudio.google.com/apikey) and create a free API key.

### 3. Create a GitHub OAuth App

GitHub → **Settings → Developer settings → OAuth Apps → New OAuth App**:
- Homepage URL: `http://localhost:3000`
- Authorization callback URL: `http://localhost:8000/api/github/callback`

Copy the **Client ID** and generate a **Client Secret**.

### 4. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# On Apple Silicon, PyTorch's CPU wheel installs automatically with the line above.

cp .env.example .env
```

Edit `backend/.env`:
```
DATABASE_URL=postgresql+psycopg://codepilot:codepilot@localhost:5432/codepilot
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
ENCRYPTION_KEY=<run: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
GITHUB_CLIENT_ID=<from step 3>
GITHUB_CLIENT_SECRET=<from step 3>
GEMINI_API_KEY=<from step 2>
```

Run migrations and start the API:
```bash
alembic upgrade head
uvicorn app.main:app --reload
```

Check it: `curl http://localhost:8000/api/health` → `{"status":"ok","database":"connected"}`
API docs: http://localhost:8000/docs

### 5. Frontend setup

In a new terminal:
```bash
cd frontend
npm install
cp .env.local.example .env.local   # already defaults to http://localhost:8000/api
npm run dev
```

Open http://localhost:3000 — register an account, connect GitHub, import a repo, and go.

### 6. Run the backend test suite (optional but recommended)

```bash
# create a separate test database once:
createdb -O codepilot codepilot_test   # or the Docker equivalent

cd backend
pip install -r requirements-dev.txt
pytest -v
```

All 124 tests should pass (they run against the real test database with fake AI/GitHub providers,
so no API keys or network access are needed to run them).

## Running with Docker instead

```bash
cp backend/.env.example backend/.env   # fill in SECRET_KEY, ENCRYPTION_KEY, GitHub + Gemini values
docker compose up --build
```

This starts Postgres, runs migrations automatically, and serves the API on :8000 and the app on :3000.

## Notes on the embedding provider

By default (`EMBEDDING_PROVIDER=local` in `.env`), the backend downloads a small Sentence
Transformers model (~90MB) on first use and runs it on the server's CPU — free, but uses about 1GB
of RAM. For a lighter footprint, set `EMBEDDING_PROVIDER=gemini` to use Gemini's hosted embeddings
instead (uses your `GEMINI_API_KEY`). Changing this setting triggers an automatic full re-index of
already-imported repositories.

## Project structure

```
codepilot-ai/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers (HTTP only)
│   │   ├── core/           # config, security, exceptions
│   │   ├── models/         # SQLAlchemy tables
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── services/       # business logic
│   │   ├── repositories/   # database queries
│   │   ├── ai/             # chunking, embeddings, RAG, LLM, prompts
│   │   └── database/       # engine, session, Base
│   ├── alembic/            # migrations
│   └── tests/              # pytest suite (124 tests)
└── frontend/
    ├── app/                # Next.js routes
    ├── components/         # UI components
    ├── hooks/              # React Query hooks
    ├── services/           # typed API client functions
    └── types/
```

## Known limitations (intentional, for a learning project)

- Background jobs (indexing, reviews) use FastAPI's `BackgroundTasks`, which run in-process and are
  lost if the server restarts mid-job (the app detects and marks these "failed" on startup so they
  can be retried). A production version would use a real task queue (e.g. Celery + Redis).
- Email verification and "forgot password" are not implemented (marked optional in the original spec).
- GitHub OAuth scope (`public_repo` by default) grants write access by GitHub's own design; a GitHub
  App would allow finer-grained, read-only permissions.
