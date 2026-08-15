import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { todayString, nowIso } from '$lib/utils/datetime';
import { startOfLocalDayMs, userTimezone } from '$lib/utils/timezone';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

const MEAL_SOURCE = 'meal';

export interface MealItemInput {
  food_item_id: string;
  servings: number;
  amount_g?: number;
}

export async function createMeal(data: {
  log_date?: string;
  meal_type?: string;
  name?: string;
  notes?: string;
  items: MealItemInput[];
}) {
  const id = uuid7();
  const now = nowIso();
  const logDate = data.log_date ?? todayString();
  const measurementId = uuid7();
  const items = (data.items ?? []).map((item) => ({ id: uuid7(), ...item }));

  const macros = await calcMacros(items);
  const startTime = new Date(startOfLocalDayMs(logDate, userTimezone())).toISOString();

  return mutate({
    kind: 'command',
    command: 'create_meal',
    queueable: true,
    payload: {
      id,
      log_date: logDate,
      meal_type: data.meal_type ?? 'snack',
      name: data.name ?? null,
      notes: data.notes ?? null,
      measurement_id: measurementId,
      items: items.map((i) => ({
        id: i.id,
        food_item_id: i.food_item_id,
        servings: i.servings,
        amount_g: i.amount_g ?? null
      }))
    },
    optimisticTable: 'meal',
    optimisticData: {
      id,
      user_id: SELF_USER_ID,
      log_date: logDate,
      meal_type: data.meal_type ?? 'snack',
      name: data.name ?? null,
      notes: data.notes ?? null,
      created_at: now,
      updated_at: null,
      deleted_at: null
    },
    optimisticRows: [
      {
        table: 'meal_item',
        rows: items.map((item) => ({
          id: item.id,
          meal_id: id,
          user_id: SELF_USER_ID,
          food_item_id: item.food_item_id,
          servings: item.servings,
          amount_g: item.amount_g ?? null,
          created_at: now,
          deleted_at: null
        }))
      },
      {
        table: 'measurement',
        rows: [
          {
            id: measurementId,
            user_id: SELF_USER_ID,
            metric_code: 'nutrition',
            source_data_type: 'nutrition',
            source: MEAL_SOURCE,
            value_numeric: null,
            value_text: null,
            value_json: JSON.stringify(macros),
            start_time: startTime,
            end_time: null,
            notes: null,
            external_id: id,
            created_at: now,
            updated_at: null,
            deleted_at: null
          }
        ]
      }
    ],
    responseTable: 'meal'
  });
}

export async function updateMeal(
  mealId: string,
  data: {
    meal_type?: string;
    name?: string;
    notes?: string;
    items?: MealItemInput[];
  }
) {
  return mutate({
    kind: 'command',
    command: 'update_meal',
    queueable: true,
    payload: { id: mealId, ...data },
    optimisticTable: 'meal',
    optimisticData: { id: mealId, ...data },
    responseTable: 'meal'
  });
}

export async function deleteMeal(mealId: string) {
  const items = await db.meal_item.where('meal_id').equals(mealId).toArray();
  const itemIds = items.map((i) => i.id);
  const measurements = await db.measurement.where('external_id').equals(mealId).toArray();

  return mutate({
    kind: 'command',
    command: 'delete_meal',
    queueable: true,
    payload: { id: mealId },
    optimisticTable: 'meal',
    optimisticData: { id: mealId, deleted_at: nowIso() },
    optimisticDelete: [
      ...(itemIds.length > 0 ? [{ table: 'meal_item', ids: itemIds }] : []),
      ...(measurements.length > 0
        ? [{ table: 'measurement', ids: measurements.map((m) => m.id) }]
        : [])
    ]
  });
}

async function calcMacros(
  items: { food_item_id: string; servings: number }[]
): Promise<{ calories: number; protein_g: number; carbs_g: number; fat_g: number }> {
  const foodIds = [...new Set(items.map((i) => i.food_item_id))];
  const foods = await db.food_item.bulkGet(foodIds);
  const foodMap = new Map(foods.filter(Boolean).map((f) => [f!.id, f!]));

  const total = { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 };
  for (const item of items) {
    const food = foodMap.get(item.food_item_id);
    if (!food) continue;
    const factor = item.servings;
    total.calories += food.calories_per_serving * factor;
    total.protein_g += food.protein_g * factor;
    total.carbs_g += food.carbs_g * factor;
    total.fat_g += food.fat_g * factor;
  }
  return total;
}
