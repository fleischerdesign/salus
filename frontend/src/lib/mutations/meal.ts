import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';

export async function createMeal(data: {
  log_date?: string;
  meal_type?: string;
  name?: string;
  notes?: string;
  items: { food_item_id: string; servings: number; amount_g?: number }[];
}) {
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  const today = new Date().toISOString().split('T')[0];

  return mutate({
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
      user_id: '',
      log_date: data.log_date ?? today,
      meal_type: data.meal_type ?? 'snack',
      name: data.name ?? null,
      notes: data.notes ?? null,
      created_at: now,
      updated_at: null,
      deleted_at: null
    }
  });
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
  return mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'meal',
    id: mealId,
    data: { id: mealId }
  });
}
