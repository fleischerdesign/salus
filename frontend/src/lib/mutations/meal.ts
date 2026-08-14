import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { todayString, nowIso } from '$lib/utils/datetime';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

export async function createMeal(data: {
  log_date?: string;
  meal_type?: string;
  name?: string;
  notes?: string;
  items: { food_item_id: string; servings: number; amount_g?: number }[];
}) {
  const id = uuid7();
  const now = nowIso();
  const today = todayString();

  const mealResult = await mutate({
    kind: 'crud',
    op: 'create',
    entity: 'meal',
    id,
    data: {
      log_date: data.log_date ?? today,
      meal_type: data.meal_type ?? 'snack',
      name: data.name ?? null,
      notes: data.notes ?? null
    },
    optimistic: {
      id,
      user_id: SELF_USER_ID,
      log_date: data.log_date ?? today,
      meal_type: data.meal_type ?? 'snack',
      name: data.name ?? null,
      notes: data.notes ?? null,
      created_at: now,
      updated_at: null,
      deleted_at: null
    }
  });

  for (const item of data.items ?? []) {
    const itemId = uuid7();
    await mutate({
      kind: 'crud',
      op: 'create',
      entity: 'meal_item',
      id: itemId,
      data: {
        meal_id: id,
        food_item_id: item.food_item_id,
        servings: item.servings,
        amount_g: item.amount_g ?? null
      },
      optimistic: {
        id: itemId,
        meal_id: id,
        user_id: SELF_USER_ID,
        food_item_id: item.food_item_id,
        servings: item.servings,
        amount_g: item.amount_g ?? null,
        created_at: now,
        deleted_at: null
      }
    });
  }

  return mealResult;
}

export async function updateMeal(
  mealId: string,
  data: {
    meal_type?: string;
    name?: string;
    notes?: string;
    items?: { food_item_id: string; servings: number; amount_g?: number }[];
  }
) {
  return mutate({
    kind: 'crud',
    op: 'update',
    entity: 'meal',
    id: mealId,
    data
  });
}

export async function deleteMeal(mealId: string) {
  const items = await db.meal_item.where('meal_id').equals(mealId).toArray();
  for (const item of items) {
    await mutate({
      kind: 'crud',
      op: 'delete',
      entity: 'meal_item',
      id: item.id,
      data: { id: item.id }
    });
  }
  return mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'meal',
    id: mealId,
    data: { id: mealId }
  });
}
