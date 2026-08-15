import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { nowIso } from '$lib/utils/datetime';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

export interface RecipeIngredientInput {
  food_item_id: string;
  amount_g: number;
  notes?: string;
}

export async function createRecipe(data: {
  name: string;
  description?: string;
  instructions?: string;
  servings?: number;
  prep_time_min?: number | null;
  cook_time_min?: number | null;
  is_favorite?: boolean;
  ingredients: RecipeIngredientInput[];
}) {
  const id = uuid7();
  const now = nowIso();
  const ingredients = (data.ingredients ?? []).map((ing) => ({ id: uuid7(), ...ing }));

  return mutate({
    kind: 'command',
    command: 'create_recipe',
    queueable: true,
    payload: {
      id,
      name: data.name,
      description: data.description ?? null,
      instructions: data.instructions ?? null,
      servings: data.servings ?? 4,
      prep_time_min: data.prep_time_min ?? null,
      cook_time_min: data.cook_time_min ?? null,
      is_favorite: data.is_favorite ?? false,
      ingredients: ingredients.map((ing) => ({
        id: ing.id,
        food_item_id: ing.food_item_id,
        amount_g: ing.amount_g,
        notes: ing.notes ?? null
      }))
    },
    optimisticTable: 'recipe',
    optimisticData: {
      id,
      user_id: SELF_USER_ID,
      name: data.name,
      description: data.description ?? null,
      instructions: data.instructions ?? null,
      servings: data.servings ?? 4,
      prep_time_min: data.prep_time_min ?? null,
      cook_time_min: data.cook_time_min ?? null,
      is_favorite: data.is_favorite ?? false,
      created_at: now,
      updated_at: null,
      deleted_at: null
    },
    optimisticRows: [
      {
        table: 'recipe_ingredient',
        rows: ingredients.map((ing) => ({
          id: ing.id,
          recipe_id: id,
          user_id: SELF_USER_ID,
          food_item_id: ing.food_item_id,
          amount_g: ing.amount_g,
          notes: ing.notes ?? null,
          created_at: now,
          deleted_at: null
        }))
      }
    ],
    responseTable: 'recipe'
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
    ingredients?: RecipeIngredientInput[];
  }
) {
  const ingredients = data.ingredients?.map((ing) => ({ id: uuid7(), ...ing }));
  return mutate({
    kind: 'command',
    command: 'update_recipe',
    queueable: true,
    payload: {
      id: recipeId,
      ...data,
      ...(ingredients
        ? {
            ingredients: ingredients.map((ing) => ({
              id: ing.id,
              food_item_id: ing.food_item_id,
              amount_g: ing.amount_g,
              notes: ing.notes ?? null
            }))
          }
        : {})
    },
    optimisticTable: 'recipe',
    optimisticData: { id: recipeId, ...data },
    optimisticRows: ingredients
      ? [
          {
            table: 'recipe_ingredient',
            rows: ingredients.map((ing) => ({
              id: ing.id,
              recipe_id: recipeId,
              user_id: SELF_USER_ID,
              food_item_id: ing.food_item_id,
              amount_g: ing.amount_g,
              notes: ing.notes ?? null,
              created_at: nowIso(),
              deleted_at: null
            }))
          }
        ]
      : undefined,
    responseTable: 'recipe'
  });
}

export async function deleteRecipe(recipeId: string) {
  const ingredients = await db.recipe_ingredient.where('recipe_id').equals(recipeId).toArray();

  return mutate({
    kind: 'command',
    command: 'delete_recipe',
    queueable: true,
    payload: { id: recipeId },
    optimisticTable: 'recipe',
    optimisticData: { id: recipeId, deleted_at: nowIso() },
    optimisticDelete:
      ingredients.length > 0
        ? [{ table: 'recipe_ingredient', ids: ingredients.map((i) => i.id) }]
        : undefined
  });
}
