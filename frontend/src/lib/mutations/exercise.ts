import { mutate } from '$lib/mutate';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

function now(): string {
  return new Date().toISOString();
}

export const createExercise = (data: Record<string, unknown>) => {
  const id = uuid7();
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'exercise',
    id,
    data,
    optimistic: {
      id,
      user_id: SELF_USER_ID,
      ...data,
      created_at: now(),
      updated_at: null,
      deleted_at: null
    }
  });
};

export const deleteExercise = (exerciseId: string) =>
  mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'exercise',
    id: exerciseId,
    optimistic: { id: exerciseId }
  });
