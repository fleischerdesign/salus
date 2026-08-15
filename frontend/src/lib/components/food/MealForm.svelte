<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import SegmentedControl from '$components/ui/SegmentedControl.svelte';
  import MealItemRow from './MealItemRow.svelte';
  import BarcodeScanner from './BarcodeScanner.svelte';
  import BarcodeNotFound from './BarcodeNotFound.svelte';
  import PortionPickerModal from './PortionPickerModal.svelte';
  import FoodFormModal from './FoodFormModal.svelte';
  import CookModal from './CookModal.svelte';
  import { lookupBarcode } from '$lib/food/barcode';
  import { loadFrequentFoods, newestFood } from '$lib/food/frequent';
  import { composeRecipe } from '$lib/mutations/recipe';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import type { FoodItem, Meal, MealItem, Recipe } from '$lib/db/types';

  interface FoodSelection {
    foodItemId: string;
    servings: number;
    name: string;
    servingSize: number;
    servingUnit: string;
    calories: number;
    proteinG: number;
    carbsG: number;
    fatG: number;
  }

  interface Props {
    open: boolean;
    foodItems: FoodItem[];
    initialMealType?: string;
    initialFoodId?: string | null;
    initialServings?: number;
    meal?: Meal | null;
    mealItems?: MealItem[];
    onSave: (data: {
      id?: string;
      meal_type: string;
      name: string;
      notes: string;
      items: { food_item_id: string; servings: number }[];
    }) => void;
    onClose: () => void;
    saving?: boolean;
  }

  let {
    open,
    foodItems,
    initialMealType = 'snack',
    initialFoodId = null,
    initialServings = 1,
    meal = null,
    mealItems = [],
    onSave,
    onClose,
    saving = false
  }: Props = $props();

  const mealTypeOptions = [
    { value: 'breakfast', label: 'Breakfast', icon: 'wb-sunny' },
    { value: 'lunch', label: 'Lunch', icon: 'lunch-dining' },
    { value: 'dinner', label: 'Dinner', icon: 'dinner-dining' },
    { value: 'snack', label: 'Snack', icon: 'cookie' },
    { value: 'other', label: 'Other', icon: 'restaurant' }
  ];

  const recipesQuery = useQuery(() => db.notDeleted(db.recipe).toArray());
  const recipes = $derived(recipesQuery.value ?? ([] as Recipe[]));

  let mealType = $state('snack');
  let name = $state('');
  let notes = $state('');
  let search = $state('');
  let showDetails = $state(false);
  let selections = $state<FoodSelection[]>([]);
  let frequent = $state<FoodItem[]>([]);
  let pickerFood = $state<FoodItem | null>(null);
  let notFoundBarcode = $state<string | null>(null);
  let createBarcode = $state<string | null>(null);
  let createOpen = $state(false);
  let cookTarget = $state<Recipe | null>(null);
  let cookOpen = $state(false);
  let searchEl = $state<HTMLInputElement | null>(null);
  let createInitDone = false;

  function reset() {
    mealType = 'snack';
    name = '';
    notes = '';
    search = '';
    showDetails = false;
    selections = [];
    pickerFood = null;
    notFoundBarcode = null;
    createBarcode = null;
    createOpen = false;
    cookTarget = null;
    cookOpen = false;
    createInitDone = false;
  }

  function loadMealForEdit(target: Meal, targetItems: MealItem[]) {
    mealType = target.meal_type;
    name = target.name ?? '';
    notes = target.notes ?? '';
    showDetails = Boolean(target.name || target.notes);
    selections = targetItems
      .filter((mi) => !mi.deleted_at)
      .map((mi) => toSelection(mi.food_item_id, mi.servings));
  }

  function toSelection(foodItemId: string, servings: number): FoodSelection {
    const food = foodItems.find((f) => f.id === foodItemId && !f.deleted_at);
    return {
      foodItemId,
      servings,
      name: food?.name ?? 'Unknown',
      servingSize: food?.serving_size ?? 1,
      servingUnit: food?.serving_unit ?? 'g',
      calories: food?.calories_per_serving ?? 0,
      proteinG: food?.protein_g ?? 0,
      carbsG: food?.carbs_g ?? 0,
      fatG: food?.fat_g ?? 0
    };
  }

  $effect(() => {
    if (!open) reset();
  });

  $effect(() => {
    if (!open) return;
    searchEl?.focus();
    if (meal) {
      loadMealForEdit(meal, mealItems);
      return;
    }
    if (!createInitDone) {
      mealType = initialMealType;
      const food = initialFoodId
        ? foodItems.find((f) => f.id === initialFoodId && !f.deleted_at)
        : undefined;
      if (food) addItem(food, initialServings);
      createInitDone = true;
    }
  });

  $effect(() => {
    if (!open) return;
    loadFrequentFoods().then((foods) => (frequent = foods));
  });

  const filteredItems = $derived(
    search.trim()
      ? foodItems.filter(
          (f) => f.name.toLowerCase().includes(search.toLowerCase()) && !f.deleted_at
        )
      : []
  );
  const filteredRecipes = $derived(
    search.trim() ? recipes.filter((r) => r.name.toLowerCase().includes(search.toLowerCase())) : []
  );

  const showSearch = $derived(search.trim().length > 0);
  const noResults = $derived(
    showSearch && filteredItems.length === 0 && filteredRecipes.length === 0
  );

  const totalCalories = $derived(selections.reduce((sum, s) => sum + s.calories * s.servings, 0));
  const totalProtein = $derived(selections.reduce((sum, s) => sum + s.proteinG * s.servings, 0));
  const totalCarbs = $derived(selections.reduce((sum, s) => sum + s.carbsG * s.servings, 0));
  const totalFat = $derived(selections.reduce((sum, s) => sum + s.fatG * s.servings, 0));

  const mealTypeLabel = $derived(
    mealTypeOptions.find((o) => o.value === mealType)?.label ?? mealType
  );

  function addItem(food: FoodItem, servings = 1) {
    const existing = selections.find((s) => s.foodItemId === food.id);
    if (existing) {
      existing.servings += servings;
      selections = [...selections];
    } else {
      selections = [...selections, toSelection(food.id ?? '', servings)];
    }
    search = '';
  }

  function addRecipeItems(items: { food_item_id: string; servings: number; amount_g: number }[]) {
    selections = items.map((i) => toSelection(i.food_item_id, i.servings));
  }

  function incrementItem(foodItemId: string) {
    const s = selections.find((s) => s.foodItemId === foodItemId);
    if (s) {
      s.servings = Math.round((s.servings + 0.5) * 2) / 2;
      selections = [...selections];
    }
  }

  function decrementItem(foodItemId: string) {
    const s = selections.find((s) => s.foodItemId === foodItemId);
    if (s) {
      s.servings = Math.max(0.25, Math.round((s.servings - 0.5) * 2) / 2);
      selections = [...selections];
    }
  }

  function removeItem(foodItemId: string) {
    selections = selections.filter((s) => s.foodItemId !== foodItemId);
  }

  const canSave = $derived(selections.length > 0);

  function handleSubmit() {
    if (!canSave) return;
    onSave({
      ...(meal?.id ? { id: meal.id } : {}),
      meal_type: mealType,
      name: name.trim() || '',
      notes: notes.trim() || '',
      items: selections.map((s) => ({
        food_item_id: s.foodItemId,
        servings: s.servings
      }))
    });
  }

  function openCook(recipe: Recipe) {
    cookTarget = recipe;
    cookOpen = true;
  }

  async function handleCook(servings: number) {
    if (!cookTarget) return;
    const composed = await composeRecipe(cookTarget.id ?? '', servings);
    if (composed && composed.items.length > 0) {
      name = `Recipe: ${composed.name}`;
      showDetails = true;
      addRecipeItems(composed.items);
    }
    cookOpen = false;
    cookTarget = null;
    search = '';
  }

  async function handleScan(code: string) {
    notFoundBarcode = null;
    try {
      const found = await lookupBarcode(code);
      if (found) {
        pickerFood = found;
      } else {
        notFoundBarcode = code;
      }
    } catch {
      notFoundBarcode = code;
    }
  }

  function openCreateFromScan() {
    createBarcode = notFoundBarcode;
    notFoundBarcode = null;
    createOpen = true;
  }

  function handlePicked(food: FoodItem, servings: number) {
    addItem(food, servings);
    pickerFood = null;
  }

  function handleCreated() {
    newestFood().then((created) => {
      if (created) pickerFood = created;
    });
    createBarcode = null;
  }
