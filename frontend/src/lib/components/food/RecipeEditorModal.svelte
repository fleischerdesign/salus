<script lang="ts">
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Modal from '../ui/Modal.svelte';
  import type { RecipeData, FoodItemData } from '../../types/nutrition';

  let {
    open = false,
    availableFoods = [],
    onclose,
    onsave
  } = $props<{
    open: boolean;
    availableFoods: FoodItemData[];
    onclose: () => void;
    onsave: (recipe: RecipeData) => void;
  }>();

  let title = $state('');
  let category = $state('Hauptmahlzeit');
  let prepTime = $state('20 Min');
  let portions = $state(2);

  const categoryOptions = [
    { value: 'Frühstück (High Protein)', label: 'Frühstück (High Protein)' },
    { value: 'Hauptmahlzeit (Post-Workout)', label: 'Hauptmahlzeit (Post-Workout)' },
    { value: 'Abendessen (Low Carb)', label: 'Abendessen (Low Carb)' },
    { value: 'Snacks & Desserts', label: 'Snacks & Desserts' }
  ];

  interface RecipeDraftIngredient {
    id: string;
    foodId: string;
    name: string;
    amount: number;
    unit: string;
    kcal: number;
    protein: number;
    carbs: number;
    fat: number;
  }

  let selectedIngredients = $state<RecipeDraftIngredient[]>([
    {
      id: 'ing_1',
      foodId: 'f_chicken',
      name: 'Hähnchenbrustfilet (roh)',
      amount: 300,
      unit: 'g',
      kcal: 330,
      protein: 69.0,
      carbs: 0.0,
      fat: 4.5
    },
    {
      id: 'ing_2',
      foodId: 'f_rice',
      name: 'Basmatireis (roh)',
      amount: 150,
      unit: 'g',
      kcal: 540,
      protein: 12.8,
      carbs: 117.0,
      fat: 1.2
    }
  ]);

  let instructions = $state<string[]>([
    'Reis mit doppelter Menge Wasser und etwas Salz 15 Minuten köcheln lassen.',
    'Hähnchenbrustfilet in Streifen schneiden und in der Pfanne goldbraun anbraten.'
  ]);
  let newStepText = $state('');

  // Search in modal to add ingredient
  let searchFoodQuery = $state('');
  let isAddingIngredient = $state(false);

  let filteredFoods = $derived(
    searchFoodQuery.trim()
      ? availableFoods
          .filter((f: FoodItemData) => f.name.toLowerCase().includes(searchFoodQuery.toLowerCase()))
          .slice(0, 5)
      : availableFoods.slice(0, 5)
  );

  function addFoodToRecipe(food: FoodItemData) {
    const defaultAmount = food.servingSizeG || 100;
    const factor = defaultAmount / 100;
    selectedIngredients.push({
      id: `ing_${Date.now()}_${Math.random().toString(36).slice(2, 5)}`,
      foodId: food.id,
      name: food.name,
      amount: defaultAmount,
      unit: 'g',
      kcal: Math.round((food.per100g?.kcal || 0) * factor),
      protein: Number(((food.per100g?.protein || 0) * factor).toFixed(1)),
      carbs: Number(((food.per100g?.carbs || 0) * factor).toFixed(1)),
      fat: Number(((food.per100g?.fat || 0) * factor).toFixed(1))
    });
    isAddingIngredient = false;
    searchFoodQuery = '';
  }

  function updateIngredientAmount(idx: number, newAmount: number) {
    const ing = selectedIngredients[idx];
    if (!ing) return;
    const food = availableFoods.find((f: FoodItemData) => f.id === ing.foodId);
    ing.amount = newAmount;
    if (food) {
      ing.kcal = Math.round((food.per100g?.kcal || 0) * (newAmount / 100));
      ing.protein = Number(((food.per100g?.protein || 0) * (newAmount / 100)).toFixed(1));
      ing.carbs = Number(((food.per100g?.carbs || 0) * (newAmount / 100)).toFixed(1));
      ing.fat = Number(((food.per100g?.fat || 0) * (newAmount / 100)).toFixed(1));
    }
    selectedIngredients = [...selectedIngredients];
  }

  function removeIngredient(idx: number) {
    selectedIngredients = selectedIngredients.filter((_, i) => i !== idx);
  }

  function addStep() {
    if (!newStepText.trim()) return;
    instructions.push(newStepText.trim());
    newStepText = '';
  }

  function removeStep(idx: number) {
    instructions = instructions.filter((_, i) => i !== idx);
  }

  // Aggregate Total & Per Portion Macros
  let totalKcal = $derived(selectedIngredients.reduce((s, i) => s + i.kcal, 0));
  let totalProtein = $derived(selectedIngredients.reduce((s, i) => s + i.protein, 0));
  let totalCarbs = $derived(selectedIngredients.reduce((s, i) => s + i.carbs, 0));
  let totalFat = $derived(selectedIngredients.reduce((s, i) => s + i.fat, 0));

  let portionKcal = $derived(Math.round(totalKcal / Math.max(1, portions)));
  let portionProtein = $derived((totalProtein / Math.max(1, portions)).toFixed(1));
  let portionCarbs = $derived((totalCarbs / Math.max(1, portions)).toFixed(1));
  let portionFat = $derived((totalFat / Math.max(1, portions)).toFixed(1));

  function handleSaveRecipe() {
    if (!title.trim() || selectedIngredients.length === 0) return;
    const newRecipe: RecipeData = {
      id: `recipe_${Date.now()}`,
      title: title.trim(),
      category,
      prepTime,
      basePortions: portions,
      currentPortions: portions,
      rating: '5.0',
      kcalPerPortion: portionKcal,
      proteinPerPortion: Number(portionProtein),
      carbsPerPortion: Number(portionCarbs),
      fatPerPortion: Number(portionFat),
      ingredients: selectedIngredients.map((i) => ({
        name: i.name,
        amount: i.amount,
        unit: i.unit,
        kcal: i.kcal,
        protein: i.protein,
        carbs: i.carbs,
        fat: i.fat
      })),
      instructions:
        instructions.length > 0 ? instructions : ['Alle Zutaten wie gewünscht zubereiten.']
    };
    onsave(newRecipe);
    onclose();
  }
