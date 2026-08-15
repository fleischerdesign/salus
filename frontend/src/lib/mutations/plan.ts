import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

function now(): string {
  return new Date().toISOString();
}

interface PlanExercise {
  id: string;
  exercise_id: string;
  sequence: number;
  target_sets: number | null;
  target_reps: number | null;
  target_rpe: number | null;
  is_autoreg_exempt: boolean;
  rest_seconds: number | null;
}

function toPlanExercises(exercises: Array<Record<string, unknown>>): PlanExercise[] {
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

export const createPlan = (
  name: string,
  description: string | null,
  autoregMode: string,
  exercises: Array<Record<string, unknown>>
) => {
  const planId = uuid7();
  const planExercises = toPlanExercises(exercises);
  return mutate({
    kind: 'command',
    command: 'create_plan',
    queueable: true,
    payload: {
      id: planId,
      name,
      description,
      autoreg_mode: autoregMode,
      exercises: planExercises
    },
    optimisticTable: 'workout_plan',
    optimisticData: {
      id: planId,
      user_id: SELF_USER_ID,
      name,
      description,
      autoreg_mode: autoregMode,
      position: 0,
      created_at: now(),
      updated_at: null,
      deleted_at: null
    },
    optimisticRows: [
      {
        table: 'workout_plan_exercise',
        rows: planExercises.map((ex) => ({
          ...ex,
          plan_id: planId,
          created_at: now(),
          updated_at: null,
          deleted_at: null
        }))
      }
    ],
    responseTable: 'workout_plan'
  });
};

export const deletePlan = async (planId: string) => {
  const planExercises = await db.workout_plan_exercise.where('plan_id').equals(planId).toArray();

  return mutate({
    kind: 'command',
    command: 'delete_plan',
    queueable: true,
    payload: { id: planId },
    optimisticTable: 'workout_plan',
    optimisticData: { id: planId, deleted_at: now() },
    optimisticDelete:
      planExercises.length > 0
        ? [{ table: 'workout_plan_exercise', ids: planExercises.map((pe) => pe.id) }]
        : undefined
  });
};
