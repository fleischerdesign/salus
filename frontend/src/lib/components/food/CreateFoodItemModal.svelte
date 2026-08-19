<script lang="ts">
  import Badge from '../ui/Badge.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Modal from '../ui/Modal.svelte';
  import Btn from '../ui/Btn.svelte';
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
      defaultServingG: servingSizeG,
      servingSizeG,
      per100g: {
        kcal: Number(kcal) || 0,
        protein: Number(protein) || 0,
        carbs: Number(carbs) || 0,
        fat: Number(fat) || 0,
        fiber: Number(fiber) || 0,
        sugar: Number(sugar) || 0,
        sodium: Number(sodium) || 0
      },
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

<Modal
  {open}
  title="Neues Lebensmittel anlegen"
  subtitle="Erfasse Nährwerte pro 100g für deine persönliche Lebensmittel-Bibliothek"
  icon="nutrition"
  size="md"
  {onclose}
>
  <div class="space-y-4 text-xs">
    <!-- Name & Brand -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Input label="Produktname *" bind:value={name} placeholder="z.B. Skyr Natur 0.2%" />
      <Input label="Marke / Hersteller" bind:value={brand} placeholder="z.B. Arla / Eigenmarke" />
    </div>

    <!-- Category & Barcode -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Select label="Kategorie" bind:value={category} options={categoryOptions} />

      <div>
        <div class="mb-1 flex items-center justify-between">
          <span class="font-bold text-text-muted">Barcode / EAN</span>
          {#if onopenbarcode}
            <button
              type="button"
              onclick={onopenbarcode}
              class="cursor-pointer text-[0.6875rem] font-bold text-primary hover:underline"
            >
              Scanner öffnen
            </button>
          {/if}
        </div>
        <Input bind:value={barcode} placeholder="z.B. 4012345678901" />
      </div>
    </div>

    <!-- Standard Serving Size -->
    <Input
      label="Typische Standardportion"
      unit="g"
      type="number"
      min={5}
      max={1000}
      step={5}
      bind:value={servingSizeG}
    />

    <!-- Macros Grid (per 100g) -->
    <div>
      <span class="mb-2 block font-bold text-text-main">Makronährstoffe pro 100 g:</span>
      <div class="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
        <div class="rounded-2xl border border-border-subtle bg-surface-0 p-3">
          <span class="block text-[0.625rem] font-bold text-activity uppercase">Energie (kcal)</span
          >
          <input
            type="number"
            min="0"
            max="900"
            bind:value={kcal}
            class="mt-1 w-full rounded-xl border border-border-subtle bg-surface-50 p-1.5 text-center text-sm font-extrabold text-activity tabular-nums outline-none"
          />
        </div>

        <div class="rounded-2xl border border-border-subtle bg-surface-0 p-3">
          <span class="block text-[0.625rem] font-bold text-emerald-500 uppercase">Protein (g)</span
          >
          <input
            type="number"
            min="0"
            max="100"
            step="0.5"
            bind:value={protein}
            class="mt-1 w-full rounded-xl border border-border-subtle bg-surface-50 p-1.5 text-center text-sm font-extrabold text-emerald-500 tabular-nums outline-none"
          />
        </div>

        <div class="rounded-2xl border border-border-subtle bg-surface-0 p-3">
          <span class="block text-[0.625rem] font-bold text-amber-500 uppercase"
            >Kohlenhydrate (g)</span
          >
          <input
            type="number"
            min="0"
            max="100"
            step="0.5"
            bind:value={carbs}
            class="mt-1 w-full rounded-xl border border-border-subtle bg-surface-50 p-1.5 text-center text-sm font-extrabold text-amber-500 tabular-nums outline-none"
          />
        </div>

        <div class="rounded-2xl border border-border-subtle bg-surface-0 p-3">
          <span class="block text-[0.625rem] font-bold text-purple-500 uppercase">Fett (g)</span>
          <input
            type="number"
            min="0"
            max="100"
            step="0.5"
            bind:value={fat}
            class="mt-1 w-full rounded-xl border border-border-subtle bg-surface-50 p-1.5 text-center text-sm font-extrabold text-purple-500 tabular-nums outline-none"
          />
        </div>
      </div>
    </div>

    <!-- Micronutrients Optional Row -->
    <div class="grid grid-cols-3 gap-2 text-center">
      <div class="rounded-2xl border border-border-subtle bg-surface-50 p-2.5">
        <span class="block text-[0.625rem] text-text-muted">Ballaststoffe (g)</span>
        <input
          type="number"
          step="0.5"
          bind:value={fiber}
          class="mt-0.5 w-full bg-transparent text-center text-xs font-bold text-text-main tabular-nums outline-none"
        />
      </div>
      <div class="rounded-2xl border border-border-subtle bg-surface-50 p-2.5">
        <span class="block text-[0.625rem] text-text-muted">davon Zucker (g)</span>
        <input
          type="number"
          step="0.5"
          bind:value={sugar}
          class="mt-0.5 w-full bg-transparent text-center text-xs font-bold text-text-main tabular-nums outline-none"
        />
      </div>
      <div class="rounded-2xl border border-border-subtle bg-surface-50 p-2.5">
        <span class="block text-[0.625rem] text-text-muted">Natrium (g)</span>
        <input
          type="number"
          step="0.01"
          bind:value={sodium}
          class="mt-0.5 w-full bg-transparent text-center text-xs font-bold text-text-main tabular-nums outline-none"
        />
      </div>
    </div>

    <!-- Calculated Live Preview per Serving -->
    <div
      class="flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-3.5"
    >
      <div>
        <span class="block font-bold text-emerald-500"
          >Berechnung für 1 Portion ({servingSizeG} g):</span
        >
        <span class="text-[0.6875rem] text-text-muted tabular-nums"
          >{servingProtein}g P &bull; {servingCarbs}g C &bull; {servingFat}g F &bull; {servingFiber}g
          Fiber</span
        >
      </div>
      <Badge variant="success" class="text-xs font-bold tabular-nums">{servingKcal} kcal</Badge>
    </div>
  </div>

  <!-- Action Buttons -->
  <div class="flex justify-end gap-2 border-t border-border-subtle pt-3">
    <Btn variant="secondary" size="md" onclick={onclose}>Abbrechen</Btn>
    <Btn variant="primary" size="md" onclick={handleSave} disabled={!name.trim()}>
      Lebensmittel speichern
    </Btn>
  </div>
</Modal>
