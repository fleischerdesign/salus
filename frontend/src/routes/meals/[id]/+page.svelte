<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import type { FoodItem } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Card from '$components/ui/Card.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import MealItemRow from '$components/food/MealItemRow.svelte';
  import { deleteMeal } from '$lib/mutations/meal';
  import { useQuery } from '$lib/db/use-query.svelte';

  let id = $derived(page.params.id);

  let deleteOpen = $state(false);

  const mealQuery = useQuery(() =>
    id ? db.meal.get(id).then((m) => (m && !m.deleted_at ? m : null)) : Promise.resolve(null)
  );
  const meal = $derived(mealQuery.value);
  const mealItemsQuery = useQuery(() =>
    db.meal_item
      .where({ meal_id: id })
      .filter((mi) => !mi.deleted_at)
      .toArray()
  );
  const mealItems = $derived(mealItemsQuery.value);
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
    for (const mi of mealItems ?? []) {
      const food = foodMap[mi.food_item_id];
      if (!food) continue;
      calories += food.calories_per_serving * mi.servings;
      protein += food.protein_g * mi.servings;
      carbs += food.carbs_g * mi.servings;
      fat += food.fat_g * mi.servings;
    }
    return { calories, protein, carbs, fat };
  });

  async function handleDelete() {
    if (!id) return;
    await deleteMeal(id);
    goto('/meals');
  }
</script>

<svelte:head><title>Salus — Meal Details</title></svelte:head>

{#if loading}
  <div class="flex justify-center py-20"><Spinner /></div>
{:else if !meal}
  <EmptyState
    icon="restaurant"
    title="Meal not found"
    description="This meal may have been deleted."
  />
{:else}
  <PageHeader
    title={meal.name ?? `${meal.meal_type.charAt(0).toUpperCase() + meal.meal_type.slice(1)}`}
    subtitle={new Date(meal.log_date + 'T12:00').toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric'
    })}
    icon="restaurant"
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <PageHeaderAction variant="danger" icon="delete" onclick={() => (deleteOpen = true)}
          >Delete</PageHeaderAction
        >
      </div>
    {/snippet}
  </PageHeader>

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
    <div class="flex flex-col gap-4 lg:col-span-2">
      <Card>
        <h3 class="mb-4 text-sm font-semibold text-surface-700">
          Items · {Math.round(macros.calories)} kcal · {Math.round(macros.protein)}P · {Math.round(
            macros.carbs
          )}C · {Math.round(macros.fat)}F
        </h3>
        <div class="flex flex-col gap-2">
          {#each mealItems ?? [] as mi (mi.id)}
            {@const food = foodMap[mi.food_item_id]}
            <MealItemRow
              name={food?.name ?? 'Unknown'}
              servings={mi.servings}
              amountG={mi.amount_g}
              calories={food ? food.calories_per_serving * mi.servings : 0}
              proteinG={food ? food.protein_g * mi.servings : 0}
              carbsG={food ? food.carbs_g * mi.servings : 0}
              fatG={food ? food.fat_g * mi.servings : 0}
              onRemove={() => {}}
              onIncrement={() => {}}
              onDecrement={() => {}}
            />
          {:else}
            <p class="text-sm text-surface-400 text-center py-4">No items in this meal.</p>
          {/each}
        </div>
      </Card>
    </div>

    <div class="flex flex-col gap-4">
      <Card>
        <h3 class="mb-2 text-sm font-semibold text-surface-700">Details</h3>
        <div class="space-y-2 text-sm">
          <div>
            <span class="text-surface-400">Type: </span>
            <Badge variant="default"
              >{meal.meal_type.charAt(0).toUpperCase() + meal.meal_type.slice(1)}</Badge
            >
          </div>
          <div>
            <span class="text-surface-400">Date: </span>
            <span class="text-surface-700">{meal.log_date}</span>
          </div>
          {#if meal.notes}
            <div>
              <span class="text-surface-400">Notes: </span>
              <span class="text-surface-700">{meal.notes}</span>
            </div>
          {/if}
          <div class="border-t border-surface-100 pt-2">
            <div class="font-medium text-surface-700">{Math.round(macros.calories)} kcal</div>
            <div class="mt-1 text-xs text-surface-400">
              {Math.round(macros.protein)}g protein · {Math.round(macros.carbs)}g carbs · {Math.round(
                macros.fat
              )}g fat
            </div>
          </div>
        </div>
      </Card>
    </div>
  </div>

  <ConfirmDialog
    bind:open={deleteOpen}
    title="Delete Meal"
    variant="danger"
    message="Are you sure you want to delete this meal?"
    confirmLabel="Delete"
    onconfirm={handleDelete}
  />
{/if}
