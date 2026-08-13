<script lang="ts">
  import { db } from '$lib/db/database';
  import { todayString, dateString } from '$lib/utils/datetime';
  import type { FoodItem, MealItem } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import DayNavigator from '$components/ui/DayNavigator.svelte';
  import NutritionSummary from '$components/food/NutritionSummary.svelte';
  import MealGrid from '$components/food/MealGrid.svelte';
  import MealForm from '$components/food/MealForm.svelte';
  import { createMeal, deleteMeal } from '$lib/mutations/meal';
  import { useQuery } from '$lib/db/use-query.svelte';

  let formOpen = $state(false);

  let selectedDate = $state(todayString());

  const mealsQuery = useQuery(() =>
    db.meal
      .where('log_date')
      .equals(selectedDate)
      .filter((m) => !m.deleted_at)
      .toArray()
  );
  const meals = $derived(mealsQuery.value);
  const mealItemsQuery = useQuery(async () => {
    const mealIds = (meals ?? []).map((m) => m.id);
    if (mealIds.length === 0) return [] as MealItem[];
    return db.meal_item
      .where('meal_id')
      .anyOf(mealIds)
      .filter((mi) => !mi.deleted_at)
      .toArray();
  });
  const mealItems = $derived(mealItemsQuery.value);
  const foodItemsQuery = useQuery(() => db.notDeleted(db.food_item).toArray());
  const foodItems = $derived(foodItemsQuery.value);
  const loading = $derived(foodItemsQuery.loading);

  const today = $derived(todayString());
  const isToday = $derived(selectedDate === today);

  const mealsForDate = $derived(
    (meals ?? [])
      .filter((m) => m.log_date === selectedDate && !m.deleted_at)
      .sort((a, b) => (a.created_at ?? '').localeCompare(b.created_at ?? ''))
  );

  const mealItemsMap = $derived.by(() => {
    const map: Record<string, MealItem[]> = {};
    for (const mi of mealItems ?? []) {
      if (mi.deleted_at) continue;
      if (!map[mi.meal_id]) map[mi.meal_id] = [];
      map[mi.meal_id].push(mi);
    }
    return map;
  });

  const foodMap = $derived.by(() => {
    const map: Record<string, FoodItem> = {};
    for (const f of foodItems ?? []) {
      if (!f.deleted_at) map[f.id] = f;
    }
    return map;
  });

  const macroTotals = $derived.by(() => {
    const map: Record<string, { calories: number; protein: number; carbs: number; fat: number }> =
      {};
    for (const meal of mealsForDate) {
      const items = mealItemsMap[meal.id ?? ''] ?? [];
      let calories = 0,
        protein = 0,
        carbs = 0,
        fat = 0;
      for (const mi of items) {
        const food = foodMap[mi.food_item_id];
        if (!food) continue;
        calories += food.calories_per_serving * mi.servings;
        protein += food.protein_g * mi.servings;
        carbs += food.carbs_g * mi.servings;
        fat += food.fat_g * mi.servings;
      }
      map[meal.id ?? ''] = { calories, protein, carbs, fat };
    }
    return map;
  });

  const dailyTotals = $derived.by(() => {
    let calories = 0,
      protein = 0,
      carbs = 0,
      fat = 0;
    for (const m of Object.values(macroTotals)) {
      calories += m.calories;
      protein += m.protein;
      carbs += m.carbs;
      fat += m.fat;
    }
    return { calories, protein, carbs, fat };
  });

  async function handleSave(data: {
    meal_type: string;
    name: string;
    notes: string;
    items: { food_item_id: string; servings: number }[];
  }) {
    await createMeal({ ...data, log_date: selectedDate });
    formOpen = false;
  }

  async function handleDelete(mealId: string) {
    const { ok, error } = await deleteMeal(mealId);
    if (!ok) console.error('Failed to delete meal:', error);
  }

  function goToEdit(mealId: string) {
    window.location.href = '/meals/' + mealId;
  }
</script>

<svelte:head><title>Salus — Meals</title></svelte:head>

<div class="space-y-6">
  <PageHeader title="Meals" subtitle="Track your nutrition, one meal at a time" icon="restaurant">
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <PageHeaderAction icon="add" onclick={() => (formOpen = true)}>Log Meal</PageHeaderAction>
      </div>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="flex justify-center py-20">
      <Spinner />
    </div>
  {:else}
    <DayNavigator
      dateDisplay={new Date(selectedDate + 'T12:00').toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      })}
      onPrev={() => {
        const d = new Date(selectedDate + 'T12:00');
        d.setDate(d.getDate() - 1);
        selectedDate = dateString(d);
      }}
      onNext={() => {
        const d = new Date(selectedDate + 'T12:00');
        d.setDate(d.getDate() + 1);
        selectedDate = dateString(d);
      }}
      {isToday}
    >
      {#snippet children()}
        {#if !isToday}
          <button
            class="text-xs text-primary-600 hover:text-primary-700"
            onclick={() => (selectedDate = today)}
          >
            Today
          </button>
        {/if}
      {/snippet}
    </DayNavigator>

    <NutritionSummary
      totalCalories={dailyTotals.calories}
      totalProtein={dailyTotals.protein}
      totalCarbs={dailyTotals.carbs}
      totalFat={dailyTotals.fat}
      mealCount={mealsForDate.length}
    />

    <MealGrid
      meals={mealsForDate}
      {mealItemsMap}
      {foodMap}
      {macroTotals}
      onEdit={goToEdit}
      onDelete={handleDelete}
      onCreate={() => (formOpen = true)}
    />
  {/if}

  <MealForm
    open={formOpen}
    foodItems={foodItems ?? []}
    onSave={handleSave}
    onClose={() => (formOpen = false)}
  />
</div>
