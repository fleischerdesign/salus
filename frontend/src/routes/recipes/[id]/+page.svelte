<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import type { FoodItem } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Card from '$components/ui/Card.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import RecipeForm from '$components/food/RecipeForm.svelte';
  import CookModal from '$components/food/CookModal.svelte';
  import { updateRecipe, deleteRecipe, cookRecipe } from '$lib/mutations/recipe';
  import { useQuery } from '$lib/db/use-query.svelte';

  let id = $derived(page.params.id);

  let editOpen = $state(false);
  let deleteOpen = $state(false);
  let cookOpen = $state(false);
  let cooking = $state(false);
  let saving = $state(false);

  const recipeQuery = useQuery(
    () =>
      id ? db.recipe.get(id).then((r) => (r && !r.deleted_at ? r : null)) : Promise.resolve(null),
    () => id
  );
  const recipe = $derived(recipeQuery.value);
  const ingredientsQuery = useQuery(
    () =>
      db.recipe_ingredient
        .where({ recipe_id: id })
        .filter((i) => !i.deleted_at)
        .toArray(),
    () => id
  );
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

  const macros = $derived.by(() => {
    let calories = 0,
      protein = 0,
      carbs = 0,
      fat = 0;
    for (const ing of ingredients ?? []) {
      const food = foodMap[ing.food_item_id];
      if (!food) continue;
      const factor = ing.amount_g / food.serving_size;
      calories += food.calories_per_serving * factor;
      protein += food.protein_g * factor;
      carbs += food.carbs_g * factor;
      fat += food.fat_g * factor;
    }
    return { calories, protein, carbs, fat };
  });

  async function handleSave(data: Parameters<typeof updateRecipe>[1]) {
    if (!id) return;
    saving = true;
    try {
      await updateRecipe(id, data);
      editOpen = false;
    } finally {
      saving = false;
    }
  }

  async function handleDelete() {
    if (!id) return;
    await deleteRecipe(id);
    goto('/recipes');
  }

  async function handleCook(servings: number) {
    if (!recipe) return;
    cooking = true;
    try {
      await cookRecipe(recipe.id ?? '', servings);
      cookOpen = false;
      goto('/meals');
    } finally {
      cooking = false;
    }
  }
</script>

<svelte:head><title>Salus — {recipe?.name ?? 'Recipe'}</title></svelte:head>