</script>

<Modal
  {open}
  title="Neues Rezept erstellen"
  subtitle="Definiere Zutaten, Portionen und Zubereitungsschritte"
  icon="menu_book"
  size="lg"
  {onclose}
>
  <div class="space-y-4 text-xs">
    <!-- Title & Category -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <!-- Basic Recipe Info -->
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div class="sm:col-span-2">
          <Input
            label="Rezepttitel *"
            bind:value={title}
            placeholder="z.B. Hähnchen-Reis Bowl mit Brokkoli"
          />
        </div>
        <div>
          <Input label="Portionen" type="number" bind:value={portions} />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Select label="Kategorie" bind:value={category} options={categoryOptions} />
        <Input label="Zubereitungszeit" bind:value={prepTime} placeholder="z.B. 25 Min" />
      </div>

      <!-- Ingredients Section -->
      <div class="space-y-2 pt-1">
        <div class="flex items-center justify-between">
          <span class="font-bold text-text-main"
            >Enthaltene Zutaten ({selectedIngredients.length})</span
          >
          <button
            type="button"
            onclick={() => (isAddingIngredient = !isAddingIngredient)}
            class="cursor-pointer rounded-xl bg-primary/10 px-3 py-1 font-bold text-primary transition-all hover:bg-primary/20"
          >
            + Zutat hinzufügen
          </button>
        </div>

        <!-- Add Ingredient Dropdown / Search -->
        {#if isAddingIngredient}
          <div
            class="animate-[fadeIn_0.15s_ease-out] space-y-2 rounded-2xl border border-border-subtle bg-surface-50 p-3"
          >
            <Input
              icon="search"
              bind:value={searchFoodQuery}
              placeholder="Lebensmittel aus Katalog suchen..."
            />
            <div class="max-h-36 divide-y divide-border-subtle overflow-y-auto">
              {#each filteredFoods as f}
                <div class="flex items-center justify-between gap-2 py-2">
                  <div>
                    <span class="block font-bold text-text-main">{f.name}</span>
                    <span class="text-[0.625rem] text-text-muted tabular-nums"
                      >{f.kcalPer100g} kcal/100g &bull; {f.proteinPer100g}g P</span
                    >
                  </div>
                  <button
                    type="button"
                    onclick={() => addFoodToRecipe(f)}
                    class="cursor-pointer rounded-lg bg-primary px-2.5 py-1 text-[0.6875rem] font-bold text-white hover:opacity-90"
                  >
                    Hinzufügen
                  </button>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Ingredients List -->
        <div class="space-y-2">
          {#each selectedIngredients as ing, idx}
            <div
              class="flex items-center justify-between gap-3 rounded-2xl border border-border-subtle bg-surface-0 p-2.5"
            >
              <div class="flex-1">
                <span class="block font-bold text-text-main">{ing.name}</span>
                <span class="text-[0.625rem] text-text-muted tabular-nums"
                  >{ing.kcal} kcal &bull; {ing.protein}g P &bull; {ing.carbs}g C &bull; {ing.fat}g F</span
                >
              </div>
              <div class="flex items-center gap-1.5">
                <input
                  type="number"
                  min="1"
                  max="5000"
                  step="5"
                  value={ing.amount}
                  oninput={(e) =>
                    updateIngredientAmount(idx, Number((e.target as HTMLInputElement).value))}
                  class="w-16 rounded-xl border border-border-subtle bg-surface-50 p-1.5 text-center font-bold text-text-main tabular-nums outline-none"
                />
                <span class="font-bold text-text-muted">{ing.unit}</span>
                <button
                  type="button"
                  onclick={() => removeIngredient(idx)}
                  class="ml-1 flex h-7 w-7 cursor-pointer items-center justify-center rounded-xl text-rose-500 hover:bg-rose-500/10"
                  title="Zutat entfernen"
                >
                  &times;
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>

      <!-- Instructions Step by Step -->
      <div class="space-y-2 border-t border-border-subtle pt-2">
        <span class="block font-bold text-text-main">Zubereitungsschritte</span>

        <div class="space-y-1.5">
          {#each instructions as step, sIdx}
            <div
              class="flex items-start gap-2 rounded-xl border border-border-subtle bg-surface-50 p-2"
            >
              <span
                class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-border-subtle bg-surface-0 text-[0.625rem] font-bold tabular-nums"
              >
                {sIdx + 1}
              </span>
              <span class="flex-1 leading-relaxed text-text-main">{step}</span>
              <button
                type="button"
                onclick={() => removeStep(sIdx)}
                class="cursor-pointer px-1 font-bold text-rose-500 hover:text-rose-600"
              >
                &times;
              </button>
            </div>
          {/each}
        </div>

        <div class="flex items-center gap-2">
          <div class="flex-1">
            <Input
              bind:value={newStepText}
              placeholder="Neuen Zubereitungsschritt hinzufügen..."
              onkeydown={(e: KeyboardEvent) => {
                if (e.key === 'Enter') addStep();
              }}
            />
          </div>
          <button
            type="button"
            onclick={addStep}
            class="h-10 shrink-0 cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-3.5 font-bold hover:bg-surface-100"
          >
            + Schritt
          </button>
        </div>
      </div>

      <!-- Live Total & Per Portion Calculation Banner -->
      <div class="space-y-2 rounded-2xl border border-border-subtle bg-surface-50 p-4">
        <div class="flex items-center justify-between text-xs">
          <span class="font-extrabold text-text-main"
            >Nährwerte pro Portion (bei {portions} Portionen):</span
          >
          <Badge variant="primary" class="text-xs font-extrabold tabular-nums"
            >{portionKcal} kcal</Badge
          >
        </div>
        <div class="grid grid-cols-3 gap-2 text-center text-xs">
          <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
            <span class="block text-[0.625rem] text-text-muted">Protein</span>
            <span class="font-bold text-emerald-500 tabular-nums">{portionProtein} g</span>
          </div>
          <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
            <span class="block text-[0.625rem] text-text-muted">Carbs</span>
            <span class="font-bold text-amber-500 tabular-nums">{portionCarbs} g</span>
          </div>
          <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
            <span class="block text-[0.625rem] text-text-muted">Fett</span>
            <span class="font-bold text-purple-500 tabular-nums">{portionFat} g</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-end gap-2 border-t border-border-subtle pt-3">
      <Btn variant="secondary" size="md" onclick={onclose}>Abbrechen</Btn>
      <Btn
        variant="primary"
        size="md"
        onclick={handleSaveRecipe}
        disabled={!title.trim() || selectedIngredients.length === 0}
      >
        Rezept speichern
      </Btn>
    </div>
  </div>
</Modal>
