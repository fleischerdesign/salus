import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

export async function createRecipe(data: {
  name: string;
  description?: string;
  instructions?: string;
  servings?: number;
  prep_time_min?: number | null;
  cook_time_min?: number | null;
  ingredients: { food_item_id: string; amount_g: number; notes?: string }[];
}) {
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'recipe',
    id: uuid7(),
    data
  });
}

export async function updateRecipe(
  recipeId: string,
  data: {
    name?: string;
    description?: string;
    instructions?: string;
    servings?: number;
    prep_time_min?: number | null;
    cook_time_min?: number | null;
    is_favorite?: boolean;
    ingredients?: { food_item_id: string; amount_g: number; notes?: string }[];
  }
) {
  return mutate({
    kind: 'crud',
    op: 'update',
    entity: 'recipe',
    id: recipeId,
    data
  });
}

export async function deleteRecipe(recipeId: string) {
  return mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'recipe',
    id: recipeId,
    data: { id: recipeId }
  });
}
