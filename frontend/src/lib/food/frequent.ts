import { db } from '$lib/db/database';
import type { FoodItem } from '$lib/db/types';

export async function loadFrequentFoods(limit = 6): Promise<FoodItem[]> {
  const items = await db.meal_item.toArray();
  const foodIds = items.filter((mi) => !mi.deleted_at).map((mi) => mi.food_item_id);
  const counts = new Map<string, number>();
  for (const id of foodIds) counts.set(id, (counts.get(id) ?? 0) + 1);
  const top = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit);
  const foods: FoodItem[] = [];
  for (const [id] of top) {
    const f = await db.food_item.get(id);
    if (f && !f.deleted_at) foods.push(f);
  }
  return foods;
}

export async function newestFood(): Promise<FoodItem | null> {
  const all = await db.notDeleted(db.food_item).toArray();
  const newest = [...all].sort((a, b) => (b.created_at ?? '').localeCompare(a.created_at ?? ''))[0];
  return newest ?? null;
}
