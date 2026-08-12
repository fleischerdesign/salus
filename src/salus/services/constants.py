"""Shared domain constants — single source of truth for repeated values."""

# Sync push deduplication window (hours)
DEDUP_TTL_HOURS = 24

# Time-series query windows (days)
DAY_WINDOWS: dict[str, int] = {
    "7d": 7,
    "30d": 30,
    "90d": 90,
    "1y": 365,
}

# Batch/chunk sizes for SQLite parameter limits and sync batches
SYNC_BATCH_SIZE = 500
SYNC_BATCH_SIZE_HIGH_VOLUME = 2000
INGEST_CHUNK_SIZE = 900

# Workout autoregulation defaults
DEFAULT_RPE = 8.0
DEFAULT_REST_SECONDS = 90
DEFAULT_TARGET_SETS = 3
DEFAULT_TARGET_REPS = 8
DEFAULT_TARGET_RPE = 8.0
