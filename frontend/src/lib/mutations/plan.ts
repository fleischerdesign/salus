import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

function now(): string {
  return new Date().toISOString();
}

export const createPlan = (
  name: string,
  description: string | null,
  autoregMode: string,
  exercises: Array<Record<string, unknown>>
) => {
  const planId = uuid7();
  const exercisesWithIds = exercises.map((ex) => ({ ...ex, id: uuid7() }));
  return mutate({
    kind: 'command',
    command: 'create_plan',
    queueable: true,
    payload: {
      id: planId,
      name,
      description,
      autoreg_mode: autoregMode,
      exercises: exercisesWithIds
    },
    optimisticTable: 'workout_plan',
    optimisticData: {
      id: planId,
      user_id: 'self',
      name,
      description,
      autoreg_mode: autoregMode,
      position: 0,
      created_at: now(),
      updated_at: null,
      deleted_at: null
    },
    responseTable: 'workout_plan'
  });
};

export const deletePlan = (planId: string) =>
  mutate({
    kind: 'command',
    command: 'delete_plan',
    queueable: true,
    payload: { id: planId },
    optimisticTable: 'workout_plan',
    optimisticData: { id: planId, deleted_at: now() }
  });
