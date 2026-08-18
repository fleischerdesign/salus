<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import { createFoodItem, updateFoodItem } from '$lib/mutations/food-item';
  import type { FoodItem } from '$lib/db/types';

  interface Props {
    open: boolean;
    food: FoodItem | null;
    initialBarcode?: string | null;
    onClose: () => void;
    onSaved?: () => void;
  }

  let { open, food, initialBarcode = null, onClose, onSaved }: Props = $props();

  let name = $state('');
  let brand = $state('');
  let calories = $state(0);
  let protein = $state(0);
  let carbs = $state(0);
  let fat = $state(0);
  let servingSize = $state(100);
  let servingUnit = $state('g');
  let saving = $state(false);

  $effect(() => {
    if (!open) return;
    if (food) {
      name = food.name;
      brand = food.brand ?? '';
      calories = food.calories_per_serving;
      protein = food.protein_g;
      carbs = food.carbs_g;
      fat = food.fat_g;
      servingSize = food.serving_size;
      servingUnit = food.serving_unit;
    } else {
      name = '';
      brand = '';
      calories = 0;
      protein = 0;
      carbs = 0;
      fat = 0;
      servingSize = 100;
      servingUnit = 'g';
    }
  });

  const canSave = $derived(name.trim().length > 0 && servingSize > 0);

  async function handleSave() {
    if (!canSave || saving) return;
    saving = true;
    try {
      if (food) {
        await updateFoodItem(food.id, {
          name: name.trim(),
          brand: brand.trim() || undefined,
          calories_per_serving: Number(calories),
          protein_g: Number(protein),
          carbs_g: Number(carbs),
          fat_g: Number(fat),
          serving_size: Number(servingSize),
          serving_unit: servingUnit.trim() || 'g'
        });
      } else {
        await createFoodItem({
          name: name.trim(),
          brand: brand.trim() || undefined,
          barcode: initialBarcode || undefined,
          calories_per_serving: Number(calories),
          protein_g: Number(protein),
          carbs_g: Number(carbs),
          fat_g: Number(fat),
          serving_size: Number(servingSize),
          serving_unit: servingUnit.trim() || 'g'
        });
      }
      onSaved?.();
      onClose();
    } finally {
      saving = false;
    }
  }
</script>

<Modal
  {open}
  onclose={onClose}
  title={food
    ? 'Lebensmittel bearbeiten'
    : initialBarcode
      ? `Lebensmittel anlegen (Barcode: ${initialBarcode})`
      : 'Neues Lebensmittel'}
  subtitle="Nährwerte und Portionsangaben erfassen"
  icon="nutrition"
  size="md"
>
  <form
    onsubmit={(e) => {
      e.preventDefault();
      handleSave();
    }}
    class="space-y-4 text-xs"
  >
    {#if !food && initialBarcode}
      <div
        class="flex items-center gap-2 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3 py-2"
      >
        <Icon name="barcode_scanner" size="sm" class="text-[var(--color-primary)]" />
        <span class="text-xs text-[var(--text-muted)]">Barcode:</span>
        <span class="font-mono text-xs font-bold text-[var(--text-main)]">{initialBarcode}</span>
      </div>
    {/if}

    <Input
      label="Produktname"
      name="food_name"
      placeholder="z. B. Haferflocken"
      bind:value={name}
      required
    />

    <Input
      label="Marke / Hersteller"
      name="brand"
      placeholder="z. B. Alnatura, Kölln"
      bind:value={brand}
    />

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Input
        label="Portionsgröße"
        name="serving_size"
        type="number"
        bind:value={servingSize}
        min={1}
        required
      />
      <Input label="Einheit" name="serving_unit" placeholder="g oder ml" bind:value={servingUnit} />
    </div>

    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <Input
        label="Kalorien (kcal)"
        name="calories"
        type="number"
        bind:value={calories}
        step={0.1}
      />
      <Input label="Protein (g)" name="protein" type="number" bind:value={protein} step={0.1} />
      <Input label="Kohlenhydrate (g)" name="carbs" type="number" bind:value={carbs} step={0.1} />
      <Input label="Fett (g)" name="fat" type="number" bind:value={fat} step={0.1} />
    </div>

    <div class="flex justify-end gap-2 border-t border-[var(--border-subtle)] pt-3">
      <Btn variant="secondary" size="md" onclick={onClose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" type="submit" disabled={!canSave || saving} loading={saving}>
        {food ? 'Speichern' : 'Lebensmittel anlegen'}
      </Btn>
    </div>
  </form>
</Modal>
