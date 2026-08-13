export NIXPKGS_ALLOW_UNFREE := "1"
export NIXPKGS_ACCEPT_ANDROID_SDK_LICENSE := "1"

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

@build-apk:
    just build-frontend
    cd frontend && npx cap sync android
    cd frontend/android && ./gradlew --stop && ./gradlew assembleDebug
    @echo "APK built successfully: frontend/android/app/build/outputs/apk/debug/app-debug.apk"

@install-apk:
    just build-apk
    adb install -r frontend/android/app/build/outputs/apk/debug/app-debug.apk
    @echo "Salus APK successfully installed on connected Android device!"

# --- Install / Sync ---

@install-frontend:
    cd frontend && npm install

@sync-backend:
    uv sync

# --- Schema ---

@schema-frontend:
    cd frontend && npm run gen-schema

@export-reference:
    uv run python scripts/export_reference.py

# --- Dev seed ---

@seed *ARGS:
    uv run python tools/seed_dev.py {{ARGS}}

@seed-dev *ARGS:
    uv run python tools/seed_dev.py {{ARGS}}

# --- Full check ---

@check: lint-backend lint-frontend typecheck-backend typecheck-frontend test-backend test-frontend
