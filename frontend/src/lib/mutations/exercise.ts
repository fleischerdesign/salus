import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

function now(): string {
  return new Date().toISOString();
}

export const createExercise = (data: Record<string, unknown>) => {
  const id = uuid7();
  return mutate({
    kind: 'command',
    command: 'create_exercise',
    queueable: true,
    payload: { id, ...data },
    optimisticTable: 'exercise',
    optimisticData: {
      id,
      user_id: 'self',
      ...data,
      created_at: now(),
      updated_at: null,
      deleted_at: null
    },
    responseTable: 'exercise'
  });
};

export const deleteExercise = (exerciseId: string) =>
  mutate({
    kind: 'command',
    command: 'delete_exercise',
    queueable: true,
    payload: { id: exerciseId },
    optimisticTable: 'exercise',
    optimisticData: { id: exerciseId, deleted_at: now() }
  });
