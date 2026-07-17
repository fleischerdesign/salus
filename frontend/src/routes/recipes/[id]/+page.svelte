<script lang="ts">
  import { liveQuery } from 'dexie';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import type { Recipe, RecipeIngredient, FoodItem } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import RecipeForm from '$components/food/RecipeForm.svelte';
  import { updateRecipe, deleteRecipe } from '$lib/mutations/recipe';
  import { createMeal } from '$lib/mutations/meal';

  let id = $derived(page.params.id);

  let loading = $state(true);
  let recipe = $state<Recipe | null>(null);
  let ingredients = $state<RecipeIngredient[]>([]);
  let foodItems = $state<FoodItem[]>([]);
  let editOpen = $state(false);
  let deleteOpen = $state(false);
  let saving = $state(false);

  $effect(() => {
    if (!id) return;
    const sub1 = liveQuery(() =>
      db.recipe.get(id).then((r) => (r && !r.deleted_at ? r : null))
    ).subscribe((v) => { recipe = v; });
    const sub2 = liveQuery(() =>
      db.recipe_ingredient.where({ recipe_id: id }).filter((i) => !i.deleted_at).toArray()
    ).subscribe((v) => { ingredients = v; });
    const sub3 = liveQuery(() =>
      db.food_item.where('deleted_at').equals('').or('deleted_at').equals(null as any).toArray()
    ).subscribe((v) => { foodItems = v; loading = false; });
    return () => { sub1.unsubscribe(); sub2.unsubscribe(); sub3.unsubscribe(); };
  });

  const foodMap = $derived.by(() => {
    const map: Record<string, FoodItem> = {};
    for (const f of foodItems) {
      if (!f.deleted_at) map[f.id] = f;
    }
    return map;
  });

  const macros = $derived.by(() => {
    let calories = 0, protein = 0, carbs = 0, fat = 0;
    for (const ing of ingredients) {
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

  async function handleSave(data: any) {
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

  async function handleCook() {
    if (!recipe) return;
    const recipeIngredients = ingredients.filter((i) => !i.deleted_at);
    await createMeal({
      name: `Recipe: ${recipe.name}`,
      meal_type: 'other',
      items: recipeIngredients.map((i) => ({
        food_item_id: i.food_item_id,
        servings: 1,
        amount_g: i.amount_g
      }))
    });
    goto('/meals');
  }
</script>

<svelte:head><title>Salus — {recipe?.name ?? 'Recipe'}</title></svelte:head>

{#if loading}
  <div class="flex justify-center py-20"><Spinner /></div>
{:else if !recipe}
  <EmptyState icon="menu-book" title="Recipe not found" description="This recipe may have been deleted." />
{:else}
  <PageHeader
    title={recipe.name}
    subtitle={`${recipe.servings} servings · ${Math.round(macros.calories / recipe.servings)} kcal/serving`}
    icon="menu-book"
    iconColor="#f59e0b"
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch gap-2">
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white hover:bg-primary-600"
          onclick={handleCook}
        >
          <Icon name="restaurant" class="text-base" /><span>Cook</span>
        </button>
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 bg-surface-100 px-6 text-sm font-semibold whitespace-nowrap text-surface-700 hover:bg-surface-200"
          onclick={() => (editOpen = true)}
        >
          <Icon name="edit" class="text-base" /><span>Edit</span>
        </button>
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 bg-error-500 px-6 text-sm font-semibold whitespace-nowrap text-white hover:bg-error-600"
          onclick={() => (deleteOpen = true)}
        >
          <Icon name="delete" class="text-base" /><span>Delete</span>
        </button>
      </div>
    {/snippet}
  </PageHeader>

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2 flex flex-col gap-4">
      <Card>
        <h3 class="text-sm font-semibold text-surface-700 mb-4">Ingredients</h3>
        <div class="divide-y divide-surface-100">
          {#each ingredients as ing (ing.id)}
            {@const food = foodMap[ing.food_item_id]}
            <div class="flex items-center justify-between py-3 first:pt-0 last:pb-0">
              <div class="flex items-center gap-3">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-100 text-surface-500">
                  <Icon name="restaurant" size="sm" />
                </div>
                <div>
                  <div class="text-sm font-medium text-surface-700">{food?.name ?? 'Unknown'}</div>
                  <div class="text-xs text-surface-400">{ing.amount_g}g{ing.notes ? ` · ${ing.notes}` : ''}</div>
                </div>
              </div>
              <div class="text-xs text-surface-500">
                {food ? Math.round((food.calories_per_serving / food.serving_size) * ing.amount_g) : '—'} kcal
              </div>
            </div>
          {/each}
        </div>
      </Card>

      {#if recipe.instructions}
        <Card>
          <h3 class="text-sm font-semibold text-surface-700 mb-4">Instructions</h3>
          <div class="prose prose-sm text-surface-600 whitespace-pre-line">{recipe.instructions}</div>
        </Card>
      {/if}
    </div>

    <div class="flex flex-col gap-4">
      <Card>
        <h3 class="text-sm font-semibold text-surface-700 mb-2">Nutrition</h3>
        <div class="text-sm space-y-1">
          <div class="flex justify-between">
            <span class="text-surface-400">Total</span>
            <span class="font-medium text-surface-700">{Math.round(macros.calories)} kcal</span>
          </div>
          <div class="flex justify-between">
            <span class="text-surface-400">Per serving</span>
            <span class="font-medium text-surface-700">{Math.round(macros.calories / recipe.servings)} kcal</span>
          </div>
        </div>
        <div class="mt-3 grid grid-cols-3 gap-2 text-center">
          <div class="rounded-lg bg-blue-50 p-2">
            <div class="text-sm font-bold text-blue-700">{Math.round(macros.protein)}g</div>
            <div class="text-[10px] text-blue-500">Protein</div>
          </div>
          <div class="rounded-lg bg-amber-50 p-2">
            <div class="text-sm font-bold text-amber-700">{Math.round(macros.carbs)}g</div>
            <div class="text-[10px] text-amber-500">Carbs</div>
          </div>
          <div class="rounded-lg bg-red-50 p-2">
            <div class="text-sm font-bold text-red-700">{Math.round(macros.fat)}g</div>
            <div class="text-[10px] text-red-500">Fat</div>
          </div>
        </div>
      </Card>

      {#if recipe.description}
        <Card>
          <h3 class="text-sm font-semibold text-surface-700 mb-2">About</h3>
          <p class="text-sm text-surface-600">{recipe.description}</p>
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
    {foodItems}
    onSave={handleSave}
    onClose={() => (editOpen = false)}
    {saving}
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
