import { mutate } from '$lib/mutate';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';
import { nowIso } from '$lib/utils/datetime';

export const startWorkout = (workoutId: string | null, programId: string | null = null) => {
  const id = uuid7();
  return mutate({
    kind: 'command',
    command: 'start_workout',
    queueable: true,
    payload: { id, workout_id: workoutId, program_id: programId },
    optimisticTable: 'workout_session',
    optimisticData: {
      id,
      user_id: SELF_USER_ID,
      workout_id: workoutId,
      program_id: programId,
      started_at: nowIso(),
      completed_at: null,
      progression_scheme: null,
      recovery_score: null,
      notes: null,
      created_at: nowIso(),
      updated_at: null,
      deleted_at: null
    },
    responseTable: 'workout_session'
  });
};

export const completeWorkout = (sessionId: string, notes?: string) =>
  mutate({
    kind: 'command',
    command: 'complete_workout',
    queueable: true,
    payload: { session_id: sessionId, notes },
    optimisticTable: 'workout_session',
    optimisticData: {
      id: sessionId,
      completed_at: nowIso(),
      notes: notes ?? null
    }
  });

export const cancelWorkout = (sessionId: string) =>
  mutate({
    kind: 'command',
    command: 'cancel_workout',
    queueable: true,
    payload: { session_id: sessionId },
    optimisticTable: 'workout_session',
    optimisticData: {
      id: sessionId,
      deleted_at: nowIso()
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
    optimisticTable: 'workout_set',
    optimisticData: {
      id,
      session_id: sessionId,
      exercise_id: exerciseId,
      set_number: setNumber,
      weight,
      reps,
      rpe: rpe ?? null,
      created_at: nowIso(),
      updated_at: null,
      deleted_at: null
    },
    responseTable: 'workout_set'
  });
};

export const deleteLogSet = (logEntryId: string) =>
  mutate({
    kind: 'command',
    command: 'delete_log_set',
    queueable: true,
    payload: { id: logEntryId },
    optimisticTable: 'workout_set',
    optimisticData: { id: logEntryId, deleted_at: nowIso() }
  });
