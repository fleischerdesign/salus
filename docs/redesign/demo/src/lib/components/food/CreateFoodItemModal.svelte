<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import TextInput from '../ui/TextInput.svelte';
  import SelectDropdown from '../ui/SelectDropdown.svelte';
  import type { FoodItemData } from '../../types/nutrition';

  let {
    open = false,
    initialBarcode = '',
    onclose,
    onsave,
    onopenbarcode
  } = $props<{
    open: boolean;
    initialBarcode?: string;
    onclose: () => void;
    onsave: (food: FoodItemData) => void;
    onopenbarcode?: () => void;
  }>();

  let name = $state('');
  let brand = $state('');
  let category = $state('Protein');
  let barcode = $state('');
  let servingSizeG = $state(100);

  // Macros per 100g
  let kcal = $state(120);
  let protein = $state(22.5);
  let carbs = $state(0.0);
  let fat = $state(2.5);
  let fiber = $state(0.0);
  let sugar = $state(0.0);
  let sodium = $state(0.05);

  const categoryOptions = [
    { value: 'Protein', label: 'Protein & Fleisch/Fisch' },
    { value: 'Kohlenhydrate', label: 'Kohlenhydrate & Getreide' },
    { value: 'Fette', label: 'Fette & Nüsse/Öle' },
    { value: 'Gemüse und Obst', label: 'Gemüse & Früchte' },
    { value: 'Milchprodukte', label: 'Milchprodukte & Alternativen' },
    { value: 'Snacks und Shakes', label: 'Snacks & Nahrungsergänzung' }
  ];

  $effect(() => {
    if (initialBarcode) {
      barcode = initialBarcode;
    }
  });

  // Calculate per serving
  let servingFactor = $derived(servingSizeG / 100);
  let servingKcal = $derived(Math.round(kcal * servingFactor));
  let servingProtein = $derived((protein * servingFactor).toFixed(1));
  let servingCarbs = $derived((carbs * servingFactor).toFixed(1));
  let servingFat = $derived((fat * servingFactor).toFixed(1));
  let servingFiber = $derived((fiber * servingFactor).toFixed(1));

  function handleSave() {
    if (!name.trim()) return;
    const newFood: FoodItemData = {
      id: `custom_${Date.now()}`,
      name: brand.trim() ? `${brand.trim()} - ${name.trim()}` : name.trim(),
      category,
      source: 'Benutzerdefiniert',
      servingSizeG,
      kcalPer100g: Number(kcal) || 0,
      proteinPer100g: Number(protein) || 0,
      carbsPer100g: Number(carbs) || 0,
      fatPer100g: Number(fat) || 0,
      fiberPer100g: Number(fiber) || 0,
      sugarPer100g: Number(sugar) || 0,
      sodiumPer100g: Number(sodium) || 0,
      verified: false
    };
    onsave(newFood);
    onclose();
  }
</script>

