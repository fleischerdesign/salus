<script lang="ts">
  import { db } from '$lib/db/database';
  import { todayString, dateString } from '$lib/utils/datetime';
  import type { FoodItem, Meal, MealItem } from '$lib/db/types';
  import { goto } from '$app/navigation';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import DayNavigator from '$components/ui/DayNavigator.svelte';
  import Card from '$components/ui/Card.svelte';
  import NutritionSummary from '$components/food/NutritionSummary.svelte';
  import MealGrid from '$components/food/MealGrid.svelte';
  import MealForm from '$components/food/MealForm.svelte';
  import { createMeal, deleteMeal } from '$lib/mutations/meal';
  import { useQuery } from '$lib/db/use-query.svelte';

  let formOpen = $state(false);
  let viewMode = $state<'day' | 'week' | 'month'>('day');

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

  // ── Week / Month overview ──
  const rangeStart = $derived(
    viewMode === 'month' ? selectedDate.slice(0, 8) + '01' : startOfWeek(selectedDate)
  );
  const rangeMealsQuery = useQuery(async () => {
    if (viewMode === 'day') return [] as Meal[];
    return db.meal
      .where('log_date')
      .between(rangeStart, selectedDate, true, true)
      .filter((m) => !m.deleted_at)
      .toArray();
  });
  const rangeMeals = $derived(rangeMealsQuery.value);
  const rangeItemsQuery = useQuery(async () => {
    const ids = (rangeMeals ?? []).map((m) => m.id);
    if (ids.length === 0) return [] as MealItem[];
    return db.meal_item
      .where('meal_id')
      .anyOf(ids)
      .filter((mi) => !mi.deleted_at)
      .toArray();
  });
  const rangeItems = $derived(rangeItemsQuery.value);

  const dailySummary = $derived.by(() => {
    const map: Record<
      string,
      { calories: number; protein: number; carbs: number; fat: number; count: number }
    > = {};
    for (const meal of rangeMeals ?? []) {
      const d = meal.log_date;
      if (!map[d]) map[d] = { calories: 0, protein: 0, carbs: 0, fat: 0, count: 0 };
      map[d].count += 1;
    }
    const mealByDate = new Map((rangeMeals ?? []).map((m) => [m.id, m.log_date]));
    for (const mi of rangeItems ?? []) {
      const food = foodMap[mi.food_item_id];
      if (!food) continue;
      const d = mealByDate.get(mi.meal_id) ?? selectedDate;
      if (!map[d]) map[d] = { calories: 0, protein: 0, carbs: 0, fat: 0, count: 0 };
      map[d].calories += food.calories_per_serving * mi.servings;
      map[d].protein += food.protein_g * mi.servings;
      map[d].carbs += food.carbs_g * mi.servings;
      map[d].fat += food.fat_g * mi.servings;
    }
    return Object.entries(map)
      .map(([date, totals]) => ({ date, ...totals }))
      .sort((a, b) => b.date.localeCompare(a.date));
  });

  function startOfWeek(dateStr: string): string {
    const d = new Date(dateStr + 'T12:00');
    const diff = (d.getDay() + 6) % 7;
    d.setDate(d.getDate() - diff);
    return dateString(d);
  }

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
        <PageHeaderAction variant="secondary" icon="search" onclick={() => goto('/food')}
          >Food DB</PageHeaderAction
        >
        <PageHeaderAction variant="secondary" icon="menu-book" onclick={() => goto('/recipes')}
          >Recipes</PageHeaderAction
        >
        <PageHeaderAction icon="add" onclick={() => (formOpen = true)}>Log Meal</PageHeaderAction>
      </div>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="flex justify-center py-20">
      <Spinner />
    </div>
  {:else}
    <div class="flex items-center justify-between gap-3">
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

      <div class="flex overflow-hidden rounded-md border border-surface-200">
        {#each ['day', 'week', 'month'] as const as mode}
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium capitalize transition-colors {viewMode === mode
              ? 'bg-primary-500 text-on-primary'
              : 'text-surface-500 hover:bg-surface-100'}"
            onclick={() => (viewMode = mode)}
          >
            {mode}
          </button>
        {/each}
      </div>
    </div>

    {#if viewMode === 'day'}
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
    {:else}
      <Card>
        <h2 class="mb-3 text-sm font-semibold tracking-wider text-surface-400 uppercase">
          {viewMode === 'week' ? 'This Week' : 'This Month'}
        </h2>
        {#if dailySummary.length > 0}
          <div class="divide-y divide-surface-100">
            {#each dailySummary as day}
              <button
                type="button"
                class="flex w-full items-center justify-between py-2.5 text-left hover:bg-surface-50"
                onclick={() => {
                  selectedDate = day.date;
                  viewMode = 'day';
                }}
              >
                <div>
                  <div class="text-sm font-medium text-surface-800">
                    {new Date(day.date + 'T12:00').toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric'
                    })}
                  </div>
                  <div class="text-xs text-surface-400">
                    {day.count}
                    {day.count === 1 ? 'meal' : 'meals'}
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-semibold text-surface-900">
                    {Math.round(day.calories)} kcal
                  </div>
                  <div class="text-xs text-surface-400">
                    {Math.round(day.protein)}P · {Math.round(day.carbs)}C · {Math.round(day.fat)}F
                  </div>
                </div>
              </button>
            {/each}
          </div>
        {:else}
          <p class="py-6 text-center text-sm text-surface-400">No meals in this range.</p>
        {/if}
      </Card>
    {/if}
  {/if}

  <MealForm
    open={formOpen}
    foodItems={foodItems ?? []}
    onSave={handleSave}
    onClose={() => (formOpen = false)}
  />
</div>
