#!/usr/bin/env python3
"""Export code-defined reference data to a JSON bundle for the frontend.

The Python seed constants (metric_type_mapping.py, achievement/definitions.py,
mood.py) are the canonical source of truth. This script projects them into a
single versioned JSON that the SPA bundles and seeds into Dexie on first launch
(empty store), so the app renders its metric/achievement structure without a
first full sync — required for Local Mode and a faster first paint.

Usage:
    uv run python scripts/export_reference.py [output_path]

Writes JSON to the given path (default: frontend/src/lib/reference/reference.json).
"""
import json
import sys
from pathlib import Path

from salus.models import DataType
from salus.services.achievement.definitions import ACHIEVEMENT_DEFINITIONS
from salus.services.lab_reference import LAB_MARKERS
from salus.services.metric_type_mapping import (
    DEFAULT_METRIC_PREFERENCES,
    METRIC_DEFINITIONS,
    METRIC_GROUPS,
)
from salus.services.mood import DEFAULT_MOOD_TAGS

DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "frontend" / "src" / "lib" / "reference" / "reference.json"


def _metric_groups() -> list[dict]:
    return [
        {
            "key": g["key"],
            "name": g["name"],
            "icon": g["icon"],
            "description": None,
            "input_mode": g.get("input_mode", "individual"),
        }
        for g in METRIC_GROUPS
    ]


def _metric_definitions() -> list[dict]:
    out = []
    for md in METRIC_DEFINITIONS:
        data_type = md["data_type"]
        out.append({
            "code": md["code"],
            "name": md["name"],
            "unit": md.get("unit", ""),
            "data_type": data_type.value if isinstance(data_type, DataType) else str(data_type),
            "source_data_type": md.get("source_data_type"),
            "group_key": md.get("group_key"),
            "description": None,
            "sort_order": md.get("sort_order", 0),
            "min_value": md.get("min_value"),
            "max_value": md.get("max_value"),
        })
    return out


def _achievement_definitions() -> list[dict]:
    return [
        {
            "code": ad["code"],
            "title": ad["title"],
            "description": ad["description"],
            "icon": ad.get("icon", "emoji-events"),
            "tier": ad.get("tier", "bronze"),
            "category": ad.get("category", "tracking"),
            "condition_type": ad.get("condition_type", "count"),
            "condition_config": ad.get("condition_config", "{}"),
            "is_hidden": ad.get("is_hidden", False),
            "sort_order": ad.get("sort_order", 0),
        }
        for ad in ACHIEVEMENT_DEFINITIONS
    ]


def _mood_tags() -> list[dict]:
    return [
        {
            "code": t["code"],
            "label": t["label"],
            "emoji": t["emoji"],
            "category": t["category"],
            "is_system": True,
        }
        for t in DEFAULT_MOOD_TAGS
    ]


def _lab_markers() -> list[dict]:
    return [
        {
            "code": m["code"],
            "category": m["category"],
            "reference_low": m.get("reference_low"),
            "reference_high": m.get("reference_high"),
            "optimal_low": m.get("optimal_low"),
            "optimal_high": m.get("optimal_high"),
            "description": m.get("description"),
        }
        for m in LAB_MARKERS
    ]


def _metric_preference_defaults() -> list[dict]:
    return [
        {
            "code": p["code"],
            "color": p.get("color", "#4f46e5"),
            "icon": p.get("icon", "monitoring"),
            "widget_size": p.get("widget_size", "medium"),
            "widget_enabled": p.get("widget_enabled", False),
            "enabled": p.get("enabled", True),
            "position": p.get("position", 0),
        }
        for p in DEFAULT_METRIC_PREFERENCES
    ]


def build_reference() -> dict:
    return {
        "version": 1,
        "metric_group": _metric_groups(),
        "metric_definition": _metric_definitions(),
        "achievement_definition": _achievement_definitions(),
        "mood_tag": _mood_tags(),
        "lab_marker": _lab_markers(),
        "metric_preference_defaults": _metric_preference_defaults(),
    }


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_reference(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Reference data written to {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
