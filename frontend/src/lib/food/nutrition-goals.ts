import { db } from '$lib/db/database';

export interface NutritionTargets {
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
}

export async function fetchNutritionTargets(): Promise<NutritionTargets> {
  const goals = await db.goal.where('metric_code').equals('nutrition').toArray();

  const targets: NutritionTargets = {};
  for (const g of goals) {
    if (g.deleted_at || !g.is_active) continue;
    if (g.frequency !== 'daily') continue;
    if (!g.nutrition_field) continue;
    targets[g.nutrition_field as keyof NutritionTargets] = g.target_value;
  }
  return targets;
}
