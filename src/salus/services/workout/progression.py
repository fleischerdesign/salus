"""Linear progression — the default progressive-overload scheme (ADR-014).

Pure rule: propose the next session's load from the athlete's most recent
completed performance. Reaching the rep target at or below the RPE target
increments the load; anything else holds it. No state is stored — the answer
is always recomputed from history.
"""


def suggest_linear_weight(
    last_weight: float | None,
    target_reps: int,
    target_rpe: float | None,
    last_reps: int | None,
    last_rpe: float | None,
    increment: float,
) -> float | None:
    """Return the proposed next weight, or None when there is no history.

    - No history (`last_weight is None`) → None (athlete picks a start weight).
    - No logged performance (`last_reps is None`) → hold the last weight.
    - Reps met and RPE at/below target (or unlogged) → last weight + increment.
    - Otherwise → hold the last weight.
    """
    if last_weight is None:
        return None
    if last_reps is None:
        return last_weight
    met_reps = last_reps >= target_reps
    met_rpe = target_rpe is None or last_rpe is None or last_rpe <= target_rpe
    return last_weight + increment if met_reps and met_rpe else last_weight
