import type { WorkoutSet } from '$lib/db/types';

export function sessionVolume(logs: WorkoutSet[] | undefined, sessionId: string): number {
  return (logs ?? [])
    .filter((l) => l.session_id === sessionId)
    .reduce((sum, l) => sum + (l.weight ?? 0) * (l.reps ?? 0), 0);
}
