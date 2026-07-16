default:
    @just --list

# --- Development ---

@dev-backend:
    uv run uvicorn src.salus.main:app --reload

@dev-frontend:
    cd frontend && npm run dev

# --- Testing ---

@test-backend *ARGS:
    uv run pytest -v {{ARGS}}

@test-frontend:
    cd frontend && npm run test

# --- Lint ---

@lint-backend:
    uv run ruff check src/

@lint-frontend:
    cd frontend && npm run lint

# --- Typecheck ---

@typecheck-backend:
    uv run pyright src/

@typecheck-frontend:
    cd frontend && npm run check

# --- Format ---

@format-frontend:
    cd frontend && npm run format

# --- Build ---

@build-frontend:
    cd frontend && npm run build

# --- Install / Sync ---

@install-frontend:
    cd frontend && npm install

@sync-backend:
    uv sync

# --- Schema ---

@schema-frontend:
    cd frontend && npm run gen-schema

# --- Dev seed ---

@seed-dev:
    python3 tools/seed_dev.py

# --- Full check ---

@check: lint-backend lint-frontend typecheck-backend typecheck-frontend test-backend test-frontend
