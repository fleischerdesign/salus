import { mutate } from '$lib/mutate';

export async function createRecipe(data: {
  name: string;
  description?: string;
  instructions?: string;
  servings?: number;
  prep_time_min?: number;
  cook_time_min?: number;
  ingredients: { food_item_id: string; amount_g: number; notes?: string }[];
}) {
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'recipe',
    id: crypto.randomUUID(),
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
    prep_time_min?: number;
    cook_time_min?: number;
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