{#if loading}
  <div class="flex justify-center py-20"><Spinner /></div>
{:else if !recipe}
  <EmptyState
    icon="menu-book"
    title="Recipe not found"
    description="This recipe may have been deleted."
  />
{:else}
  <PageHeader
    title={recipe.name}
    subtitle={`${recipe.servings} servings · ${Math.round(macros.calories / recipe.servings)} kcal/serving`}
    icon="menu-book"
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch gap-2">
        <PageHeaderAction icon="restaurant" onclick={() => (cookOpen = true)}>Cook</PageHeaderAction
        >
        <PageHeaderAction variant="secondary" icon="edit" onclick={() => (editOpen = true)}
          >Edit</PageHeaderAction
        >
        <PageHeaderAction variant="danger" icon="delete" onclick={() => (deleteOpen = true)}
          >Delete</PageHeaderAction
        >
      </div>
    {/snippet}
  </PageHeader>

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
    <div class="flex flex-col gap-4 lg:col-span-2">
      <Card>
        <h3 class="text-surface-700 mb-4 text-sm font-semibold">Ingredients</h3>
        <div class="divide-surface-100 divide-y">
          {#each ingredients as ing (ing.id)}
            {@const food = foodMap[ing.food_item_id]}
            <div class="flex items-center justify-between py-3 first:pt-0 last:pb-0">
              <div class="flex items-center gap-3">
                <div
                  class="bg-surface-100 text-surface-500 flex h-8 w-8 items-center justify-center rounded-lg"
                >
                  <Icon name="restaurant" size="sm" />
                </div>
                <div>
                  <div class="text-surface-700 text-sm font-medium">{food?.name ?? 'Unknown'}</div>
                  <div class="text-surface-400 text-xs">
                    {ing.amount_g}g{ing.notes ? ` · ${ing.notes}` : ''}
                  </div>
                </div>
              </div>
              <div class="text-surface-500 text-xs">
                {food
                  ? Math.round((food.calories_per_serving / food.serving_size) * ing.amount_g)
                  : '—'} kcal
              </div>
            </div>
          {/each}
        </div>
      </Card>

      {#if recipe.instructions}
        <Card>
          <h3 class="text-surface-700 mb-4 text-sm font-semibold">Instructions</h3>
          <div class="prose prose-sm text-surface-600 whitespace-pre-line">
            {recipe.instructions}
          </div>
        </Card>
      {/if}
    </div>

    <div class="flex flex-col gap-4">
      <Card>
        <h3 class="text-surface-700 mb-2 text-sm font-semibold">Nutrition</h3>
        <div class="space-y-1 text-sm">
          <div class="flex justify-between">
            <span class="text-surface-400">Total</span>
            <span class="text-surface-700 font-medium">{Math.round(macros.calories)} kcal</span>
          </div>
          <div class="flex justify-between">
            <span class="text-surface-400">Per serving</span>
            <span class="text-surface-700 font-medium"
              >{Math.round(macros.calories / recipe.servings)} kcal</span
            >
          </div>
        </div>
        <div class="mt-3 grid grid-cols-3 gap-2 text-center">
          <div class="rounded-lg bg-blue-50 p-2">
            <div class="text-sm font-bold text-blue-700">{Math.round(macros.protein)}g</div>
            <div class="text-[10px] text-blue-500">Protein</div>
          </div>
          <div class="bg-warning-50 rounded-lg p-2">
            <div class="text-warning-700 text-sm font-bold">{Math.round(macros.carbs)}g</div>
            <div class="text-warning-500 text-[10px]">Carbs</div>
          </div>
          <div class="bg-error-50 rounded-lg p-2">
            <div class="text-error-700 text-sm font-bold">{Math.round(macros.fat)}g</div>
            <div class="text-error-500 text-[10px]">Fat</div>
          </div>
        </div>
      </Card>

      {#if recipe.description}
        <Card>
          <h3 class="text-surface-700 mb-2 text-sm font-semibold">About</h3>
          <p class="text-surface-600 text-sm">{recipe.description}</p>
        </Card>
      {/if}

      <Card>
        <div class="flex items-center justify-between text-sm">
          <div>
            <span class="text-surface-400">Prep: </span>
            <span class="text-surface-700">{recipe.prep_time_min ?? '—'} min</span>
          </div>
          <div>
            <span class="text-surface-400">Cook: </span>
            <span class="text-surface-700">{recipe.cook_time_min ?? '—'} min</span>
          </div>
          <div>
            <span class="text-surface-400">Servings: </span>
            <span class="text-surface-700">{recipe.servings}</span>
          </div>
        </div>
      </Card>
    </div>
  </div>

  <RecipeForm
    open={editOpen}
    recipe={{
      name: recipe.name,
      description: recipe.description ?? '',
      instructions: recipe.instructions ?? '',
      servings: recipe.servings,
      prep_time_min: recipe.prep_time_min,
      cook_time_min: recipe.cook_time_min
    }}
    recipeIngredients={(ingredients ?? [])
      .filter((i) => !i.deleted_at)
      .map((i) => ({
        food_item_id: i.food_item_id,
        amount_g: i.amount_g,
        notes: i.notes ?? null
      }))}
    foodItems={foodItems ?? []}
    onSave={handleSave}
    onClose={() => (editOpen = false)}
    {saving}
  />

  <CookModal
    open={cookOpen}
    recipeName={recipe.name}
    recipeServings={recipe.servings}
    macros={{
      calories: macros.calories,
      protein: macros.protein,
      carbs: macros.carbs,
      fat: macros.fat
    }}
    onCook={handleCook}
    onClose={() => (cookOpen = false)}
    {cooking}
  />

  <ConfirmDialog
    bind:open={deleteOpen}
    title="Delete Recipe"
    variant="danger"
    message="Are you sure you want to delete this recipe?"
    confirmLabel="Delete"
    onconfirm={handleDelete}
  />
{/if}
