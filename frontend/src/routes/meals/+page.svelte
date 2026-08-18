<script lang="ts">
  import { db } from '$lib/db/database';
  import { todayString, dateString } from '$lib/utils/datetime';
  import type { FoodItem, Meal, MealItem } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import DayNavigator from '$components/ui/DayNavigator.svelte';
  import Card from '$components/ui/Card.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import SegmentedControl from '$components/ui/SegmentedControl.svelte';
  import LineChart from '$components/dashboard/LineChart.svelte';
  import MealGroups from '$components/food/MealGroups.svelte';
  import MealForm from '$components/food/MealForm.svelte';
  import FoodDetailModal from '$components/food/FoodDetailModal.svelte';
  import FoodFormModal from '$components/food/FoodFormModal.svelte';
  import { createMeal, deleteMeal, updateMeal } from '$lib/mutations/meal';
  import { fetchNutritionTargets, type NutritionTargets } from '$lib/food/nutrition-goals';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { page } from '$app/state';

  let formOpen = $state(false);
  let formMealType = $state('snack');
  let preSelectedFoodId = $state<string | null>(null);
  let editMeal = $state<Meal | null>(null);
  let viewFood = $state<FoodItem | null>(null);
  let foodFormOpen = $state(false);
  let editFood = $state<FoodItem | null>(null);
  let viewMode = $state<'day' | 'week' | 'month'>('day');

  let selectedDate = $state(todayString());

  const dayQuery = useQuery(
    async () => {
      const meals = await db.meal
        .where('log_date')
        .equals(selectedDate)
        .filter((m) => !m.deleted_at)
        .toArray();
      const mealIds = meals.map((m) => m.id);
      const items =
        mealIds.length > 0
          ? await db.meal_item
              .where('meal_id')
              .anyOf(mealIds)
              .filter((mi) => !mi.deleted_at)
              .toArray()
          : [];
      return { meals, items };
    },
    () => selectedDate
  );
  const meals = $derived(dayQuery.value?.meals ?? []);
  const mealItems = $derived(dayQuery.value?.items ?? []);
  const foodItemsQuery = useQuery(() => db.notDeleted(db.food_item).toArray());
  const foodItems = $derived(foodItemsQuery.value);
  const targetsQuery = useQuery(() => fetchNutritionTargets());
  const targets = $derived(targetsQuery.value ?? ({} as NutritionTargets));
  const loading = $derived(foodItemsQuery.loading || dayQuery.loading);

  const today = $derived(todayString());
  const isToday = $derived(selectedDate === today);

  const mealsForDate = $derived(
    meals
      .filter((m) => m.log_date === selectedDate && !m.deleted_at)
      .sort((a, b) => (a.created_at ?? '').localeCompare(b.created_at ?? ''))
  );

  const mealItemsMap = $derived.by(() => {
    const map: Record<string, MealItem[]> = {};
    for (const mi of mealItems) {
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

  // ── Week / Month chart ──
  const rangeStart = $derived(
    viewMode === 'month' ? selectedDate.slice(0, 8) + '01' : startOfWeek(selectedDate)
  );
  const rangeQuery = useQuery(
    async () => {
      if (viewMode === 'day') return { meals: [] as Meal[], items: [] as MealItem[] };
      const meals = await db.meal
        .where('log_date')
        .between(rangeStart, selectedDate, true, true)
        .filter((m) => !m.deleted_at)
        .toArray();
      const ids = meals.map((m) => m.id);
      const items =
        ids.length > 0
          ? await db.meal_item
              .where('meal_id')
              .anyOf(ids)
              .filter((mi) => !mi.deleted_at)
              .toArray()
          : [];
      return { meals, items };
    },
    () => [viewMode, selectedDate]
  );
  const rangeMeals = $derived(rangeQuery.value?.meals ?? []);
  const rangeItems = $derived(rangeQuery.value?.items ?? []);

  const dayKcalMap = $derived.by(() => {
    const map: Record<string, number> = {};
    const mealByDate = new Map(rangeMeals.map((m) => [m.id, m.log_date]));
    for (const mi of rangeItems) {
      const food = foodMap[mi.food_item_id];
      if (!food) continue;
      const d = mealByDate.get(mi.meal_id) ?? selectedDate;
      map[d] = (map[d] ?? 0) + food.calories_per_serving * mi.servings;
    }
    return map;
  });

  const chartData = $derived.by(() => {
    if (viewMode === 'day') return null;
    const days: { label: string; kcal: number }[] = [];
    const start = new Date(rangeStart + 'T12:00');
    const end = new Date(selectedDate + 'T12:00');
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      const ds = dateString(d);
      days.push({
        label: new Date(ds + 'T12:00').toLocaleDateString('en-US', {
          weekday: 'short',
          day: 'numeric'
        }),
        kcal: Math.round(dayKcalMap[ds] ?? 0)
      });
    }
    const series = [
      {
        label: 'kcal',
        data: days.map((d) => d.kcal),
        color: 'var(--color-primary-500)',
        yAxis: 'left' as const
      }
    ];
    if (targets.calories != null) {
      series.push({
        label: 'Target',
        data: days.map(() => targets.calories!),
        color: 'var(--color-surface-300)',
        yAxis: 'left'
      });
    }
    return { labels: days.map((d) => d.label), series };
  });

  function startOfWeek(dateStr: string): string {
    const d = new Date(dateStr + 'T12:00');
    const diff = (d.getDay() + 6) % 7;
    d.setDate(d.getDate() - diff);
    return dateString(d);
  }

  async function handleSave(data: {
    id?: string;
    meal_type: string;
    name: string;
    notes: string;
    items: { food_item_id: string; servings: number }[];
  }) {
    const { id, ...rest } = data;
    if (id) {
      await updateMeal(id, rest);
    } else {
      await createMeal({ ...rest, log_date: selectedDate });
    }
    formOpen = false;
    editMeal = null;
  }

  async function handleDelete(mealId: string) {
    const { ok, error } = await deleteMeal(mealId);
    if (!ok) console.error('Failed to delete meal:', error);
  }

  async function handleUpdateItems(mealId: string, items: MealItem[]) {
    if (items.length === 0) {
      await deleteMeal(mealId);
      return;
    }
    await updateMeal(mealId, {
      items: items.map((i) => ({
        id: i.id,
        food_item_id: i.food_item_id,
        servings: i.servings,
        amount_g: i.amount_g ?? undefined
      }))
    });
  }

  function openEdit(mealId: string) {
    const meal = mealsForDate.find((m) => m.id === mealId) ?? null;
    editMeal = meal;
    formMealType = meal?.meal_type ?? 'snack';
    preSelectedFoodId = null;
    formOpen = true;
  }

  function openAdd(mealType: string) {
    editMeal = null;
    formMealType = mealType;
    preSelectedFoodId = null;
    formOpen = true;
  }

  function inferMealType(): string {
    const hour = new Date().getHours();
    if (hour < 11) return 'breakfast';
    if (hour < 15) return 'lunch';
    if (hour < 21) return 'dinner';
    return 'snack';
  }

  const addParam = $derived(page.url.searchParams.get('add'));
  const addServingsParam = $derived(page.url.searchParams.get('servings'));
  const initialServings = $derived(
    addServingsParam ? Math.max(0.25, parseFloat(addServingsParam) || 1) : 1
  );

  $effect(() => {
    if (!addParam) return;
    preSelectedFoodId = addParam;
    editMeal = null;
    formOpen = true;
  });
</script>

<svelte:head><title>Salus — Meals</title></svelte:head>

<div class="space-y-6">
  <PageHeader title="Meals" subtitle="Track your nutrition, one meal at a time" icon="restaurant">
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <PageHeaderAction icon="add" onclick={() => openAdd(inferMealType())}
          >Log Food</PageHeaderAction
        >
      </div>
    {/snippet}
    {#snippet stats()}
      {#if isToday}
        <div
          class="divide-surface-100 grid grid-cols-2 divide-y sm:grid-cols-4 sm:divide-x sm:divide-y-0"
        >
          <div class="px-6 py-4">
            <Stat
              value={Math.round(dailyTotals.calories)}
              unit={targets.calories != null
                ? `/ ${targets.calories.toLocaleString()} kcal`
                : 'kcal'}
              label="Calories"
            />
          </div>
          <div class="px-6 py-4">
            <Stat
              value={targets.protein != null ? Math.round(dailyTotals.protein) : '—'}
              unit={targets.protein != null ? `/ ${targets.protein} g` : 'g'}
              label="Protein"
            />
          </div>
          <div class="px-6 py-4">
            <Stat
              value={targets.carbs != null ? Math.round(dailyTotals.carbs) : '—'}
              unit={targets.carbs != null ? `/ ${targets.carbs} g` : 'g'}
              label="Carbs"
            />
          </div>
          <div class="px-6 py-4">
            <Stat
              value={targets.fat != null ? Math.round(dailyTotals.fat) : '—'}
              unit={targets.fat != null ? `/ ${targets.fat} g` : 'g'}
              label="Fat"
            />
          </div>
        </div>
      {/if}
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="flex justify-center py-20">
      <Spinner />
    </div>
  {:else}
    <div class="flex flex-wrap items-center justify-between gap-3">
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
              class="text-primary-600 hover:text-primary-700 text-xs"
              onclick={() => (selectedDate = today)}
            >
              Today
            </button>
          {/if}
        {/snippet}
      </DayNavigator>

      <SegmentedControl
        options={[
          { value: 'day', label: 'Day' },
          { value: 'week', label: 'Week' },
          { value: 'month', label: 'Month' }
        ]}
        bind:value={viewMode}
      />
    </div>

    {#if viewMode === 'day'}
      {#if mealsForDate.length > 0}
        <MealGroups
          meals={mealsForDate}
          {mealItemsMap}
          {foodMap}
          {macroTotals}
          onEdit={openEdit}
          onDelete={handleDelete}
          onUpdateItems={handleUpdateItems}
          onAdd={openAdd}
          onViewFood={(food) => (viewFood = food)}
        />
      {:else}
        <Card>
          <div class="flex flex-col items-center gap-2 py-8 text-center">
            <p class="text-surface-700 text-sm font-medium">No meals logged yet</p>
            <p class="text-surface-400 max-w-sm text-xs">
              Use the "Log Food" button or the "+ Add" buttons to start tracking your nutrition.
            </p>
          </div>
        </Card>
      {/if}
    {:else}
      <Card padding={false}>
        {#snippet header()}
          <span class="text-surface-900 text-sm font-semibold">
            {viewMode === 'week' ? 'This Week' : 'This Month'} · Calories
          </span>
        {/snippet}
        <div class="p-6">
          {#if chartData}
            <LineChart
              labels={chartData.labels}
              series={chartData.series}
              leftUnit="kcal"
              height={240}
            />
          {:else}
            <div class="flex h-[200px] items-center justify-center">
              <p class="text-surface-400 text-sm">No meals in this range.</p>
            </div>
          {/if}
        </div>
      </Card>
    {/if}
  {/if}

  <MealForm
    open={formOpen}
    foodItems={foodItems ?? []}
    initialMealType={formMealType}
    initialFoodId={preSelectedFoodId}
    {initialServings}
    meal={editMeal}
    mealItems={editMeal ? (mealItemsMap[editMeal.id ?? ''] ?? []) : []}
    onSave={handleSave}
    onClose={() => {
      formOpen = false;
      editMeal = null;
      preSelectedFoodId = null;
    }}
  />

  <FoodDetailModal
    food={viewFood}
    onEdit={(food) => {
      viewFood = null;
      editFood = food;
      foodFormOpen = true;
    }}
    onClose={() => (viewFood = null)}
  />

  <FoodFormModal
    open={foodFormOpen}
    food={editFood}
    onClose={() => {
      foodFormOpen = false;
      editFood = null;
    }}
  />
</div>
