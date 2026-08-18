<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import TextInput from '../ui/TextInput.svelte';
  import SelectDropdown from '../ui/SelectDropdown.svelte';
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
      ? availableFoods.filter(f => f.name.toLowerCase().includes(searchFoodQuery.toLowerCase())).slice(0, 5)
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
      kcal: Math.round(food.kcalPer100g * factor),
      protein: Number((food.proteinPer100g * factor).toFixed(1)),
      carbs: Number((food.carbsPer100g * factor).toFixed(1)),
      fat: Number((food.fatPer100g * factor).toFixed(1))
    });
    isAddingIngredient = false;
    searchFoodQuery = '';
  }

  function updateIngredientAmount(idx: number, newAmount: number) {
    const ing = selectedIngredients[idx];
    if (!ing) return;
    const food = availableFoods.find(f => f.id === ing.foodId);
    const factor = newAmount / (food?.servingSizeG ? 100 : 100);
    ing.amount = newAmount;
    if (food) {
      ing.kcal = Math.round(food.kcalPer100g * (newAmount / 100));
      ing.protein = Number((food.proteinPer100g * (newAmount / 100)).toFixed(1));
      ing.carbs = Number((food.carbsPer100g * (newAmount / 100)).toFixed(1));
      ing.fat = Number((food.fatPer100g * (newAmount / 100)).toFixed(1));
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
      ingredients: selectedIngredients.map(i => ({
        name: i.name,
        amount: i.amount,
        unit: i.unit,
        kcal: i.kcal,
        protein: i.protein,
        carbs: i.carbs,
        fat: i.fat
      })),
      instructions: instructions.length > 0 ? instructions : ['Alle Zutaten wie gewünscht zubereiten.']
    };
    onsave(newRecipe);
    onclose();
  }
</script>

