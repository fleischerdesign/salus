import type { ProgramWorkout } from '$lib/db/types';

export type ResolveReason = 'dated' | 'weekly' | 'rotation' | 'rest';

export interface ResolvedToday {
  workoutId: string | null;
  reason: ResolveReason;
}

/**
 * Resolve a program's workout for today: dated → weekly → rotation → rest.
 * Mirrors the backend resolve_today (schedule.py) client-side so the UI stays
 * Dexie-first and reactive.
 */
export function resolveToday(
  slots: ProgramWorkout[],
  lastWorkoutId: string | null,
  todayStr: string,
  weekday: number
): ResolvedToday {
  const active = slots.filter((s) => !s.deleted_at);
  if (active.length === 0) {
    return { workoutId: null, reason: 'rest' };
  }

  const dated = active.find((s) => s.scheduled_date === todayStr);
  if (dated) return { workoutId: dated.workout_id, reason: 'dated' };

  const weekly = active.find((s) => s.day_of_week === weekday);
  if (weekly) return { workoutId: weekly.workout_id, reason: 'weekly' };

  const rotation = active
    .filter((s) => s.day_of_week == null && s.scheduled_date == null)
    .sort((a, b) => a.sequence - b.sequence);
  if (rotation.length > 0) {
    const idx = rotation.findIndex((s) => s.workout_id === lastWorkoutId);
    const next = idx >= 0 ? rotation[(idx + 1) % rotation.length] : rotation[0];
    return { workoutId: next.workout_id, reason: 'rotation' };
  }

  return { workoutId: null, reason: 'rest' };
}
