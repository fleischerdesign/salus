<script lang="ts">
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Modal from '../ui/Modal.svelte';
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

  const categories = [
    'Alle',
    'Protein',
    'Kohlenhydrate',
    'Fette',
    'Gemüse und Obst',
    'Snacks und Shakes'
  ];

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
    foodCatalog.filter((f) => {
      const matchCat = selectedCategory === 'Alle' || f.category === selectedCategory;
      const matchSearch =
        !searchQuery ||
        f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (f.brand && f.brand.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchCat && matchSearch;
    })
  );

  function handleSelect(food: FoodItem) {
    selectedFood = food;
    selectedServingG = food.defaultServingG || food.servingSizeG || 100;
  }

  function handleAdd() {
    if (!selectedFood || !targetMeal) return;

    const ratio = selectedServingG / 100;
    const per100 = selectedFood.per100g || {
      kcal: selectedFood.kcalPer100g || 0,
      protein: selectedFood.proteinPer100g || 0,
      carbs: selectedFood.carbsPer100g || 0,
      fat: selectedFood.fatPer100g || 0,
      fiber: selectedFood.fiberPer100g || 0
    };

    const newItem: LoggedFoodItem = {
      id: `lfi_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      name: selectedFood.name,
      amountG: selectedServingG,
      kcal: Math.round(per100.kcal * ratio),
      protein: Number((per100.protein * ratio).toFixed(1)),
      carbs: Number((per100.carbs * ratio).toFixed(1)),
      fat: Number((per100.fat * ratio).toFixed(1)),
      fiber: Number((per100.fiber * ratio).toFixed(1))
    };

    onaddfood(targetMeal.id, newItem);
    selectedFood = null;
    onclose();
  }
</script>

<Modal
  open={open && Boolean(targetMeal)}
  title="Lebensmittel hinzufügen"
  subtitle={`In: ${targetMeal?.title || ''} • Suche im Katalog oder scanne Barcode`}
  icon="nutrition"
  size="xl"
  {onclose}
>
  <div class="space-y-4">
    <!-- Quick Barcode Action & Search Input -->
    <div class="grid grid-cols-1 items-center gap-3 sm:grid-cols-12">
      <div class="sm:col-span-8">
        <Input
          icon="search"
          placeholder="Lebensmittel oder Marke suchen..."
          bind:value={searchQuery}
        />
      </div>
      <div class="sm:col-span-4">
        <button
          type="button"
          onclick={() => {
            onclose();
            onopenbarcode?.();
          }}
          class="flex h-10 w-full cursor-pointer items-center justify-center gap-1.5 rounded-xl border border-primary/30 bg-primary/10 px-3 text-xs font-bold text-primary shadow-2xs transition-all hover:bg-primary/15"
        >
          <span>Barcode scannen</span>
        </button>
      </div>
    </div>

    <!-- Category Filter Pills with Soft Mask Fade -->
    <div class="relative w-full overflow-hidden">
      <div class="no-scrollbar scroll-mask-x flex gap-2 overflow-x-auto px-1 py-1 select-none">
        {#each categories as cat}
          <button
            type="button"
            onclick={() => (selectedCategory = cat)}
            class="shrink-0 cursor-pointer rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {selectedCategory ===
            cat
              ? 'bg-primary text-white shadow-xs'
              : 'border border-border-subtle bg-surface-0 text-text-muted hover:text-text-main'}"
          >
            {cat}
          </button>
        {/each}
      </div>
    </div>

    <!-- Selected Food Portion Configurator (if active) -->
    {#if selectedFood}
      {@const ratio = selectedServingG / 100}
      {@const per100 = selectedFood.per100g || {
        kcal: selectedFood.kcalPer100g || 0,
        protein: selectedFood.proteinPer100g || 0,
        carbs: selectedFood.carbsPer100g || 0,
        fat: selectedFood.fatPer100g || 0
      }}
      {@const calcKcal = Math.round(per100.kcal * ratio)}
      {@const calcP = Number((per100.protein * ratio).toFixed(1))}
      {@const calcC = Number((per100.carbs * ratio).toFixed(1))}
      {@const calcF = Number((per100.fat * ratio).toFixed(1))}

      <div class="animate-fade-in space-y-3 rounded-3xl border-2 border-primary bg-surface-50 p-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-extrabold text-text-main">{selectedFood.name}</h3>
            <span class="text-xs text-text-muted">{selectedFood.brand}</span>
          </div>
          <button
            type="button"
            onclick={() => (selectedFood = null)}
            class="cursor-pointer text-xs text-text-muted hover:text-rose-500"
          >
            Abwählen &times;
          </button>
        </div>

        <!-- Quantity Stepper -->
        <div
          class="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border-subtle bg-surface-0 p-3"
        >
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-text-muted">Menge:</span>
            <div class="w-28">
              <Input
                type="number"
                min={5}
                max={2000}
                step={5}
                unit="g"
                bind:value={selectedServingG}
              />
            </div>
          </div>

          <!-- Quick Portion Buttons -->
          <div class="flex gap-1.5">
            <button
              type="button"
              onclick={() => (selectedServingG = 100)}
              class="cursor-pointer rounded-lg border border-border-subtle bg-surface-50 px-2 py-1 text-[0.6875rem] font-bold text-text-muted hover:bg-surface-100"
            >
              100g
            </button>
            <button
              type="button"
              onclick={() => (selectedServingG = selectedFood?.defaultServingG || 150)}
              class="cursor-pointer rounded-lg border border-border-subtle bg-surface-50 px-2 py-1 text-[0.6875rem] font-bold text-primary hover:bg-surface-100"
            >
              {selectedFood.servingName}
            </button>
          </div>
        </div>

        <!-- Calculated Live Macros -->
        <div class="grid grid-cols-4 gap-2 text-center text-xs">
          <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
            <span class="block text-[0.625rem] text-text-muted">Kalorien</span>
            <span class="text-sm font-extrabold text-activity tabular-nums">{calcKcal} kcal</span>
          </div>
          <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
            <span class="block text-[0.625rem] text-text-muted">Protein</span>
            <span class="text-sm font-extrabold text-emerald-500 tabular-nums">{calcP}g</span>
          </div>
          <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
            <span class="block text-[0.625rem] text-text-muted">Carbs</span>
            <span class="text-sm font-extrabold text-amber-500 tabular-nums">{calcC}g</span>
          </div>
          <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
            <span class="block text-[0.625rem] text-text-muted">Fett</span>
            <span class="text-sm font-extrabold text-purple-500 tabular-nums">{calcF}g</span>
          </div>
        </div>

        <button
          type="button"
          onclick={handleAdd}
          class="w-full cursor-pointer rounded-2xl bg-primary py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-90"
        >
          + Zu „{targetMeal.title}“ hinzufügen ({calcKcal} kcal)
        </button>
      </div>
    {/if}

    <!-- Food Catalog List -->
    <div class="max-h-[38vh] space-y-2 overflow-y-auto pr-1">
      {#each filteredCatalog as item}
        {@const per100 = item.per100g || {
          kcal: item.kcalPer100g || 0,
          protein: item.proteinPer100g || 0,
          carbs: item.carbsPer100g || 0,
          fat: item.fatPer100g || 0
        }}
        <div
          class="group flex items-center justify-between gap-3 rounded-2xl border border-border-subtle bg-surface-0 p-3 transition-all hover:border-primary"
        >
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-extrabold text-text-main group-hover:text-primary">
                {item.name}
              </span>
              <Badge variant="default" class="text-[0.5625rem]">{item.category}</Badge>
            </div>
            <span class="mt-0.5 block text-[0.6875rem] text-text-muted">
              {item.brand} &bull; 100g: {per100.kcal} kcal, {per100.protein}g P, {per100.carbs}g C, {per100.fat}g
              F
            </span>
          </div>

          <button
            type="button"
            onclick={() => handleSelect(item)}
            class="shrink-0 cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-3 py-1.5 text-xs font-bold text-primary transition-all hover:bg-primary hover:text-white"
          >
            Auswählen &rarr;
          </button>
        </div>
      {/each}
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between border-t border-border-subtle pt-3">
      <span class="text-xs text-text-muted">{filteredCatalog.length} Lebensmittel verfügbar</span>
      <Btn variant="secondary" size="md" onclick={onclose}>Schließen</Btn>
    </div>
  </div>
</Modal>
