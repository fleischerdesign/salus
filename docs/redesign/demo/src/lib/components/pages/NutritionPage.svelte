<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import MacroDonutGauge from '../food/MacroDonutGauge.svelte';
  import FoodSearchModal from '../food/FoodSearchModal.svelte';
  import RecipeDetailModal from '../food/RecipeDetailModal.svelte';
  import RecipeEditorModal from '../food/RecipeEditorModal.svelte';
  import CreateFoodItemModal from '../food/CreateFoodItemModal.svelte';
  import type { MealSlotData, LoggedFoodItem, RecipeData, FoodItemData } from '../../types/nutrition';

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

  $effect(() => {
    activeTab = initialTab;
  });

  function setTab(tab: NutritionTab) {
    activeTab = tab;
    ontabchange?.(tab);
  }

  // ─── 4 MEAL SLOTS STATE ───
  let mealSlots = $state<MealSlotData[]>([
    {
      id: 'meal_breakfast',
      type: 'breakfast',
      title: 'Frühstück',
      time: '08:30 Uhr',
      items: [
        { id: 'i1', name: 'Bio-Eier (Größe L)', amountG: 180, kcal: 225, protein: 20.0, carbs: 1.2, fat: 15.6, fiber: 0 },
        { id: 'i2', name: 'Vollkorn-Sauerteigbrot', amountG: 90, kcal: 210, protein: 7.5, carbs: 40.0, fat: 1.8, fiber: 5.4 },
        { id: 'i3', name: 'Avocado Hass', amountG: 60, kcal: 105, protein: 1.2, carbs: 1.0, fat: 9.6, fiber: 4.0 }
      ]
    },
    {
      id: 'meal_lunch',
      type: 'lunch',
      title: 'Mittagessen',
      time: '13:15 Uhr',
      items: [
        { id: 'i4', name: 'Hähnchenbrustfilet (Bio)', amountG: 200, kcal: 220, protein: 47.0, carbs: 0.0, fat: 3.0, fiber: 0 },
        { id: 'i5', name: 'Basmatireis (gekocht)', amountG: 220, kcal: 280, protein: 6.8, carbs: 61.6, fat: 0.6, fiber: 1.2 },
        { id: 'i6', name: 'Brokkoli gedämpft', amountG: 150, kcal: 51, protein: 4.2, carbs: 6.0, fat: 0.6, fiber: 4.5 }
      ]
    },
    {
      id: 'meal_dinner',
      type: 'dinner',
      title: 'Abendessen',
      time: '19:45 Uhr',
      items: [
        { id: 'i7', name: 'Wildlachsfilet (MSC)', amountG: 160, kcal: 285, protein: 32.0, carbs: 0.0, fat: 17.6, fiber: 0 },
        { id: 'i8', name: 'Süßkartoffel aus dem Ofen', amountG: 200, kcal: 172, protein: 3.2, carbs: 40.2, fat: 0.2, fiber: 6.0 },
        { id: 'i9', name: 'Blattspinat mit Olivenöl', amountG: 120, kcal: 72, protein: 3.5, carbs: 2.0, fat: 5.5, fiber: 3.2 }
      ]
    },
    {
      id: 'meal_snack',
      type: 'snack',
      title: 'Snacks und Shakes',
      time: '16:30 Uhr',
      items: [
        { id: 'i10', name: 'Whey Protein Isolat mit Mandelmilch', amountG: 30, kcal: 145, protein: 28.0, carbs: 2.5, fat: 1.5, fiber: 0.5 },
        { id: 'i11', name: 'Frische Blaubeeren', amountG: 100, kcal: 57, protein: 0.7, carbs: 12.0, fat: 0.3, fiber: 2.4 }
      ]
    }
  ]);

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
      for (const item of m.items) sum += (item.fiber || 0);
    }
    return Math.round(sum);
  });

  // Micronutrients estimates
  let totalSugar = $derived(Math.round(totalCarbs * 0.18));
  let totalSaturatedFat = $derived(Math.round(totalFat * 0.28));
  let totalSodiumG = $derived((1.8).toFixed(1));
  let totalPotassiumG = $derived((3.2).toFixed(1));

  // ─── SEARCH & ADD FOOD MODAL STATE ───
  let activeMealForSearch = $state<MealSlotData | null>(null);
  let isSearchModalOpen = $state(false);

  function openSearchForMeal(meal: MealSlotData) {
    activeMealForSearch = meal;
    isSearchModalOpen = true;
  }

  function handleFoodSelected(item: LoggedFoodItem) {
    if (activeMealForSearch) {
      activeMealForSearch.items = [...activeMealForSearch.items, item];
      mealSlots = [...mealSlots];
    }
    isSearchModalOpen = false;
  }

  function removeItemFromMeal(mealType: string, itemId: string) {
    const meal = mealSlots.find(m => m.type === mealType);
    if (meal) {
      meal.items = meal.items.filter(i => i.id !== itemId);
      mealSlots = [...mealSlots];
    }
  }

  function copyPreviousDay() {
    alert('Mahlzeiten und Portionsgrößen vom gestrigen Tag erfolgreich übernommen!');
  }

  // ─── RECIPES STATE ───
  let recipesList = $state<RecipeData[]>([
    {
      id: 'r1',
      title: 'Hähnchen-Süßkartoffel Power Bowl',
      category: 'Hauptmahlzeit (Post-Workout)',
      prepTime: '20 Min',
      basePortions: 2,
      currentPortions: 2,
      rating: '4.9',
      kcalPerPortion: 540,
      proteinPerPortion: 52.0,
      carbsPerPortion: 62.0,
      fatPerPortion: 8.5,
      ingredients: [
        { name: 'Hähnchenbrustfilet (roh)', amount: 350, unit: 'g', kcal: 385, protein: 82.2, carbs: 0, fat: 5.2 },
        { name: 'Süßkartoffel', amount: 300, unit: 'g', kcal: 258, protein: 4.8, carbs: 60.3, fat: 0.3 },
        { name: 'Brokkoli', amount: 200, unit: 'g', kcal: 68, protein: 5.6, carbs: 8.0, fat: 0.8 },
        { name: 'Olivenöl extra vergine', amount: 10, unit: 'ml', kcal: 88, protein: 0, carbs: 0, fat: 10.0 }
      ],
      instructions: [
        'Süßkartoffeln schälen, in mundgerechte Würfel schneiden und in kochendem Salzwasser ca. 12 Minuten garen.',
        'Hähnchenbrustfilet in Streifen schneiden, mit Paprikapulver, Salz und Pfeffer würzen.',
        'In einer beschichteten Pfanne mit etwas Olivenöl von allen Seiten 6–8 Minuten scharf anbraten.',
        'Brokkoli-Röschen dazugeben, 4 Minuten dünsten und alles in zwei Bowls anrichten.'
      ]
    },
    {
      id: 'r2',
      title: 'High-Protein Blaubeer-Quark Schale',
      category: 'Frühstück (Low Fat)',
      prepTime: '5 Min',
      basePortions: 1,
      currentPortions: 1,
      rating: '4.8',
      kcalPerPortion: 380,
      proteinPerPortion: 55.4,
      carbsPerPortion: 23.8,
      fatPerPortion: 6.1,
      ingredients: [
        { name: 'Magerquark', amount: 250, unit: 'g', kcal: 170, protein: 31.2, carbs: 10.0, fat: 0.5 },
        { name: 'Whey Protein Isolat', amount: 25, unit: 'g', kcal: 94, protein: 21.5, carbs: 0.6, fat: 0.3 },
        { name: 'Frische Blaubeeren', amount: 100, unit: 'g', kcal: 57, protein: 0.7, carbs: 12.0, fat: 0.3 },
        { name: 'Mandelsplitter', amount: 10, unit: 'g', kcal: 59, protein: 2.1, carbs: 1.2, fat: 5.0 }
      ],
      instructions: [
        'Magerquark mit einem Schuss Mineralwasser und Whey Isolat cremig rühren.',
        'Blaubeeren waschen und auf der Quarkcreme anrichten.',
        'Mit gerösteten Mandelsplittern toppen.'
      ]
    },
    {
      id: 'r3',
      title: 'Wildlachs mit Süßkartoffel und Spargel',
      category: 'Abendessen (Omega-3)',
      prepTime: '25 Min',
      basePortions: 2,
      currentPortions: 2,
      rating: '5.0',
      kcalPerPortion: 620,
      proteinPerPortion: 42.0,
      carbsPerPortion: 45.0,
      fatPerPortion: 28.0,
      ingredients: [
        { name: 'Wildlachsfilet', amount: 320, unit: 'g', kcal: 570, protein: 64.0, carbs: 0, fat: 35.2 },
        { name: 'Süßkartoffeln', amount: 400, unit: 'g', kcal: 344, protein: 6.4, carbs: 80.4, fat: 0.4 },
        { name: 'Grüner Spargel', amount: 250, unit: 'g', kcal: 45, protein: 5.5, carbs: 4.8, fat: 0.5 }
      ],
      instructions: [
        'Süßkartoffeln würfeln und bei 200°C Umluft ca. 20 Minuten im Ofen backen.',
        'Wildlachsfilet auf der Hautseite in der Pfanne ca. 4 Minuten kross anbraten, wenden und kurz ruhen lassen.',
        'Grünen Spargel in der gleichen Pfanne 5 Minuten anbraten und zusammen anrichten.'
      ]
    }
  ]);

  let activeRecipeForModal = $state<RecipeData | null>(null);
  let isRecipeModalOpen = $state(false);
  let isRecipeEditorOpen = $state(false);

  function openRecipeModal(recipe: RecipeData) {
    activeRecipeForModal = recipe;
    isRecipeModalOpen = true;
  }

  function handleLogRecipe(mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack', item: LoggedFoodItem) {
    const meal = mealSlots.find(m => m.type === mealType);
    if (meal) {
      meal.items = [...meal.items, item];
      mealSlots = [...mealSlots];
    }
  }

  function handleSaveNewRecipe(recipe: RecipeData) {
    recipesList = [recipe, ...recipesList];
  }

  // ─── GLOBAL & CUSTOM FOOD ITEMS DATABASE ───
  let foodCatalog = $state<FoodItemData[]>([
    { id: 'f-1', name: 'Hähnchenbrustfilet (Bio)', category: 'Protein', source: 'USDA Core', servingSizeG: 100, kcalPer100g: 110, proteinPer100g: 23.5, carbsPer100g: 0.0, fatPer100g: 1.5, verified: true },
    { id: 'f-2', name: 'Basmatireis (roh)', category: 'Kohlenhydrate', source: 'System Seeded', servingSizeG: 100, kcalPer100g: 360, proteinPer100g: 8.5, carbsPer100g: 78.0, fatPer100g: 0.8, verified: true },
    { id: 'f-3', name: 'Magerquark 0.2%', category: 'Protein', source: 'OpenFoodFacts', servingSizeG: 250, kcalPer100g: 68, proteinPer100g: 12.5, carbsPer100g: 4.0, fatPer100g: 0.2, verified: true },
    { id: 'f-4', name: 'Whey Protein Isolat Vanille', category: 'Snacks und Shakes', source: 'Benutzerdefiniert', servingSizeG: 30, kcalPer100g: 380, proteinPer100g: 86.0, carbsPer100g: 2.0, fatPer100g: 1.0, verified: false },
    { id: 'f-5', name: 'Wildlachsfilet (MSC)', category: 'Protein', source: 'USDA Core', servingSizeG: 150, kcalPer100g: 178, proteinPer100g: 20.0, carbsPer100g: 0.0, fatPer100g: 11.0, verified: true },
    { id: 'f-6', name: 'Haferflocken zart', category: 'Kohlenhydrate', source: 'System Seeded', servingSizeG: 50, kcalPer100g: 372, proteinPer100g: 13.5, carbsPer100g: 58.7, fatPer100g: 7.0, fiberPer100g: 10.0, verified: true }
  ]);

  let isCreateFoodModalOpen = $state(false);
  let dbSearch = $state('');
  let dbCategory = $state('Alle');
  const catalogCategories = ['Alle', 'Protein', 'Kohlenhydrate', 'Fette', 'Gemüse und Obst', 'Snacks und Shakes'];

  let filteredCatalog = $derived(
    foodCatalog.filter(f => {
      const matchQuery = !dbSearch.trim() || f.name.toLowerCase().includes(dbSearch.toLowerCase());
      const matchCat = dbCategory === 'Alle' || f.category === dbCategory;
      return matchQuery && matchCat;
    })
  );

  function handleSaveCustomFood(food: FoodItemData) {
    foodCatalog = [food, ...foodCatalog];
  }
