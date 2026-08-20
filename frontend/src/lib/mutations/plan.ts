import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

function now(): string {
  return new Date().toISOString();
}

interface WorkoutExerciseInput {
  id: string;
  exercise_id: string;
  sequence: number;
  target_sets: number | null;
  target_reps: number | null;
  target_rpe: number | null;
  is_autoreg_exempt: boolean;
  rest_seconds: number | null;
}

function toWorkoutExercises(exercises: Array<Record<string, unknown>>): WorkoutExerciseInput[] {
  return exercises.map((ex, index) => ({
    id: uuid7(),
    exercise_id: String(ex.exercise_id ?? ''),
    sequence: Number(ex.sequence ?? index),
    target_sets: (ex.target_sets as number | null) ?? null,
    target_reps: (ex.target_reps as number | null) ?? null,
    target_rpe: (ex.target_rpe as number | null) ?? null,
    is_autoreg_exempt: Boolean(ex.is_autoreg_exempt),
    rest_seconds: (ex.rest_seconds as number | null) ?? null
  }));
}

export const createWorkout = (
  name: string,
  description: string | null,
  exercises: Array<Record<string, unknown>>
) => {
  const workoutId = uuid7();
  const workoutExercises = toWorkoutExercises(exercises);
  return mutate({
    kind: 'command',
    command: 'create_workout',
    queueable: true,
    payload: {
      id: workoutId,
      name,
      description,
      exercises: workoutExercises
    },
    optimisticTable: 'workout',
    optimisticData: {
      id: workoutId,
      user_id: SELF_USER_ID,
      name,
      description,
      position: 0,
      created_at: now(),
      updated_at: null,
      deleted_at: null
    },
    optimisticRows: [
      {
        table: 'workout_exercise',
        rows: workoutExercises.map((ex) => ({
          ...ex,
          workout_id: workoutId,
          created_at: now(),
          updated_at: null,
          deleted_at: null
        }))
      }
    ],
    responseTable: 'workout'
  });
};

export const deleteWorkout = async (workoutId: string) => {
  const workoutExercises = await db.workout_exercise
    .where('workout_id')
    .equals(workoutId)
    .toArray();

  return mutate({
    kind: 'command',
    command: 'delete_workout',
    queueable: true,
    payload: { id: workoutId },
    optimisticTable: 'workout',
    optimisticData: { id: workoutId, deleted_at: now() },
    optimisticDelete:
      workoutExercises.length > 0
        ? [{ table: 'workout_exercise', ids: workoutExercises.map((we) => we.id) }]
        : undefined
  });
};
