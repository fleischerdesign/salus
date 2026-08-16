"""Shared domain constants — single source of truth for repeated values."""

# Sync push deduplication window (hours)
DEDUP_TTL_HOURS = 24

# Batch size for sync batches
SYNC_BATCH_SIZE = 500

# Measurement source channel for manually entered data
SOURCE_MANUAL = "manual"

# Measurement source channel for device health sources (Health Connect bulk replication)
SOURCE_HEALTH_CONNECT = "health_connect"

# Food item sources (food_item.source)
SOURCE_SYSTEM = "system"
SOURCE_OPENFOODFACTS = "openfoodfacts"

# Workout autoregulation defaults
DEFAULT_RPE = 8.0
DEFAULT_REST_SECONDS = 90
DEFAULT_TARGET_SETS = 3
DEFAULT_TARGET_REPS = 8
DEFAULT_TARGET_RPE = 8.0
