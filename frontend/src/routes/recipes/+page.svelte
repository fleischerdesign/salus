<script lang="ts">
  import { db } from '$lib/db/database';
  import type { Recipe, RecipeIngredient, FoodItem } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import RecipeGrid from '$components/food/RecipeGrid.svelte';
  import RecipeForm from '$components/food/RecipeForm.svelte';
  import { createRecipe } from '$lib/mutations/recipe';
  import { createMeal } from '$lib/mutations/meal';
  import { useQuery } from '$lib/db/use-query.svelte';

  let formOpen = $state(false);

  const { value: recipes } = useQuery(() => db.notDeleted(db.recipe).toArray());
  const { value: ingredients } = useQuery(() => db.notDeleted(db.recipe_ingredient).toArray());
  const { value: foodItems, loading } = useQuery(() => db.notDeleted(db.food_item).toArray());

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
        let calories = 0;
        for (const ing of recipeIngredients) {
          const food = foodMap[ing.food_item_id];
          if (food) {
            calories += (food.calories_per_serving / food.serving_size) * ing.amount_g;
          }
        }
        return {
          id: r.id ?? '',
          name: r.name,
          description: r.description,
          servings: r.servings,
          totalCalories: Math.round(calories),
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
    const recipeIngredients = (ingredients ?? []).filter(
      (i) => i.recipe_id === recipeId && !i.deleted_at
    );
    await createMeal({
      name: r.name ? `Recipe: ${r.name}` : undefined,
      meal_type: 'other',
      items: recipeIngredients.map((i) => ({
        food_item_id: i.food_item_id,
        servings: 1,
        amount_g: i.amount_g
      }))
    });
  }
</script>

<svelte:head><title>Salus — Recipes</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Recipes"
    subtitle="Save and reuse your favorite meal combinations"
    icon="menu-book"
    iconColor="#f59e0b"
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white hover:bg-primary-600"
          onclick={() => (formOpen = true)}
        >
          <Icon name="add" class="text-base" /><span>New Recipe</span>
        </button>
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
</div>
