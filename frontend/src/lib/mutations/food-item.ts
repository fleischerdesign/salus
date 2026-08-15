import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

export async function createFoodItem(data: {
  name: string;
  brand?: string;
  barcode?: string;
  serving_size?: number;
  serving_unit?: string;
  calories_per_serving?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
  sugar_g?: number;
  saturated_fat_g?: number;
  sodium_mg?: number;
}) {
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'food_item',
    id: uuid7(),
    data
  });
}

export async function updateFoodItem(
  foodItemId: string,
  data: Partial<Parameters<typeof createFoodItem>[0]>
) {
  return mutate({
    kind: 'crud',
    op: 'update',
    entity: 'food_item',
    id: foodItemId,
    data,
    optimistic: { id: foodItemId, ...data }
  });
}

export async function deleteFoodItem(foodItemId: string) {
  return mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'food_item',
    id: foodItemId,
    optimistic: { id: foodItemId }
  });
}