</script>

<Modal {open} onclose={onClose} title={meal ? 'Edit Meal' : 'Log Food'} size="lg">
  <div class="flex flex-col gap-4">
    <SegmentedControl options={mealTypeOptions} bind:value={mealType} class="w-full" />

    <div class="relative">
      <span
        class="pointer-events-none absolute inset-y-0 left-3 z-10 flex items-center text-surface-400"
      >
        <Icon name="search" size="sm" />
      </span>
      <div class="pl-9">
        <Input
          name="food_search"
          placeholder="Search foods or recipes…"
          bind:value={search}
          bind:el={searchEl}
        />
      </div>
    </div>

    {#if showSearch}
      <div class="max-h-56 space-y-2 overflow-y-auto rounded-lg border border-surface-200 p-1">
        {#if filteredItems.length > 0}
          <p
            class="px-2 pt-1.5 text-[10px] font-semibold tracking-wider text-surface-400 uppercase"
          >
            Foods
          </p>
          {#each filteredItems.slice(0, 8) as food (food.id)}
            <button
              onclick={() => (pickerFood = food)}
              class="flex w-full items-center justify-between rounded-md px-2 py-2 text-left hover:bg-surface-50"
            >
              <div class="min-w-0">
                <div class="truncate text-sm font-medium text-surface-800">{food.name}</div>
                <div class="text-xs text-surface-400">
                  {Math.round(food.calories_per_serving)} kcal · {Math.round(food.protein_g)}P ·{' '}
                  {Math.round(food.carbs_g)}C · {Math.round(food.fat_g)}F
                </div>
              </div>
              <Icon name="add-circle" size="sm" class="shrink-0 text-primary-500" />
            </button>
          {/each}
        {/if}

        {#if filteredRecipes.length > 0}
          <p
            class="px-2 pt-1.5 text-[10px] font-semibold tracking-wider text-surface-400 uppercase"
          >
            Recipes
          </p>
          {#each filteredRecipes.slice(0, 6) as recipe (recipe.id)}
            <button
              onclick={() => openCook(recipe)}
              class="flex w-full items-center justify-between rounded-md px-2 py-2 text-left hover:bg-surface-50"
            >
              <div class="min-w-0">
                <div class="truncate text-sm font-medium text-surface-800">{recipe.name}</div>
                <div class="text-xs text-surface-400">
                  {recipe.servings} serving{recipe.servings !== 1 ? 's' : ''}
                </div>
              </div>
              <Icon name="menu-book" size="sm" class="shrink-0 text-warning-600" />
            </button>
          {/each}
        {/if}
      </div>
    {:else if noResults}
      <div
        class="flex flex-col items-center gap-3 rounded-lg border border-dashed border-surface-300 py-5 text-center"
      >
        <p class="text-sm font-medium text-surface-700">No "{search}" in the database</p>
        <Btn variant="secondary" size="sm" onclick={() => (createOpen = true)}>
          <Icon name="add" size="sm" />
          Create food
        </Btn>
      </div>
    {/if}

    {#if notFoundBarcode}
      <BarcodeNotFound
        barcode={notFoundBarcode}
        onCreate={openCreateFromScan}
        onDismiss={() => (notFoundBarcode = null)}
      />
    {/if}

    <div class="flex flex-wrap items-center gap-2">
      <BarcodeScanner onScan={handleScan} variant="secondary" label="Scan" />
      {#if frequent.length > 0 && !search.trim()}
        <div class="flex flex-1 flex-wrap items-center gap-2">
          {#each frequent as food (food.id)}
            <button
              type="button"
              onclick={() => (pickerFood = food)}
              class="inline-flex items-center gap-1 rounded-full border border-surface-200 bg-surface-50 px-2.5 py-1 text-xs font-medium text-surface-700 transition-colors hover:border-primary-300 hover:bg-primary-50 hover:text-primary-700"
            >
              <Icon name="add" size="sm" />
              {food.name}
            </button>
          {/each}
        </div>
      {/if}
    </div>

    {#if selections.length > 0}
      <div class="rounded-lg border border-surface-200 p-3">
        <div class="mb-2 flex items-center justify-between">
          <h3 class="text-xs font-semibold tracking-wider text-surface-400 uppercase">Items</h3>
          <button
            type="button"
            onclick={() => (showDetails = !showDetails)}
            class="flex items-center gap-1 text-xs font-medium text-surface-500 hover:text-surface-700"
          >
            {showDetails ? 'Hide' : 'Show'} details
            <Icon name={showDetails ? 'keyboard-arrow-up' : 'expand-more'} size="sm" />
          </button>
        </div>
        <div class="flex flex-col gap-2">
          {#each selections as sel (sel.foodItemId)}
            <MealItemRow
              name={sel.name}
              servings={sel.servings}
              servingSize={sel.servingSize}
              servingUnit={sel.servingUnit}
              calories={sel.calories}
              proteinG={sel.proteinG}
              carbsG={sel.carbsG}
              fatG={sel.fatG}
              onRemove={() => removeItem(sel.foodItemId)}
              onIncrement={() => incrementItem(sel.foodItemId)}
              onDecrement={() => decrementItem(sel.foodItemId)}
            />
          {/each}
        </div>

        {#if showDetails}
          <div class="mt-3 space-y-3 border-t border-surface-100 pt-3">
            <Input
              name="meal_name"
              label="Name (optional — groups items into a meal)"
              placeholder="e.g. Porridge with banana"
              bind:value={name}
            />
            <Input
              name="notes"
              label="Notes (optional)"
              placeholder="Optional notes…"
              bind:value={notes}
            />
          </div>
        {/if}
      </div>
    {/if}

    {#if selections.length > 0}
      <div
        class="sticky bottom-0 flex items-center justify-between rounded-lg border border-surface-200 bg-surface-0 px-4 py-3 shadow-md"
      >
        <div class="text-xs">
          <div class="text-lg font-bold text-surface-900 tabular-nums">
            {Math.round(totalCalories).toLocaleString()} kcal
          </div>
          <div class="text-surface-400">
            {Math.round(totalProtein)}P · {Math.round(totalCarbs)}C · {Math.round(totalFat)}F
          </div>
        </div>
        <Btn variant="primary" onclick={handleSubmit} disabled={!canSave || saving}>
          {saving ? 'Saving…' : meal ? 'Save Meal' : `Add to ${mealTypeLabel}`}
        </Btn>
      </div>
    {:else}
      <div class="flex justify-end gap-3 pt-2">
        <Btn variant="ghost" onclick={onClose}>Cancel</Btn>
        <Btn variant="primary" onclick={handleSubmit} disabled={!canSave || saving}>
          {saving ? 'Saving…' : meal ? 'Save Meal' : 'Log Food'}
        </Btn>
      </div>
    {/if}
  </div>

  <PortionPickerModal food={pickerFood} onAdd={handlePicked} onClose={() => (pickerFood = null)} />

  <CookModal
    open={cookOpen}
    recipeName={cookTarget?.name ?? ''}
    recipeServings={cookTarget?.servings ?? 1}
    macros={null}
    onCook={handleCook}
    onClose={() => {
      cookOpen = false;
      cookTarget = null;
    }}
  />

  <FoodFormModal
    open={createOpen}
    food={null}
    initialBarcode={createBarcode}
    onClose={() => {
      createOpen = false;
      createBarcode = null;
    }}
    onSaved={handleCreated}
  />
</Modal>