{#if open}
  <div
    class="fixed inset-0 bg-black/75 backdrop-blur-md z-70 flex items-center justify-center p-4 overflow-y-auto"
    onclick={(e) => { if (e.target === e.currentTarget) onclose(); }}
    role="presentation"
  >
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-7 max-w-lg w-full shadow-2xl space-y-5 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between pb-3 border-b border-[var(--border-subtle)]">
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Neues Lebensmittel anlegen</h2>
            <Badge variant="primary" class="text-[0.625rem]">Eigene Datenbank</Badge>
          </div>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">Erfasse Nährwerte pro 100g für deine persönliche Lebensmittel-Bibliothek</p>
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
      <div class="space-y-4 text-xs">
        
        <!-- Name & Brand -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <TextInput
            label="Produktname *"
            bind:value={name}
            placeholder="z.B. Skyr Natur 0.2%"
          />
          <TextInput
            label="Marke / Hersteller"
            bind:value={brand}
            placeholder="z.B. Arla / Eigenmarke"
          />
        </div>

        <!-- Category & Barcode -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <SelectDropdown
            label="Kategorie"
            bind:value={category}
            options={categoryOptions}
          />

          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="font-bold text-[var(--text-muted)]">Barcode / EAN</span>
              {#if onopenbarcode}
                <button
                  type="button"
                  onclick={onopenbarcode}
                  class="text-[var(--color-primary)] hover:underline font-bold text-[0.6875rem] cursor-pointer"
                >
                  Scanner öffnen
                </button>
              {/if}
            </div>
            <TextInput
              bind:value={barcode}
              placeholder="z.B. 4012345678901"
            />
          </div>
        </div>

        <!-- Standard Serving Size -->
        <div class="p-3.5 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] space-y-1.5">
          <div class="flex justify-between items-center">
            <label for="food-portion" class="font-bold text-[var(--text-main)]">Typische Standardportion</label>
            <span class="font-extrabold text-[var(--color-primary)] tabular-nums">{servingSizeG} g</span>
          </div>
          <input
            id="food-portion"
            type="number"
            min="5"
            max="1000"
            step="5"
            bind:value={servingSizeG}
            class="w-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-2 tabular-nums text-[var(--text-main)] outline-none"
          />
        </div>

        <!-- Macros Grid (per 100g) -->
        <div>
          <span class="block font-bold text-[var(--text-main)] mb-2">Makronährstoffe pro 100 g:</span>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <div class="p-3 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl">
              <span class="text-[0.625rem] font-bold text-[var(--color-activity)] block uppercase">Energie (kcal)</span>
              <input
                type="number"
                min="0"
                max="900"
                bind:value={kcal}
                class="w-full mt-1 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-1.5 font-extrabold text-sm text-[var(--color-activity)] tabular-nums outline-none text-center"
              />
            </div>

            <div class="p-3 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl">
              <span class="text-[0.625rem] font-bold text-emerald-500 block uppercase">Protein (g)</span>
              <input
                type="number"
                min="0"
                max="100"
                step="0.5"
                bind:value={protein}
                class="w-full mt-1 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-1.5 font-extrabold text-sm text-emerald-500 tabular-nums outline-none text-center"
              />
            </div>

            <div class="p-3 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl">
              <span class="text-[0.625rem] font-bold text-amber-500 block uppercase">Kohlenhydrate (g)</span>
              <input
                type="number"
                min="0"
                max="100"
                step="0.5"
                bind:value={carbs}
                class="w-full mt-1 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-1.5 font-extrabold text-sm text-amber-500 tabular-nums outline-none text-center"
              />
            </div>

            <div class="p-3 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl">
              <span class="text-[0.625rem] font-bold text-purple-500 block uppercase">Fett (g)</span>
              <input
                type="number"
                min="0"
                max="100"
                step="0.5"
                bind:value={fat}
                class="w-full mt-1 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-1.5 font-extrabold text-sm text-purple-500 tabular-nums outline-none text-center"
              />
            </div>
          </div>
        </div>

        <!-- Micronutrients Optional Row -->
        <div class="grid grid-cols-3 gap-2 text-center">
          <div class="p-2.5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
            <span class="text-[0.625rem] text-[var(--text-muted)] block">Ballaststoffe (g)</span>
            <input type="number" step="0.5" bind:value={fiber} class="w-full text-center bg-transparent font-bold text-xs text-[var(--text-main)] tabular-nums outline-none mt-0.5" />
          </div>
          <div class="p-2.5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
            <span class="text-[0.625rem] text-[var(--text-muted)] block">davon Zucker (g)</span>
            <input type="number" step="0.5" bind:value={sugar} class="w-full text-center bg-transparent font-bold text-xs text-[var(--text-main)] tabular-nums outline-none mt-0.5" />
          </div>
          <div class="p-2.5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
            <span class="text-[0.625rem] text-[var(--text-muted)] block">Natrium (g)</span>
            <input type="number" step="0.01" bind:value={sodium} class="w-full text-center bg-transparent font-bold text-xs text-[var(--text-main)] tabular-nums outline-none mt-0.5" />
          </div>
        </div>

        <!-- Calculated Live Preview per Serving -->
        <div class="p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center justify-between flex-wrap gap-2">
          <div>
            <span class="font-bold text-emerald-500 block">Berechnung für 1 Portion ({servingSizeG} g):</span>
            <span class="text-[0.6875rem] text-[var(--text-muted)] tabular-nums">{servingProtein}g P &bull; {servingCarbs}g C &bull; {servingFat}g F &bull; {servingFiber}g Fiber</span>
          </div>
          <Badge variant="success" class="text-xs font-bold tabular-nums">{servingKcal} kcal</Badge>
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
          onclick={handleSave}
          disabled={!name.trim()}
          class="px-5 py-2 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs disabled:opacity-50"
        >
          Lebensmittel speichern
        </button>
      </div>

    </div>
  </div>
{/if}
