"""Progression schemes — how a program proposes targets (ADR-014).

A scheme turns a ``ProgressionContext`` (base targets + recent performance)
into a list of suggested targets. Three schemes exist today:

- ``NoneProgressionScheme`` — standard targets, no progression.
- ``LinearProgressionScheme`` — progressive overload from the last load.
- ``AutoregulatedProgressionScheme`` — recovery-based targets.

All schemes are stateless with respect to the database: the answer is always
recomputed from the context (history), never persisted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from salus.services.constants import DEFAULT_LINEAR_INCREMENT, DEFAULT_RPE

if TYPE_CHECKING:
    from salus.models.workout import Exercise, WorkoutExercise
    from salus.services.workout.autoregulation import AutoregulationService


@dataclass
class ProgressionContext:
    """Everything a scheme needs to propose targets for one workout."""

    user_id: str
    date_str: str | None
    exercises: list[tuple["WorkoutExercise", "Exercise"]]
    last_weights: dict[str, float]
    last_reps: dict[str, int]
    last_rpes: dict[str, float | None]


class ProgressionScheme(Protocol):
    """Computes suggested targets for a workout's exercises."""

    def compute_targets(self, ctx: ProgressionContext) -> list[dict]: ...


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


class NoneProgressionScheme:
    """Standard targets — no progression applied."""

    def compute_targets(self, ctx: ProgressionContext) -> list[dict]:
        return [
            {
                "exercise_id": ex.id,
                "name": ex.name,
                "suggested_sets": workout_ex.target_sets,
                "suggested_reps": workout_ex.target_reps,
                "suggested_rpe": workout_ex.target_rpe or DEFAULT_RPE,
                "weight_multiplier": 1.0,
                "is_autoreg_exempt": True,
                "reason": "Progression disabled for this program.",
            }
            for workout_ex, ex in ctx.exercises
        ]


class LinearProgressionScheme:
    """Progressive overload — increment the load on a met target."""

    def compute_targets(self, ctx: ProgressionContext) -> list[dict]:
        return [
            {
                "exercise_id": ex.id,
                "name": ex.name,
                "suggested_sets": workout_ex.target_sets,
                "suggested_reps": workout_ex.target_reps,
                "suggested_rpe": workout_ex.target_rpe or DEFAULT_RPE,
                "weight_multiplier": 1.0,
                "is_autoreg_exempt": workout_ex.is_autoreg_exempt,
                "suggested_weight": suggest_linear_weight(
                    last_weight=ctx.last_weights.get(workout_ex.exercise_id),
                    target_reps=workout_ex.target_reps,
                    target_rpe=workout_ex.target_rpe,
                    last_reps=ctx.last_reps.get(workout_ex.exercise_id),
                    last_rpe=ctx.last_rpes.get(workout_ex.exercise_id),
                    increment=DEFAULT_LINEAR_INCREMENT,
                ),
                "reason": "Linear progression from last performance.",
            }
            for workout_ex, ex in ctx.exercises
        ]


class AutoregulatedProgressionScheme:
    """Recovery-based targets — delegates to the autoregulation service."""

    def __init__(self, autoreg_svc: "AutoregulationService") -> None:
        self.autoreg_svc = autoreg_svc

    def compute_targets(self, ctx: ProgressionContext) -> list[dict]:
        return self.autoreg_svc.get_autoregulated_targets(
            user_id=ctx.user_id,
            exercises_with_targets=ctx.exercises,
            date_str=ctx.date_str,
        )