{#if open}
  <div
    class="fixed inset-0 bg-black/75 backdrop-blur-md z-70 flex items-center justify-center p-4 overflow-y-auto"
    onclick={(e) => { if (e.target === e.currentTarget) onclose(); }}
    role="presentation"
  >
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-7 max-w-xl w-full shadow-2xl space-y-5 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between pb-3 border-b border-[var(--border-subtle)]">
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Neues Rezept erstellen</h2>
            <Badge variant="primary" class="text-[0.625rem]">Rezept-Rechner</Badge>
          </div>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">Kombiniere Zutaten aus deinem Katalog zur automatischen Nährwertberechnung</p>
        </div>
        <button
          type="button"
          onclick={onclose}
          class="w-8 h-8 rounded-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center text-lg cursor-pointer transition-colors"
          aria-label="Schließen"
        >
          &times;
        </button>
      </div>

      <!-- Form Content -->
      <div class="space-y-4 text-xs max-h-[68vh] overflow-y-auto pr-1">
        
        <!-- Basic Recipe Info -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="sm:col-span-2">
            <TextInput
              label="Rezepttitel *"
              bind:value={title}
              placeholder="z.B. Hähnchen-Reis Bowl mit Brokkoli"
            />
          </div>
          <div>
            <TextInput
              label="Portionen"
              type="number"
              bind:value={portions}
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <SelectDropdown
            label="Kategorie"
            bind:value={category}
            options={categoryOptions}
          />
          <TextInput
            label="Zubereitungszeit"
            bind:value={prepTime}
            placeholder="z.B. 25 Min"
          />
        </div>

        <!-- Ingredients Section -->
        <div class="space-y-2 pt-1">
          <div class="flex items-center justify-between">
            <span class="font-bold text-[var(--text-main)]">Enthaltene Zutaten ({selectedIngredients.length})</span>
            <button
              type="button"
              onclick={() => isAddingIngredient = !isAddingIngredient}
              class="px-3 py-1 rounded-xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] hover:bg-[var(--color-primary)]/20 font-bold transition-all cursor-pointer"
            >
              + Zutat hinzufügen
            </button>
          </div>

          <!-- Add Ingredient Dropdown / Search -->
          {#if isAddingIngredient}
            <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-2 animate-[fadeIn_0.15s_ease-out]">
              <input
                type="text"
                bind:value={searchFoodQuery}
                placeholder="Lebensmittel aus Katalog suchen..."
                class="w-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-2 text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
              />
              <div class="divide-y divide-[var(--border-subtle)] max-h-36 overflow-y-auto">
                {#each filteredFoods as f}
                  <div class="py-2 flex items-center justify-between gap-2">
                    <div>
                      <span class="font-bold text-[var(--text-main)] block">{f.name}</span>
                      <span class="text-[0.625rem] text-[var(--text-muted)] tabular-nums">{f.kcalPer100g} kcal/100g &bull; {f.proteinPer100g}g P</span>
                    </div>
                    <button
                      type="button"
                      onclick={() => addFoodToRecipe(f)}
                      class="px-2.5 py-1 rounded-lg bg-[var(--color-primary)] text-white text-[0.6875rem] font-bold hover:opacity-90 cursor-pointer"
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
              <div class="p-2.5 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] flex items-center justify-between gap-3">
                <div class="flex-1">
                  <span class="font-bold text-[var(--text-main)] block">{ing.name}</span>
                  <span class="text-[0.625rem] text-[var(--text-muted)] tabular-nums">{ing.kcal} kcal &bull; {ing.protein}g P &bull; {ing.carbs}g C &bull; {ing.fat}g F</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <input
                    type="number"
                    min="1"
                    max="5000"
                    step="5"
                    value={ing.amount}
                    oninput={(e) => updateIngredientAmount(idx, Number((e.target as HTMLInputElement).value))}
                    class="w-16 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-1.5 text-center font-bold tabular-nums text-[var(--text-main)] outline-none"
                  />
                  <span class="text-[var(--text-muted)] font-bold">{ing.unit}</span>
                  <button
                    type="button"
                    onclick={() => removeIngredient(idx)}
                    class="w-7 h-7 rounded-xl text-rose-500 hover:bg-rose-500/10 flex items-center justify-center cursor-pointer ml-1"
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
        <div class="space-y-2 pt-2 border-t border-[var(--border-subtle)]">
          <span class="font-bold text-[var(--text-main)] block">Zubereitungsschritte</span>
          
          <div class="space-y-1.5">
            {#each instructions as step, sIdx}
              <div class="p-2 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] flex items-start gap-2">
                <span class="w-5 h-5 rounded-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[0.625rem] font-bold flex items-center justify-center shrink-0 mt-0.5 tabular-nums">
                  {sIdx + 1}
                </span>
                <span class="flex-1 text-[var(--text-main)] leading-relaxed">{step}</span>
                <button
                  type="button"
                  onclick={() => removeStep(sIdx)}
                  class="text-rose-500 hover:text-rose-600 cursor-pointer font-bold px-1"
                >
                  &times;
                </button>
              </div>
            {/each}
          </div>

          <div class="flex gap-2">
            <input
              type="text"
              bind:value={newStepText}
              placeholder="Neuen Zubereitungsschritt hinzufügen..."
              class="flex-1 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2 text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
              onkeydown={(e) => { if (e.key === 'Enter') addStep(); }}
            />
            <button
              type="button"
              onclick={addStep}
              class="px-3 py-2 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] hover:bg-[var(--bg-surface-100)] font-bold cursor-pointer"
            >
              + Schritt
            </button>
          </div>
        </div>

        <!-- Live Total & Per Portion Calculation Banner -->
        <div class="p-4 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-extrabold text-[var(--text-main)]">Nährwerte pro Portion (bei {portions} Portionen):</span>
            <Badge variant="primary" class="font-extrabold text-xs tabular-nums">{portionKcal} kcal</Badge>
          </div>
          <div class="grid grid-cols-3 gap-2 text-center text-xs">
            <div class="p-2 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Protein</span>
              <span class="font-bold text-emerald-500 tabular-nums">{portionProtein} g</span>
            </div>
            <div class="p-2 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Carbs</span>
              <span class="font-bold text-amber-500 tabular-nums">{portionCarbs} g</span>
            </div>
            <div class="p-2 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Fett</span>
              <span class="font-bold text-purple-500 tabular-nums">{portionFat} g</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Action Buttons -->
      <div class="flex gap-2 justify-end pt-3 border-t border-[var(--border-subtle)]">
        <button
          type="button"
          onclick={onclose}
          class="px-4 py-2 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold hover:bg-[var(--bg-surface-100)] transition-all cursor-pointer"
        >
          Abbrechen
        </button>
        <button
          type="button"
          onclick={handleSaveRecipe}
          disabled={!title.trim() || selectedIngredients.length === 0}
          class="px-5 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs disabled:opacity-50"
        >
          Rezept speichern
        </button>
      </div>

    </div>
  </div>
{/if}
