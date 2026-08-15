<script lang="ts">
  import { db } from '$lib/db/database';
  import type { FoodItem } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import RecipeGrid from '$components/food/RecipeGrid.svelte';
  import RecipeForm from '$components/food/RecipeForm.svelte';
  import CookModal from '$components/food/CookModal.svelte';
  import { createRecipe, cookRecipe } from '$lib/mutations/recipe';
  import { useQuery } from '$lib/db/use-query.svelte';

  let formOpen = $state(false);
  let cookTarget = $state<{
    id: string;
    name: string;
    servings: number;
    macros: { calories: number; protein: number; carbs: number; fat: number } | null;
  } | null>(null);
  let cooking = $state(false);

  const recipesQuery = useQuery(() => db.notDeleted(db.recipe).toArray());
  const recipes = $derived(recipesQuery.value);
  const ingredientsQuery = useQuery(() => db.notDeleted(db.recipe_ingredient).toArray());
  const ingredients = $derived(ingredientsQuery.value);
  const foodItemsQuery = useQuery(() => db.notDeleted(db.food_item).toArray());
  const foodItems = $derived(foodItemsQuery.value);
  const loading = $derived(foodItemsQuery.loading);

  const foodMap = $derived.by(() => {
    const map: Record<string, FoodItem> = {};
    for (const f of foodItems ?? []) {
      if (!f.deleted_at) map[f.id] = f;
    }
    return map;
  });

  const recipeData = $derived.by(() => {
    return (recipes ?? [])
      .filter((r) => !r.deleted_at)
      .map((r) => {
        const recipeIngredients = (ingredients ?? []).filter(
          (i) => i.recipe_id === r.id && !i.deleted_at
        );
        let calories = 0,
          protein = 0,
          carbs = 0,
          fat = 0;
        for (const ing of recipeIngredients) {
          const food = foodMap[ing.food_item_id];
          if (food) {
            const factor = ing.amount_g / food.serving_size;
            calories += food.calories_per_serving * factor;
            protein += food.protein_g * factor;
            carbs += food.carbs_g * factor;
            fat += food.fat_g * factor;
          }
        }
        return {
          id: r.id ?? '',
          name: r.name,
          description: r.description,
          servings: r.servings,
          totalCalories: calories,
          totalProtein: protein,
          totalCarbs: carbs,
          totalFat: fat,
          prepTimeMin: r.prep_time_min,
          cookTimeMin: r.cook_time_min,
          isFavorite: r.is_favorite
        };
      });
  });

  async function handleSave(data: Parameters<typeof createRecipe>[0]) {
    await createRecipe(data);
    formOpen = false;
  }

  async function handleCook(recipeId: string) {
    const r = (recipes ?? []).find((r) => r.id === recipeId);
    if (!r) return;
    const macros = recipeData.find((rd) => rd.id === recipeId);
    cookTarget = {
      id: recipeId,
      name: r.name ?? 'Recipe',
      servings: r.servings,
      macros: macros
        ? {
            calories: macros.totalCalories,
            protein: macros.totalProtein,
            carbs: macros.totalCarbs,
            fat: macros.totalFat
          }
        : null
    };
  }

  async function handleCookConfirm(servings: number) {
    if (!cookTarget) return;
    cooking = true;
    try {
      await cookRecipe(cookTarget.id, servings);
      cookTarget = null;
    } finally {
      cooking = false;
    }
  }
</script>

<svelte:head><title>Salus — Recipes</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Recipes"
    subtitle="Save and reuse your favorite meal combinations"
    icon="menu-book"
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <PageHeaderAction icon="add" onclick={() => (formOpen = true)}>New Recipe</PageHeaderAction>
      </div>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="flex justify-center py-20"><Spinner /></div>
  {:else}
    <RecipeGrid recipes={recipeData} onCook={handleCook} onCreate={() => (formOpen = true)} />
  {/if}

  <RecipeForm
    open={formOpen}
    recipe={null}
    foodItems={foodItems ?? []}
    onSave={handleSave}
    onClose={() => (formOpen = false)}
  />

  <CookModal
    open={cookTarget !== null}
    recipeName={cookTarget?.name ?? ''}
    recipeServings={cookTarget?.servings ?? 1}
    macros={cookTarget?.macros ?? null}
    onCook={handleCookConfirm}
    onClose={() => (cookTarget = null)}
    {cooking}
  />
</div>
