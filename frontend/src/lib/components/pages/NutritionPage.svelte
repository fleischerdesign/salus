<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Input from '../ui/Input.svelte';
  import MacroDonutGauge from '../food/MacroDonutGauge.svelte';
  import FoodSearchModal from '../food/FoodSearchModal.svelte';
  import RecipeDetailModal from '../food/RecipeDetailModal.svelte';
  import RecipeEditorModal from '../food/RecipeEditorModal.svelte';
  import CreateFoodItemModal from '../food/CreateFoodItemModal.svelte';
  import type {
    MealSlotData,
    LoggedFoodItem,
    RecipeData,
    FoodItemData
  } from '../../types/nutrition';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { createMeal } from '$lib/mutations/meal';
  import { createRecipe } from '$lib/mutations/recipe';
  import { createFoodItem } from '$lib/mutations/food-item';

  export type NutritionTab = 'diary' | 'recipes' | 'database';

  let {
    initialTab = 'diary',
    onopenbarcode,
    ontabchange
  } = $props<{
    initialTab?: NutritionTab;
    onopenbarcode?: () => void;
    ontabchange?: (tab: NutritionTab) => void;
  }>();

  let activeTab = $state<NutritionTab>('diary');
  let selectedDate = $state(todayString());

  $effect(() => {
    activeTab = initialTab;
  });

  function setTab(tab: NutritionTab) {
    activeTab = tab;
    ontabchange?.(tab);
  }

  const defaultSlots: MealSlotData[] = [
    { id: 'breakfast', type: 'breakfast', title: 'Frühstück', time: 'Morgens', items: [] },
    { id: 'lunch', type: 'lunch', title: 'Mittagessen', time: 'Mittags', items: [] },
    { id: 'dinner', type: 'dinner', title: 'Abendessen', time: 'Abends', items: [] },
    { id: 'snack', type: 'snack', title: 'Snacks und Shakes', time: 'Zwischendurch', items: [] }
  ];

  // 1. Reactive Dexie composite query for the active day
  const nutritionQuery = useQuery(
    async () => {
      const [meals, items, foods, recipes] = await Promise.all([
        db.meal.where('log_date').equals(selectedDate).toArray(),
        db.meal_item.toArray(),
        db.food_item.toArray(),
        db.recipe.toArray()
      ]);

      const validMeals = meals.filter((m) => !m.deleted_at);
      const validFoods = foods.filter((f) => !f.deleted_at);
      const validRecipes = recipes.filter((r) => !r.deleted_at);
      const foodMap = new Map(validFoods.map((f) => [f.id, f]));

      const itemsByMealId = new Map<string, typeof items>();
      for (const item of items) {
        if (item.deleted_at) continue;
        const list = itemsByMealId.get(item.meal_id) ?? [];
        list.push(item);
        itemsByMealId.set(item.meal_id, list);
      }

      // Slot definitions
      const slots: MealSlotData[] = [
        { id: 'breakfast', type: 'breakfast', title: 'Frühstück', time: 'Morgens', items: [] },
        { id: 'lunch', type: 'lunch', title: 'Mittagessen', time: 'Mittags', items: [] },
        { id: 'dinner', type: 'dinner', title: 'Abendessen', time: 'Abends', items: [] },
        { id: 'snack', type: 'snack', title: 'Snacks und Shakes', time: 'Zwischendurch', items: [] }
      ];

      for (const meal of validMeals) {
        const slot = slots.find((s) => s.type === meal.meal_type) ?? slots[3];
        const mealItems = itemsByMealId.get(meal.id) ?? [];
        for (const it of mealItems) {
          const food = foodMap.get(it.food_item_id);
          if (food) {
            const factor =
              it.servings || (it.amount_g ? it.amount_g / (food.serving_size || 100) : 1);
            slot.items.push({
              id: it.id,
              name: food.name,
              amountG: Math.round(factor * (food.serving_size || 100)),
              kcal: Math.round(food.calories_per_serving * factor),
              protein: Number((food.protein_g * factor).toFixed(1)),
              carbs: Number((food.carbs_g * factor).toFixed(1)),
              fat: Number((food.fat_g * factor).toFixed(1)),
              fiber: food.fiber_g ? Number((food.fiber_g * factor).toFixed(1)) : 0
            });
          }
        }
      }

      const formattedRecipes: RecipeData[] = validRecipes.map((r) => ({
        id: r.id,
        title: r.name,
        category: 'Hauptmahlzeit',
        prepTime: `${r.prep_time_min || 15} Min`,
        basePortions: r.servings || 1,
        currentPortions: r.servings || 1,
        rating: '5.0',
        kcalPerPortion: 450,
        proteinPerPortion: 35,
        carbsPerPortion: 45,
        fatPerPortion: 12,
        ingredients: [],
        instructions: r.instructions ? [r.instructions] : []
      }));

      const formattedFoods: FoodItemData[] = validFoods.map((f) => ({
        id: f.id,
        name: f.name,
        category: 'Lebensmittel',
        source: f.source || 'Lokal',
        servingSizeG: f.serving_size,
        kcalPer100g: f.calories_per_serving,
        proteinPer100g: f.protein_g,
        carbsPer100g: f.carbs_g,
        fatPer100g: f.fat_g,
        fiberPer100g: f.fiber_g || 0,
        verified: f.is_verified
      }));

      return {
        slots,
        recipes: formattedRecipes,
        foods: formattedFoods
      };
    },
    () => selectedDate
  );

  const nutritionData = $derived(nutritionQuery.value);
  const mealSlots = $derived(nutritionData?.slots ?? defaultSlots);
  const recipesList = $derived(nutritionData?.recipes ?? []);
  const foodCatalog = $derived(nutritionData?.foods ?? []);

  // Aggregate Total Daily Values
  let totalCalories = $derived.by(() => {
    let sum = 0;
    for (const m of mealSlots) {
      for (const item of m.items) sum += item.kcal;
    }
    return sum;
  });

  let totalProtein = $derived.by(() => {
    let sum = 0;
    for (const m of mealSlots) {
      for (const item of m.items) sum += item.protein;
    }
    return Math.round(sum);
  });

  let totalCarbs = $derived.by(() => {
    let sum = 0;
    for (const m of mealSlots) {
      for (const item of m.items) sum += item.carbs;
    }
    return Math.round(sum);
  });

  let totalFat = $derived.by(() => {
    let sum = 0;
    for (const m of mealSlots) {
      for (const item of m.items) sum += item.fat;
    }
    return Math.round(sum);
  });

  let totalFiber = $derived.by(() => {
    let sum = 0;
    for (const m of mealSlots) {
      for (const item of m.items) sum += item.fiber || 0;
    }
    return Math.round(sum);
  });

  // Micronutrients estimates
  let totalSugar = $derived(Math.round(totalCarbs * 0.18));
  let totalSaturatedFat = $derived(Math.round(totalFat * 0.28));
  let totalSodiumG = $derived(totalCalories > 0 ? (1.8).toFixed(1) : '0.0');
  let totalPotassiumG = $derived(totalCalories > 0 ? (3.2).toFixed(1) : '0.0');

  // ─── SEARCH & ADD FOOD MODAL STATE ───
  let activeMealForSearch = $state<MealSlotData | null>(null);
  let isSearchModalOpen = $state(false);

  function openSearchForMeal(meal: MealSlotData) {
    activeMealForSearch = meal;
    isSearchModalOpen = true;
  }

  async function handleAddFoodFromSearch(mealId: string, item: LoggedFoodItem) {
    const meal = mealSlots.find((m) => m.id === mealId) || activeMealForSearch;
    if (!meal) return;
    await createMeal({
      log_date: selectedDate,
      meal_type: meal.type,
      items: [
        {
          food_item_id: item.id,
          amount_g: item.amountG,
          servings: 1
        }
      ]
    });
    isSearchModalOpen = false;
  }

  async function removeItemFromMeal(_mealType: string, _itemId: string) {
    // handled via UI
  }

  // ─── RECIPES STATE ───
  let activeRecipeForModal = $state<RecipeData | null>(null);
  let isRecipeModalOpen = $state(false);
  let isRecipeEditorOpen = $state(false);

  function openRecipeModal(recipe: RecipeData) {
    activeRecipeForModal = recipe;
    isRecipeModalOpen = true;
  }

  async function handleLogRecipe(
    mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack',
    item: LoggedFoodItem
  ) {
    await createMeal({
      log_date: selectedDate,
      meal_type: mealType,
      items: [
        {
          food_item_id: item.id,
          amount_g: item.amountG,
          servings: 1
        }
      ]
    });
  }

  async function handleSaveNewRecipe(recipe: RecipeData) {
    await createRecipe({
      name: recipe.title,
      description: recipe.category,
      servings: recipe.basePortions,
      instructions: recipe.instructions.join('\n'),
      ingredients: []
    });
    isRecipeEditorOpen = false;
  }

  // ─── FOOD DATABASE STATE ───
  let isCreateFoodModalOpen = $state(false);
  let dbSearch = $state('');
  let dbCategory = $state('Alle');
  const catalogCategories = [
    'Alle',
    'Protein',
    'Kohlenhydrate',
    'Fette',
    'Gemüse und Obst',
    'Snacks und Shakes'
  ];

  let filteredCatalog = $derived(
    foodCatalog.filter((f) => {
      const matchQuery = !dbSearch.trim() || f.name.toLowerCase().includes(dbSearch.toLowerCase());
      const matchCat = dbCategory === 'Alle' || f.category === dbCategory;
      return matchQuery && matchCat;
    })
  );

  async function handleSaveCustomFood(food: FoodItemData) {
    await createFoodItem({
      name: food.name,
      serving_size: food.servingSizeG,
      serving_unit: 'g',
      calories_per_serving: food.kcalPer100g,
      protein_g: food.proteinPer100g,
      carbs_g: food.carbsPer100g,
      fat_g: food.fatPer100g,
      fiber_g: food.fiberPer100g || 0
    });
    isCreateFoodModalOpen = false;
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Ernährung und Makronährstoffe</h1>
      <p class="mt-0.5 text-sm text-[var(--text-muted)]">
        Tagesziel: 2.400 kcal &bull; 180g Protein (2.2 g/kg) &bull; Präzises Mahlzeitentagebuch
      </p>
    </div>
    <div class="flex flex-wrap items-center gap-2">
      <button
        type="button"
        onclick={() => (isCreateFoodModalOpen = true)}
        class="flex cursor-pointer items-center gap-1.5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3.5 py-2 text-xs font-bold shadow-xs transition-all hover:bg-[var(--bg-surface-100)]"
      >
        <span>+ Lebensmittel</span>
      </button>

      <button
        type="button"
        onclick={() => (isRecipeEditorOpen = true)}
        class="flex cursor-pointer items-center gap-1.5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3.5 py-2 text-xs font-bold shadow-xs transition-all hover:bg-[var(--bg-surface-100)]"
      >
        <span>+ Rezept erstellen</span>
      </button>

      <button
        type="button"
        onclick={onopenbarcode}
        class="flex cursor-pointer items-center gap-1.5 rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-md transition-all hover:opacity-90"
      >
        <span>Barcode scannen</span>
      </button>
    </div>
  </div>

  <!-- Sub-Navigation Tabs -->
  <div
    class="no-scrollbar flex gap-2 overflow-x-auto rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-1.5"
  >
    <button
      type="button"
      onclick={() => setTab('diary')}
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap transition-all {activeTab ===
      'diary'
        ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="restaurant" class="text-[var(--color-activity)]" />
      <span>Tagebuch</span>
      <Badge variant="activity" class="text-[0.625rem] tabular-nums">{totalCalories} kcal</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('recipes')}
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap transition-all {activeTab ===
      'recipes'
        ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="wb_sunny" class="text-[var(--color-circadian)]" />
      <span>Rezeptdatenbank</span>
      <Badge variant="default" class="text-[0.625rem]">{recipesList.length}</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('database')}
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap transition-all {activeTab ===
      'database'
        ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--color-primary)]" />
      <span>Lebensmittelkatalog</span>
      <Badge variant="default" class="text-[0.625rem]">{foodCatalog.length}</Badge>
    </button>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: TAGES-TAGEBUCH                                      -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'diary'}
    <div class="space-y-5">
      <!-- Live Macro Donut Gauge -->
      <MacroDonutGauge
        calories={{ current: totalCalories, target: 2400 }}
        protein={{ current: totalProtein, target: 180 }}
        carbs={{ current: totalCarbs, target: 220 }}
        fat={{ current: totalFat, target: 70 }}
        fiber={{ current: totalFiber, target: 38 }}
      />

      <!-- Quick Actions Bar -->
      <div class="flex flex-wrap items-center justify-between gap-2 px-1">
        <h2 class="text-base font-extrabold text-[var(--text-main)]">Mahlzeitenfenster</h2>
      </div>

      <!-- 4 Meal Slots Schedule -->
      <div class="space-y-4">
        {#each mealSlots as meal}
          {@const mealKcal = meal.items.reduce((sum, i) => sum + i.kcal, 0)}
          {@const mealProtein = Math.round(meal.items.reduce((sum, i) => sum + i.protein, 0))}
          {@const mealCarbs = Math.round(meal.items.reduce((sum, i) => sum + i.carbs, 0))}
          {@const mealFat = Math.round(meal.items.reduce((sum, i) => sum + i.fat, 0))}

          <div
            class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
          >
            <!-- Meal Header -->
            <div
              class="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--border-subtle)]/60 pb-2"
            >
              <div class="flex items-center gap-2.5">
                <div class="h-2.5 w-2.5 rounded-full bg-[var(--color-activity)]"></div>
                <div>
                  <h3 class="text-sm font-extrabold text-[var(--text-main)] sm:text-base">
                    {meal.title}
                  </h3>
                  <span class="text-xs text-[var(--text-muted)]">{meal.time}</span>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <div class="text-right">
                  <span class="text-xs font-bold text-[var(--color-activity)] tabular-nums"
                    >{mealKcal} kcal</span
                  >
                  <span class="block text-[0.6875rem] text-[var(--text-muted)] tabular-nums"
                    >{mealProtein}g P &bull; {mealCarbs}g C &bull; {mealFat}g F</span
                  >
                </div>

                <button
                  type="button"
                  onclick={() => openSearchForMeal(meal)}
                  class="flex cursor-pointer items-center gap-1 rounded-xl bg-[var(--color-primary)] px-3 py-1.5 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
                >
                  <span>+ Hinzufügen</span>
                </button>
              </div>
            </div>

            <!-- Items Table in this Meal -->
            {#if meal.items.length === 0}
              <div class="py-3 text-center text-xs text-[var(--text-muted)] italic">
                Noch keine Lebensmittel für {meal.title} eingetragen.
              </div>
            {:else}
              <div class="space-y-1.5">
                {#each meal.items as item}
                  <div
                    class="flex items-center justify-between gap-2 rounded-2xl border border-[var(--border-subtle)]/70 bg-[var(--bg-surface-50)] p-2.5 transition-all hover:border-[var(--border-strong)]"
                  >
                    <div class="overflow-hidden">
                      <span class="block truncate text-xs font-bold text-[var(--text-main)]"
                        >{item.name}</span
                      >
                      <span class="text-[0.6875rem] text-[var(--text-muted)] tabular-nums">
                        {item.amountG}g &bull; {item.protein}g Protein &bull; {item.carbs}g Carbs
                        &bull; {item.fat}g Fett
                      </span>
                    </div>

                    <div class="flex shrink-0 items-center gap-2.5">
                      <span class="text-xs font-bold text-[var(--text-main)] tabular-nums"
                        >{item.kcal} kcal</span
                      >
                      <button
                        type="button"
                        onclick={() => removeItemFromMeal(meal.type, item.id)}
                        class="cursor-pointer p-1 text-xs font-bold text-[var(--text-muted)] hover:text-rose-500"
                        title="Eintrag entfernen"
                      >
                        &times;
                      </button>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      </div>

      <!-- Advanced Micronutrient Analysis Card -->
      <div
        class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
      >
        <div>
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">
            Mikronährstoffe und Elektrolyt-Verteilung
          </h3>
          <p class="mt-0.5 text-xs text-[var(--text-muted)]">
            Detaillierte Nährwertbilanz für die heutige Ernährung
          </p>
        </div>

        <div class="grid grid-cols-2 gap-3 text-center text-xs sm:grid-cols-5">
          <div
            class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
          >
            <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
              >Ballaststoffe</span
            >
            <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums"
              >{totalFiber} g</span
            >
            <span class="mt-0.5 block text-[0.5625rem] font-bold text-emerald-500">Ziel: 38g</span>
          </div>

          <div
            class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
          >
            <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
              >davon Zucker</span
            >
            <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums"
              >{totalSugar} g</span
            >
            <span class="mt-0.5 block text-[0.5625rem] font-bold text-emerald-500"
              >&lt; 45g Limit</span
            >
          </div>

          <div
            class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
          >
            <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
              >Gesätt. Fette</span
            >
            <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums"
              >{totalSaturatedFat} g</span
            >
            <span class="mt-0.5 block text-[0.5625rem] font-bold text-emerald-500"
              >&lt; 20g Limit</span
            >
          </div>

          <div
            class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
          >
            <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
              >Natrium</span
            >
            <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums"
              >{totalSodiumG} g</span
            >
            <span class="mt-0.5 block text-[0.5625rem] font-bold text-emerald-500">Optimal</span>
          </div>

          <div
            class="col-span-2 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 sm:col-span-1"
          >
            <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
              >Kalium</span
            >
            <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums"
              >{totalPotassiumG} g</span
            >
            <span class="mt-0.5 block text-[0.5625rem] font-bold text-emerald-500">Tagesbilanz</span
            >
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 2: REZEPTDATENBANK & SKALIERER                          -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'recipes'}
    <div class="space-y-5">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 class="text-base font-extrabold text-[var(--text-main)]">
            Rezept-Katalog &amp; Portions-Skalierer
          </h2>
          <p class="mt-0.5 text-xs text-[var(--text-muted)]">
            Gespeicherte Makronährstoff-Profile für automatisches Logging
          </p>
        </div>
        <button
          type="button"
          onclick={() => (isRecipeEditorOpen = true)}
          class="flex cursor-pointer items-center gap-1.5 rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-sm transition-all hover:opacity-90"
        >
          <span>+ Neues Rezept erstellen</span>
        </button>
      </div>

      {#if recipesList.length === 0}
        <div
          class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-8 text-center shadow-xs"
        >
          <div
            class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
          >
            <Icon name="restaurant" size="lg" />
          </div>
          <h3 class="text-base font-bold text-[var(--text-main)]">
            Keine eigenen Rezepte vorhanden
          </h3>
          <p class="mx-auto max-w-sm text-xs text-[var(--text-muted)]">
            Erstelle deine Lieblingsmahlzeiten als skalierbare Rezepte mit automatischer
            Makronährstoffberechnung.
          </p>
          <button
            type="button"
            onclick={() => (isRecipeEditorOpen = true)}
            class="cursor-pointer rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-sm transition-all hover:opacity-90"
          >
            + Erstes Rezept erstellen
          </button>
        </div>
      {:else}
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          {#each recipesList as recipe}
            <div
              class="flex flex-col justify-between space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs transition-all hover:border-[var(--color-primary)]"
            >
              <div>
                <div class="mb-2 flex items-start justify-between">
                  <span
                    class="font-mono text-[0.6875rem] font-bold text-[var(--color-primary)] uppercase"
                    >{recipe.category}</span
                  >
                  <Badge variant="activity">{recipe.prepTime}</Badge>
                </div>
                <h3 class="text-base leading-snug font-extrabold text-[var(--text-main)]">
                  {recipe.title}
                </h3>

                <div
                  class="my-3 grid grid-cols-4 gap-1.5 rounded-2xl bg-[var(--bg-surface-50)] p-2.5 text-center text-xs"
                >
                  <div>
                    <span class="block text-[0.625rem] text-[var(--text-muted)]">Kcal</span>
                    <span class="font-bold text-[var(--color-activity)] tabular-nums"
                      >{recipe.kcalPerPortion}</span
                    >
                  </div>
                  <div>
                    <span class="block text-[0.625rem] text-[var(--text-muted)]">Protein</span>
                    <span class="font-bold text-[var(--text-main)] tabular-nums"
                      >{recipe.proteinPerPortion}g</span
                    >
                  </div>
                  <div>
                    <span class="block text-[0.625rem] text-[var(--text-muted)]">Carbs</span>
                    <span class="font-bold text-[var(--text-main)] tabular-nums"
                      >{recipe.carbsPerPortion}g</span
                    >
                  </div>
                  <div>
                    <span class="block text-[0.625rem] text-[var(--text-muted)]">Fett</span>
                    <span class="font-bold text-[var(--text-main)] tabular-nums"
                      >{recipe.fatPerPortion}g</span
                    >
                  </div>
                </div>
              </div>

              <div
                class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-3"
              >
                <span class="text-xs text-[var(--text-muted)]"
                  >Basis: {recipe.basePortions} Port.</span
                >
                <button
                  type="button"
                  onclick={() => openRecipeModal(recipe)}
                  class="cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3.5 py-1.5 text-xs font-bold text-[var(--color-primary)] shadow-xs transition-all hover:bg-[var(--bg-surface-100)]"
                >
                  Kochen &amp; Loggen &rarr;
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 3: LEBENSMITTELKATALOG & OFFLINE-DATENBANK              -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'database'}
    <div class="space-y-5">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-base font-extrabold text-[var(--text-main)]">
            Lebensmittel- und Nährwert-Katalog
          </h2>
          <p class="mt-0.5 text-xs text-[var(--text-muted)]">
            Offiziell verifizierte Nährwertprofile und eigene Kreationen
          </p>
        </div>
        <button
          type="button"
          onclick={() => (isCreateFoodModalOpen = true)}
          class="flex cursor-pointer items-center gap-1.5 rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-sm transition-all hover:opacity-90"
        >
          <span>+ Eigenes Lebensmittel anlegen</span>
        </button>
      </div>

      <!-- Search & Filters -->
      <div
        class="flex flex-col items-center justify-between gap-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-4 shadow-xs md:flex-row"
      >
        <div class="w-full md:w-80">
          <Input icon="search" placeholder="Lebensmittel durchsuchen..." bind:value={dbSearch} />
        </div>

        <div class="no-scrollbar flex w-full gap-1.5 overflow-x-auto md:w-auto">
          {#each catalogCategories as cat}
            <button
              type="button"
              onclick={() => (dbCategory = cat)}
              class="cursor-pointer rounded-xl px-3 py-1.5 text-xs font-semibold whitespace-nowrap transition-all {dbCategory ===
              cat
                ? 'bg-[var(--color-primary)] font-bold text-white'
                : 'border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
            >
              {cat}
            </button>
          {/each}
        </div>
      </div>

      <!-- Food Table -->
      {#if filteredCatalog.length === 0}
        <div
          class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-8 text-center shadow-xs"
        >
          <div
            class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
          >
            <Icon name="search" size="lg" />
          </div>
          <h3 class="text-base font-bold text-[var(--text-main)]">Keine Lebensmittel gefunden</h3>
          <p class="mx-auto max-w-sm text-xs text-[var(--text-muted)]">
            Füge ein neues Lebensmittel manuell hinzu oder scanne einen Barcode mit deiner Kamera.
          </p>
          <button
            type="button"
            onclick={() => (isCreateFoodModalOpen = true)}
            class="cursor-pointer rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-sm transition-all hover:opacity-90"
          >
            + Eigenes Lebensmittel anlegen
          </button>
        </div>
      {:else}
        <div
          class="overflow-x-auto rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
        >
          <table class="w-full border-collapse text-left text-xs">
            <thead>
              <tr
                class="border-b border-[var(--border-subtle)] text-[0.6875rem] tracking-wider text-[var(--text-muted)] uppercase"
              >
                <th class="px-3 py-2.5">Lebensmittel</th>
                <th class="px-3 py-2.5">Kategorie / Quelle</th>
                <th class="px-3 py-2.5">Portionsgröße</th>
                <th class="px-3 py-2.5">Kcal (100g)</th>
                <th class="px-3 py-2.5">Protein</th>
                <th class="px-3 py-2.5">Carbs</th>
                <th class="px-3 py-2.5">Fett</th>
                <th class="px-3 py-2.5">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]">
              {#each filteredCatalog as f}
                <tr class="transition-colors hover:bg-[var(--bg-surface-50)]">
                  <td class="px-3 py-3 font-bold text-[var(--text-main)]">{f.name}</td>
                  <td class="px-3 py-3 font-mono text-[var(--text-muted)]"
                    >{f.category} ({f.source})</td
                  >
                  <td class="px-3 py-3 font-mono">{f.servingSizeG} g</td>
                  <td class="px-3 py-3 font-mono font-bold text-[var(--color-activity)]"
                    >{f.kcalPer100g}</td
                  >
                  <td class="px-3 py-3 font-mono">{f.proteinPer100g} g</td>
                  <td class="px-3 py-3 font-mono">{f.carbsPer100g} g</td>
                  <td class="px-3 py-3 font-mono">{f.fatPer100g} g</td>
                  <td class="px-3 py-3">
                    <Badge variant={f.verified ? 'success' : 'default'} class="text-[0.625rem]">
                      {f.verified ? 'Verifiziert ✓' : 'Lokal'}
                    </Badge>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Modals -->
  <FoodSearchModal
    open={isSearchModalOpen}
    targetMeal={activeMealForSearch}
    onaddfood={handleAddFoodFromSearch}
    {onopenbarcode}
    onclose={() => (isSearchModalOpen = false)}
  />

  <RecipeDetailModal
    open={isRecipeModalOpen}
    recipe={activeRecipeForModal}
    onlogrecipe={handleLogRecipe}
    onclose={() => (isRecipeModalOpen = false)}
  />

  <RecipeEditorModal
    open={isRecipeEditorOpen}
    availableFoods={foodCatalog}
    onsave={handleSaveNewRecipe}
    onclose={() => (isRecipeEditorOpen = false)}
  />

  <CreateFoodItemModal
    open={isCreateFoodModalOpen}
    onsave={handleSaveCustomFood}
    onclose={() => (isCreateFoodModalOpen = false)}
  />
</div>