</script>

<div class="space-y-6">
  
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Ernährung und Makronährstoffe</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Tagesziel: 2.400 kcal &bull; 180g Protein (2.2 g/kg) &bull; Präzises Mahlzeitentagebuch
      </p>
    </div>
    <div class="flex items-center gap-2 flex-wrap">
      <button
        type="button"
        onclick={() => isCreateFoodModalOpen = true}
        class="px-3.5 py-2 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold hover:bg-[var(--bg-surface-100)] transition-all cursor-pointer shadow-xs flex items-center gap-1.5"
      >
        <span>+ Lebensmittel</span>
      </button>

      <button
        type="button"
        onclick={() => isRecipeEditorOpen = true}
        class="px-3.5 py-2 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold hover:bg-[var(--bg-surface-100)] transition-all cursor-pointer shadow-xs flex items-center gap-1.5"
      >
        <span>+ Rezept erstellen</span>
      </button>

      <button
        type="button"
        onclick={onopenbarcode}
        class="px-4 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md flex items-center gap-1.5"
      >
        <span>Barcode scannen</span>
      </button>
    </div>
  </div>

  <!-- Sub-Navigation Tabs -->
  <div class="flex gap-2 bg-[var(--bg-surface-50)] p-1.5 rounded-2xl border border-[var(--border-subtle)] overflow-x-auto no-scrollbar">
    <button
      type="button"
      onclick={() => setTab('diary')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'diary' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="food" class="text-[var(--color-activity)]" />
      <span>Tagebuch</span>
      <Badge variant="activity" class="text-[0.625rem] tabular-nums">{totalCalories} kcal</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('recipes')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'recipes' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="sun" class="text-[var(--color-circadian)]" />
      <span>Rezeptdatenbank</span>
      <Badge variant="default" class="text-[0.625rem]">{recipesList.length}</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('database')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'database' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
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
      <div class="flex items-center justify-between flex-wrap gap-2 px-1">
        <h2 class="text-base font-extrabold text-[var(--text-main)]">Mahlzeitenfenster</h2>
        <div class="flex items-center gap-2">
          <button
            type="button"
            onclick={copyPreviousDay}
            class="px-3 py-1.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--text-main)] hover:bg-[var(--bg-surface-50)] transition-all cursor-pointer shadow-xs"
          >
            Vortag kopieren
          </button>
        </div>
      </div>

      <!-- 4 Meal Slots Schedule -->
      <div class="space-y-4">
        {#each mealSlots as meal}
          {@const mealKcal = meal.items.reduce((sum, i) => sum + i.kcal, 0)}
          {@const mealProtein = Math.round(meal.items.reduce((sum, i) => sum + i.protein, 0))}
          {@const mealCarbs = Math.round(meal.items.reduce((sum, i) => sum + i.carbs, 0))}
          {@const mealFat = Math.round(meal.items.reduce((sum, i) => sum + i.fat, 0))}

          <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-3">
            
            <!-- Meal Header -->
            <div class="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-[var(--border-subtle)]/60">
              <div class="flex items-center gap-2.5">
                <div class="w-2.5 h-2.5 rounded-full bg-[var(--color-activity)]"></div>
                <div>
                  <h3 class="text-sm sm:text-base font-extrabold text-[var(--text-main)]">{meal.title}</h3>
                  <span class="text-xs text-[var(--text-muted)]">{meal.time}</span>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <div class="text-right">
                  <span class="text-xs font-bold text-[var(--color-activity)] tabular-nums">{mealKcal} kcal</span>
                  <span class="text-[0.6875rem] text-[var(--text-muted)] block tabular-nums">{mealProtein}g P &bull; {mealCarbs}g C &bull; {mealFat}g F</span>
                </div>

                <button
                  type="button"
                  onclick={() => openSearchForMeal(meal)}
                  class="px-3 py-1.5 rounded-xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs flex items-center gap-1"
                >
                  <span>+ Hinzufügen</span>
                </button>
              </div>
            </div>

            <!-- Items Table in this Meal -->
            <div class="space-y-1.5">
              {#each meal.items as item}
                <div class="p-2.5 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]/70 flex items-center justify-between gap-2 hover:border-[var(--border-strong)] transition-all">
                  <div class="overflow-hidden">
                    <span class="font-bold text-xs text-[var(--text-main)] block truncate">{item.name}</span>
                    <span class="text-[0.6875rem] text-[var(--text-muted)] tabular-nums">
                      {item.amountG}g &bull; {item.protein}g Protein &bull; {item.carbs}g Carbs &bull; {item.fat}g Fett
                    </span>
                  </div>

                  <div class="flex items-center gap-2.5 shrink-0">
                    <span class="text-xs font-bold text-[var(--text-main)] tabular-nums">{item.kcal} kcal</span>
                    <button
                      type="button"
                      onclick={() => removeItemFromMeal(meal.type, item.id)}
                      class="text-xs font-bold text-[var(--text-muted)] hover:text-rose-500 cursor-pointer p-1"
                      title="Eintrag entfernen"
                    >
                      &times;
                    </button>
                  </div>
                </div>
              {/each}
            </div>

          </div>
        {/each}
      </div>

      <!-- Advanced Micronutrient Analysis Card -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
        <div>
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">Mikronährstoffe und Elektrolyt-Verteilung</h3>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">Detaillierte Nährwertbilanz für die heutige Ernährung</p>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center text-xs">
          <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
            <span class="text-[0.625rem] text-[var(--text-muted)] uppercase font-bold block">Ballaststoffe</span>
            <span class="font-extrabold text-sm text-[var(--text-main)] tabular-nums">{totalFiber} g</span>
            <span class="text-[0.5625rem] text-emerald-500 font-bold block mt-0.5">Ziel: 38g (84%)</span>
          </div>

          <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
            <span class="text-[0.625rem] text-[var(--text-muted)] uppercase font-bold block">davon Zucker</span>
            <span class="font-extrabold text-sm text-[var(--text-main)] tabular-nums">{totalSugar} g</span>
            <span class="text-[0.5625rem] text-emerald-500 font-bold block mt-0.5">&lt; 45g Limit</span>
          </div>

          <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
            <span class="text-[0.625rem] text-[var(--text-muted)] uppercase font-bold block">Gesätt. Fette</span>
            <span class="font-extrabold text-sm text-[var(--text-main)] tabular-nums">{totalSaturatedFat} g</span>
            <span class="text-[0.5625rem] text-emerald-500 font-bold block mt-0.5">&lt; 20g Limit</span>
          </div>

          <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
            <span class="text-[0.625rem] text-[var(--text-muted)] uppercase font-bold block">Natrium</span>
            <span class="font-extrabold text-sm text-[var(--text-main)] tabular-nums">{totalSodiumG} g</span>
            <span class="text-[0.5625rem] text-emerald-500 font-bold block mt-0.5">Optimal</span>
          </div>

          <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl col-span-2 sm:col-span-1">
            <span class="text-[0.625rem] text-[var(--text-muted)] uppercase font-bold block">Kalium</span>
            <span class="font-extrabold text-sm text-[var(--text-main)] tabular-nums">{totalPotassiumG} g</span>
            <span class="text-[0.5625rem] text-emerald-500 font-bold block mt-0.5">80% Tagesbedarf</span>
          </div>
        </div>
      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 2: REZEPTDATENBANK & SKALIERER                          -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'recipes'}
    <div class="space-y-5">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h2 class="text-base font-extrabold text-[var(--text-main)]">Deine Rezept-Bibliothek</h2>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">Skalierbare Rezepte mit dynamischer Nährwert- und Zutatenberechnung</p>
        </div>
        <button
          type="button"
          onclick={() => isRecipeEditorOpen = true}
          class="px-4 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs"
        >
          + Neues Rezept anlegen
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        {#each recipesList as recipe}
          <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4 hover:border-[var(--border-strong)] transition-all">
            <div class="flex items-start justify-between gap-3">
              <div>
                <Badge variant="primary" class="text-[0.625rem] mb-1.5">{recipe.category}</Badge>
                <h3 class="text-base font-extrabold text-[var(--text-main)] leading-snug">{recipe.title}</h3>
                <span class="text-xs text-[var(--text-muted)] mt-0.5 block">Zubereitungszeit: {recipe.prepTime} &bull; Basis: {recipe.basePortions} Portionen</span>
              </div>
            </div>

            <!-- Macros pill grid -->
            <div class="grid grid-cols-4 gap-2 text-center text-xs">
              <div class="p-2 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
                <span class="text-[0.625rem] text-[var(--text-muted)] block">Kcal / Port.</span>
                <span class="font-extrabold text-sm text-[var(--color-activity)] tabular-nums">{recipe.kcalPerPortion}</span>
              </div>
              <div class="p-2 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
                <span class="text-[0.625rem] text-[var(--text-muted)] block">Protein</span>
                <span class="font-extrabold text-sm text-emerald-500 tabular-nums">{recipe.proteinPerPortion}g</span>
              </div>
              <div class="p-2 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
                <span class="text-[0.625rem] text-[var(--text-muted)] block">Carbs</span>
                <span class="font-extrabold text-sm text-amber-500 tabular-nums">{recipe.carbsPerPortion}g</span>
              </div>
              <div class="p-2 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
                <span class="text-[0.625rem] text-[var(--text-muted)] block">Fett</span>
                <span class="font-extrabold text-sm text-purple-500 tabular-nums">{recipe.fatPerPortion}g</span>
              </div>
            </div>

            <!-- Open Recipe Scaler & Cook Modal -->
            <div class="flex gap-2 pt-1">
              <button
                type="button"
                onclick={() => openRecipeModal(recipe)}
                class="flex-1 py-2.5 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs text-center"
              >
                Rezept öffnen & kochen
              </button>
            </div>
          </div>
        {/each}
      </div>
    </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 3: LEBENSMITTELKATALOG                                  -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'database'}
    <div class="space-y-5">
      
      <!-- Catalog Controls -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Lebensmittel- und Nährwert-Katalog</h2>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">Durchsuche globale und eigens erfasste Lebensmittel</p>
          </div>
          <button
            type="button"
            onclick={() => isCreateFoodModalOpen = true}
            class="px-4 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs"
          >
            + Eigenes Lebensmittel anlegen
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="sm:col-span-2">
            <input
              type="text"
              bind:value={dbSearch}
              placeholder="Lebensmittel suchen (z.B. Hähnchen, Skyr, Reis)..."
              class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-2.5 text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)] font-semibold"
            />
          </div>
          <div>
            <select
              bind:value={dbCategory}
              class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-2.5 text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)] cursor-pointer"
            >
              {#each catalogCategories as cat}
                <option value={cat}>{cat}</option>
              {/each}
            </select>
          </div>
        </div>
      </div>

      <!-- Food Items Table -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs">
        <div class="w-full overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.625rem]">
                <th class="py-2.5 px-3">Lebensmittel</th>
                <th class="py-2.5 px-3">Kategorie</th>
                <th class="py-2.5 px-3">Quelle</th>
                <th class="py-2.5 px-3">Kcal / 100g</th>
                <th class="py-2.5 px-3">Protein</th>
                <th class="py-2.5 px-3">Carbs</th>
                <th class="py-2.5 px-3">Fett</th>
                <th class="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]">
              {#each filteredCatalog as f}
                <tr class="hover:bg-[var(--bg-surface-50)] transition-colors">
                  <td class="py-3 px-3 font-bold text-[var(--text-main)]">{f.name}</td>
                  <td class="py-3 px-3 text-[var(--text-muted)]">{f.category}</td>
                  <td class="py-3 px-3 text-[var(--text-soft)]">{f.source}</td>
                  <td class="py-3 px-3 font-extrabold text-[var(--color-activity)] tabular-nums">{f.kcalPer100g} kcal</td>
                  <td class="py-3 px-3 font-bold text-emerald-500 tabular-nums">{f.proteinPer100g}g</td>
                  <td class="py-3 px-3 font-bold text-amber-500 tabular-nums">{f.carbsPer100g}g</td>
                  <td class="py-3 px-3 font-bold text-purple-500 tabular-nums">{f.fatPer100g}g</td>
                  <td class="py-3 px-3 text-right">
                    <Badge variant={f.verified ? 'success' : 'default'} class="text-[0.5625rem]">
                      {f.verified ? 'Verifiziert' : 'Eigener Eintrag'}
                    </Badge>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  {/if}

</div>

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- MODALS                                                      -->
<!-- ═══════════════════════════════════════════════════════════ -->
<FoodSearchModal
  open={isSearchModalOpen}
  targetMeal={activeMealForSearch}
  onclose={() => isSearchModalOpen = false}
  onselect={handleFoodSelected}
  {onopenbarcode}
/>

<RecipeDetailModal
  open={isRecipeModalOpen}
  recipe={activeRecipeForModal}
  onclose={() => isRecipeModalOpen = false}
  onlog={handleLogRecipe}
/>

<RecipeEditorModal
  open={isRecipeEditorOpen}
  availableFoods={foodCatalog}
  onclose={() => isRecipeEditorOpen = false}
  onsave={handleSaveNewRecipe}
/>

<CreateFoodItemModal
  open={isCreateFoodModalOpen}
  onclose={() => isCreateFoodModalOpen = false}
  onsave={handleSaveCustomFood}
  {onopenbarcode}
/>
