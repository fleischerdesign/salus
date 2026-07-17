<script lang="ts">
  import { liveQuery } from 'dexie';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import type { Meal, MealItem, FoodItem } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import MealItemRow from '$components/food/MealItemRow.svelte';
  import { deleteMeal } from '$lib/mutations/meal';

  let id = $derived(page.params.id);

  let loading = $state(true);
  let meal = $state<Meal | null>(null);
  let mealItems = $state<MealItem[]>([]);
  let foodItems = $state<FoodItem[]>([]);
  let deleteOpen = $state(false);

  $effect(() => {
    if (!id) return;
    const sub1 = liveQuery(() =>
      db.meal.get(id).then((m) => (m && !m.deleted_at ? m : null))
    ).subscribe((v) => { meal = v; });
    const sub2 = liveQuery(() =>
      db.meal_item.where({ meal_id: id }).filter((mi) => !mi.deleted_at).toArray()
    ).subscribe((v) => { mealItems = v; });
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
    for (const mi of mealItems) {
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
  <EmptyState icon="restaurant" title="Meal not found" description="This meal may have been deleted." />
{:else}
  <PageHeader
    title={meal.name ?? `${meal.meal_type.charAt(0).toUpperCase() + meal.meal_type.slice(1)}`}
    subtitle={new Date(meal.log_date + 'T12:00').toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
    icon="restaurant"
    iconColor="#f59e0b"
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch">
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
        <h3 class="text-sm font-semibold text-surface-700 mb-4">
          Items · {Math.round(macros.calories)} kcal · {Math.round(macros.protein)}P · {Math.round(macros.carbs)}C · {Math.round(macros.fat)}F
        </h3>
        <div class="flex flex-col gap-2">
          {#each mealItems as mi (mi.id)}
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
        <h3 class="text-sm font-semibold text-surface-700 mb-2">Details</h3>
        <div class="text-sm space-y-2">
          <div>
            <span class="text-surface-400">Type: </span>
            <Badge variant="default">{meal.meal_type.charAt(0).toUpperCase() + meal.meal_type.slice(1)}</Badge>
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
          <div class="pt-2 border-t border-surface-100">
            <div class="font-medium text-surface-700">{Math.round(macros.calories)} kcal</div>
            <div class="text-xs text-surface-400 mt-1">
              {Math.round(macros.protein)}g protein · {Math.round(macros.carbs)}g carbs · {Math.round(macros.fat)}g fat
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
