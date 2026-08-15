import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { nowIso, todayString } from '$lib/utils/datetime';
import { startOfLocalDayMs, userTimezone } from '$lib/utils/timezone';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

export interface RecipeIngredientInput {
  food_item_id: string;
  amount_g: number;
  notes?: string;
}

export async function cookRecipe(recipeId: string, servings: number) {
  const recipe = await db.recipe.get(recipeId);
  if (!recipe || recipe.deleted_at) return { ok: false, error: 'Recipe not found' };

  const ingredients = await db.recipe_ingredient
    .where('recipe_id')
    .equals(recipeId)
    .filter((i) => !i.deleted_at)
    .toArray();
  const foodIds = [...new Set(ingredients.map((i) => i.food_item_id))];
  const foods = await db.food_item.bulkGet(foodIds);
  const foodMap = new Map(foods.filter(Boolean).map((f) => [f!.id, f!]));
  const scale = recipe.servings > 0 ? servings / recipe.servings : 1;

  const mealId = uuid7();
  const measurementId = uuid7();
  const now = nowIso();
  const logDate = todayString();

  const items = ingredients
    .map((ing) => {
      const food = foodMap.get(ing.food_item_id);
      if (!food) return null;
      const amountG = Math.round(ing.amount_g * scale);
      return {
        id: uuid7(),
        food_item_id: ing.food_item_id,
        servings: food.serving_size > 0 ? amountG / food.serving_size : 0,
        amount_g: amountG,
        food
      };
    })
    .filter(Boolean) as Array<{
    id: string;
    food_item_id: string;
    servings: number;
    amount_g: number;
    food: (typeof foods)[number] & Record<string, unknown>;
  }>;

  const macros = items.reduce(
    (acc, item) => {
      const f = item.food;
      const factor = item.servings;
      acc.calories += f!.calories_per_serving * factor;
      acc.protein_grams += f!.protein_g * factor;
      acc.carbs_grams += f!.carbs_g * factor;
      acc.fat_grams += f!.fat_g * factor;
      return acc;
    },
    { calories: 0, protein_grams: 0, carbs_grams: 0, fat_grams: 0 }
  );

  const startTime = new Date(startOfLocalDayMs(logDate, userTimezone())).toISOString();

  return mutate({
    kind: 'command',
    command: 'cook_recipe',
    queueable: true,
    payload: {
      recipe_id: recipeId,
      servings,
      measurement_id: measurementId,
      meal_id: mealId,
      items: items.map((i) => ({
        id: i.id,
        food_item_id: i.food_item_id,
        servings: i.servings,
        amount_g: i.amount_g
      }))
    },
    optimisticTable: 'meal',
    optimisticData: {
      id: mealId,
      user_id: SELF_USER_ID,
      log_date: logDate,
      meal_type: 'other',
      name: `Recipe: ${recipe.name}`,
      notes: null,
      created_at: now,
      updated_at: null,
      deleted_at: null
    },
    optimisticRows: [
      {
        table: 'meal_item',
        rows: items.map((i) => ({
          id: i.id,
          meal_id: mealId,
          user_id: SELF_USER_ID,
          food_item_id: i.food_item_id,
          servings: i.servings,
          amount_g: i.amount_g,
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
            source: 'meal',
            value_numeric: null,
            value_text: null,
            value_json: JSON.stringify(macros),
            start_time: startTime,
            end_time: null,
            notes: null,
            external_id: mealId,
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
