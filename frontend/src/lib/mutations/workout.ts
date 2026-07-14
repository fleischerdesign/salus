import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

function now(): string {
  return new Date().toISOString();
}

export const startWorkout = (planId: string | null, autoregMode = 'advisory') =>
  mutate({
    kind: 'command',
    command: 'start_workout',
    queueable: true,
    payload: { id: uuid7(), plan_id: planId },
    optimisticTable: 'workout_session',
    optimisticData: {
      id: uuid7(),
      user_id: 'self',
      plan_id: planId,
      started_at: now(),
      completed_at: null,
      autoreg_mode: autoregMode,
      recovery_score: null,
      notes: null,
      created_at: now(),
      updated_at: null,
      deleted_at: null
    },
    responseTable: 'workout_session'
  });

export const completeWorkout = (sessionId: string, notes?: string) =>
  mutate({
    kind: 'command',
    command: 'complete_workout',
    queueable: true,
    payload: { session_id: sessionId, notes },
    optimisticTable: 'workout_session',
    optimisticData: {
      id: sessionId,
      completed_at: now(),
      notes: notes ?? null
    }
  });

export const logSet = (
  sessionId: string,
  exerciseId: string,
  setNumber: number,
  weight: number,
  reps: number,
  rpe?: number
) => {
  const id = uuid7();
  return mutate({
    kind: 'command',
    command: 'log_set',
    queueable: true,
    payload: {
      id,
      session_id: sessionId,
      exercise_id: exerciseId,
      set_number: setNumber,
      weight,
      reps,
      rpe
    },
    optimisticTable: 'workout_log_entry',
    optimisticData: {
      id,
      session_id: sessionId,
      exercise_id: exerciseId,
      set_number: setNumber,
      weight,
      reps,
      rpe: rpe ?? null,
      created_at: now(),
      updated_at: null,
      deleted_at: null
    },
    responseTable: 'workout_log_entry'
  });
};

export const deleteLogSet = (logEntryId: string) =>
  mutate({
    kind: 'command',
    command: 'delete_log_set',
    queueable: true,
    payload: { id: logEntryId },
    optimisticTable: 'workout_log_entry',
    optimisticData: { id: logEntryId, deleted_at: now() }
  });
