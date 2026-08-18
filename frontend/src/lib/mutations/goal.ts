import { mutate } from '$lib/mutate';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

export const createGoal = (
  metricCode: string,
  targetValue: number,
  direction = 'increase',
  frequency = 'daily',
  deadline?: string,
  nutritionField?: string | null
) => {
  const id = uuid7();
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'goal',
    id,
    data: {
      id,
      metric_code: metricCode,
      target_value: targetValue,
      direction,
      frequency,
      deadline: deadline ?? null,
      nutrition_field: nutritionField ?? null
    },
    optimistic: {
      id,
      user_id: SELF_USER_ID,
      metric_code: metricCode,
      target_value: targetValue,
      direction,
      frequency,
      deadline: deadline ?? null,
      nutrition_field: nutritionField ?? null,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: null,
      deleted_at: null
    }
  });
};

export const updateGoal = (
  goalId: string,
  data: Partial<{
    target_value: number;
    direction: string;
    frequency: string;
    deadline: string | null;
  }>
) =>
  mutate({
    kind: 'crud',
    op: 'update',
    entity: 'goal',
    id: goalId,
    data,
    optimistic: { id: goalId, ...data }
  });

export const deleteGoal = (goalId: string) =>
  mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'goal',
    id: goalId,
    optimistic: { id: goalId }
  });
