"""Standard mood tags seeded on system startup."""

DEFAULT_MOOD_TAGS: list[dict[str, str]] = [
    {"code": "energetic", "label": "Energetic", "emoji": "⚡", "category": "positive"},
    {"code": "happy", "label": "Happy", "emoji": "😊", "category": "positive"},
    {"code": "productive", "label": "Productive", "emoji": "✅", "category": "positive"},
    {"code": "grateful", "label": "Grateful", "emoji": "🙏", "category": "positive"},
    {"code": "calm", "label": "Calm", "emoji": "🧘", "category": "positive"},
    {"code": "okay", "label": "Okay", "emoji": "😐", "category": "neutral"},
    {"code": "tired", "label": "Tired", "emoji": "😴", "category": "negative"},
    {"code": "stressed", "label": "Stressed", "emoji": "😰", "category": "negative"},
    {"code": "anxious", "label": "Anxious", "emoji": "😟", "category": "negative"},
    {"code": "sad", "label": "Sad", "emoji": "😢", "category": "negative"},
    {"code": "frustrated", "label": "Frustrated", "emoji": "😤", "category": "negative"},
    {"code": "sick", "label": "Sick", "emoji": "🤒", "category": "negative"},
]
