<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import type { FoodItem, LoggedFoodItem, MealSlotData } from '../../types/nutrition';

  let {
    open = false,
    targetMeal = null,
    onaddfood,
    onopenbarcode,
    onclose
  } = $props<{
    open: boolean;
    targetMeal: MealSlotData | null;
    onaddfood: (mealId: string, item: LoggedFoodItem) => void;
    onopenbarcode?: () => void;
    onclose: () => void;
  }>();

  let searchQuery = $state('');
  let selectedCategory = $state<string>('Alle');
  let selectedServingG = $state<number>(100);
  let selectedFood = $state<FoodItem | null>(null);

  const categories = ['Alle', 'Protein', 'Kohlenhydrate', 'Fette', 'Gemüse und Obst', 'Snacks und Shakes'];

  const foodCatalog: FoodItem[] = [
    {
      id: 'f1',
      name: 'Hähnchenbrustfilet (Bio)',
      brand: 'Bio-Geflügelhof',
      category: 'Protein',
      per100g: { kcal: 110, protein: 23.5, carbs: 0.0, fat: 1.5, fiber: 0.0 },
      defaultServingG: 180,
      servingName: '1 Filet (180g)'
    },
    {
      id: 'f2',
      name: 'Haferflocken zart',
      brand: 'Alnatura',
      category: 'Kohlenhydrate',
      per100g: { kcal: 370, protein: 13.5, carbs: 58.7, fat: 7.0, fiber: 10.0 },
      defaultServingG: 80,
      servingName: '1 Schale (80g)'
    },
    {
      id: 'f3',
      name: 'Magerquark (Speisequark Magerstufe)',
      brand: 'Berchtesgadener Land',
      category: 'Protein',
      per100g: { kcal: 68, protein: 12.5, carbs: 4.0, fat: 0.2, fiber: 0.0 },
      defaultServingG: 250,
      servingName: '1/2 Becher (250g)'
    },
    {
      id: 'f4',
      name: 'Bio-Eier (Größe L)',
      brand: 'Regionaler Freilandbetrieb',
      category: 'Protein',
      per100g: { kcal: 143, protein: 12.8, carbs: 0.7, fat: 9.9, fiber: 0.0 },
      defaultServingG: 120,
      servingName: '2 Stück (120g)'
    },
    {
      id: 'f5',
      name: 'Wildlachsfilet (MSC)',
      brand: 'Followfish',
      category: 'Protein',
      per100g: { kcal: 178, protein: 20.0, carbs: 0.0, fat: 11.0, fiber: 0.0 },
      defaultServingG: 150,
      servingName: '1 Filet (150g)'
    },
    {
      id: 'f6',
      name: 'Avocado Hass (Bio)',
      brand: 'Bio',
      category: 'Fette',
      per100g: { kcal: 160, protein: 2.0, carbs: 1.7, fat: 15.0, fiber: 6.7 },
      defaultServingG: 100,
      servingName: '1/2 Avocado (100g)'
    },
    {
      id: 'f7',
      name: 'Basmatireis (roh)',
      brand: 'Davert',
      category: 'Kohlenhydrate',
      per100g: { kcal: 350, protein: 8.5, carbs: 77.0, fat: 0.8, fiber: 1.5 },
      defaultServingG: 75,
      servingName: '1 Portion roh (75g)'
    },
    {
      id: 'f8',
      name: 'Whey Protein Isolat (Vanille)',
      brand: 'Salus Nutrition Lab',
      category: 'Snacks und Shakes',
      per100g: { kcal: 375, protein: 86.0, carbs: 2.5, fat: 1.2, fiber: 0.5 },
      defaultServingG: 30,
      servingName: '1 Messlöffel (30g)'
    },
    {
      id: 'f9',
      name: 'Brokkoli frisch',
      brand: 'Frischemarkt',
      category: 'Gemüse und Obst',
      per100g: { kcal: 34, protein: 2.8, carbs: 4.0, fat: 0.4, fiber: 3.0 },
      defaultServingG: 150,
      servingName: '1 Beilage (150g)'
    },
    {
      id: 'f10',
      name: 'Blaubeeren frisch',
      brand: 'Bio',
      category: 'Gemüse und Obst',
      per100g: { kcal: 57, protein: 0.7, carbs: 12.0, fat: 0.3, fiber: 2.4 },
      defaultServingG: 125,
      servingName: '1 Schälchen (125g)'
    }
  ];

  let filteredCatalog = $derived(
    foodCatalog.filter(f => {
      const matchCat = selectedCategory === 'Alle' || f.category === selectedCategory;
      const matchSearch = !searchQuery || f.name.toLowerCase().includes(searchQuery.toLowerCase()) || (f.brand && f.brand.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchCat && matchSearch;
    })
  );

  function handleSelect(food: FoodItem) {
    selectedFood = food;
    selectedServingG = food.defaultServingG;
  }

  function handleAdd() {
    if (!selectedFood || !targetMeal) return;

    const ratio = selectedServingG / 100;
    const newItem: LoggedFoodItem = {
      id: `lfi_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      name: selectedFood.name,
      amountG: selectedServingG,
      kcal: Math.round(selectedFood.per100g.kcal * ratio),
      protein: Number((selectedFood.per100g.protein * ratio).toFixed(1)),
      carbs: Number((selectedFood.per100g.carbs * ratio).toFixed(1)),
      fat: Number((selectedFood.per100g.fat * ratio).toFixed(1)),
      fiber: Number((selectedFood.per100g.fiber * ratio).toFixed(1))
    };

    onaddfood(targetMeal.id, newItem);
    selectedFood = null;
    onclose();
  }
</script>

{#if open && targetMeal}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-70 flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl space-y-5 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-[var(--color-activity)]/10 text-[var(--color-activity)] flex items-center justify-center font-bold text-lg shrink-0">
            
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-extrabold text-[var(--text-main)]">Lebensmittel hinzufügen</h2>
              <Badge variant="activity" class="font-bold">In: {targetMeal.title}</Badge>
            </div>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">Suche in der Nährwert-Datenbank oder scanne einen Barcode</p>
          </div>
        </div>

        <button
          type="button"
          onclick={onclose}
          class="w-8 h-8 rounded-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center text-lg cursor-pointer transition-colors"
          title="Schließen"
          aria-label="Schließen"
        >
          &times;
        </button>
      </div>

      <!-- Quick Barcode Action & Search Input -->
      <div class="grid grid-cols-1 sm:grid-cols-12 gap-3">
        <div class="sm:col-span-8">
          <input
            type="text"
            placeholder="Lebensmittel oder Marke suchen..."
            bind:value={searchQuery}
            class="w-full px-4 py-2.5 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
          />
        </div>
        <div class="sm:col-span-4">
          <button
            type="button"
            onclick={() => {
              onclose();
              onopenbarcode?.();
            }}
            class="w-full h-full py-2.5 px-3 rounded-2xl bg-[var(--color-primary)]/10 border border-[var(--color-primary)]/30 hover:bg-[var(--color-primary)]/15 text-[var(--color-primary)] font-bold text-xs flex items-center justify-center gap-1.5 cursor-pointer transition-all shadow-2xs"
          >
            <span> Barcode scannen</span>
          </button>
        </div>
      </div>

      <!-- Category Filter Pills with Soft Mask Fade -->
      <div class="relative w-full overflow-hidden">
        <div class="flex gap-2 overflow-x-auto py-1 px-1 no-scrollbar scroll-mask-x select-none">
          {#each categories as cat}
            <button
              type="button"
              onclick={() => selectedCategory = cat}
              class="px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap cursor-pointer transition-all shrink-0 {selectedCategory === cat ? 'bg-[var(--color-primary)] text-white shadow-xs' : 'bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
            >
              {cat}
            </button>
          {/each}
        </div>
      </div>

      <!-- Selected Food Portion Configurator (if active) -->
      {#if selectedFood}
        {@const ratio = selectedServingG / 100}
        {@const calcKcal = Math.round(selectedFood.per100g.kcal * ratio)}
        {@const calcP = Number((selectedFood.per100g.protein * ratio).toFixed(1))}
        {@const calcC = Number((selectedFood.per100g.carbs * ratio).toFixed(1))}
        {@const calcF = Number((selectedFood.per100g.fat * ratio).toFixed(1))}
        
        <div class="p-4 bg-[var(--bg-surface-50)] border-2 border-[var(--color-primary)] rounded-3xl space-y-3 animate-[fadeIn_0.15s_ease-out]">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-extrabold text-[var(--text-main)]">{selectedFood.name}</h3>
              <span class="text-xs text-[var(--text-muted)]">{selectedFood.brand}</span>
            </div>
            <button
              type="button"
              onclick={() => selectedFood = null}
              class="text-xs text-[var(--text-muted)] hover:text-rose-500 cursor-pointer"
            >
              Abwählen &times;
            </button>
          </div>

          <!-- Quantity Stepper -->
          <div class="flex items-center justify-between flex-wrap gap-3 bg-[var(--bg-surface-0)] p-3 rounded-2xl border border-[var(--border-subtle)]">
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-[var(--text-muted)]">Menge:</span>
              <input
                type="number"
                min="5"
                max="2000"
                step="5"
                bind:value={selectedServingG}
                class="w-20 px-2 py-1 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-sm font-extrabold text-center tabular-nums text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
              />
              <span class="text-xs font-bold text-[var(--text-muted)]">Gramm (g)</span>
            </div>

            <!-- Quick Portion Buttons -->
            <div class="flex gap-1.5">
              <button
                type="button"
                onclick={() => selectedServingG = 100}
                class="px-2 py-1 rounded-lg bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[0.6875rem] font-bold text-[var(--text-muted)] cursor-pointer hover:bg-[var(--bg-surface-100)]"
              >
                100g
              </button>
              <button
                type="button"
                onclick={() => selectedServingG = selectedFood?.defaultServingG || 150}
                class="px-2 py-1 rounded-lg bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[0.6875rem] font-bold text-[var(--color-primary)] cursor-pointer hover:bg-[var(--bg-surface-100)]"
              >
                {selectedFood.servingName}
              </button>
            </div>
          </div>

          <!-- Calculated Live Macros -->
          <div class="grid grid-cols-4 gap-2 text-center text-xs">
            <div class="p-2 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)]">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Kalorien</span>
              <span class="font-extrabold text-sm text-[var(--color-activity)] tabular-nums">{calcKcal} kcal</span>
            </div>
            <div class="p-2 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)]">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Protein</span>
              <span class="font-extrabold text-sm text-emerald-500 tabular-nums">{calcP}g</span>
            </div>
            <div class="p-2 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)]">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Carbs</span>
              <span class="font-extrabold text-sm text-amber-500 tabular-nums">{calcC}g</span>
            </div>
            <div class="p-2 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)]">
              <span class="text-[0.625rem] text-[var(--text-muted)] block">Fett</span>
              <span class="font-extrabold text-sm text-purple-500 tabular-nums">{calcF}g</span>
            </div>
          </div>

          <button
            type="button"
            onclick={handleAdd}
            class="w-full py-2.5 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md"
          >
            + Zu „{targetMeal.title}“ hinzufügen ({calcKcal} kcal)
          </button>
        </div>
      {/if}

      <!-- Food Catalog List -->
      <div class="space-y-2 max-h-[38vh] overflow-y-auto pr-1">
        {#each filteredCatalog as item}
          <div
            class="p-3 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] hover:border-[var(--color-primary)] flex items-center justify-between gap-3 transition-all group"
          >
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-extrabold text-[var(--text-main)] group-hover:text-[var(--color-primary)]">
                  {item.name}
                </span>
                <Badge variant="default" class="text-[0.5625rem]">{item.category}</Badge>
              </div>
              <span class="text-[0.6875rem] text-[var(--text-muted)] block mt-0.5">
                {item.brand} &bull; 100g: {item.per100g.kcal} kcal, {item.per100g.protein}g P, {item.per100g.carbs}g C, {item.per100g.fat}g F
              </span>
            </div>

            <button
              type="button"
              onclick={() => handleSelect(item)}
              class="px-3 py-1.5 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-white cursor-pointer transition-all shrink-0"
            >
              Auswählen &rarr;
            </button>
          </div>
        {/each}
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between pt-3 border-t border-[var(--border-subtle)]">
        <span class="text-xs text-[var(--text-muted)]">{filteredCatalog.length} Lebensmittel verfügbar</span>
        <Btn variant="secondary" size="sm" onclick={onclose}>Schließen</Btn>
      </div>

    </div>
  </div>
{/if}
