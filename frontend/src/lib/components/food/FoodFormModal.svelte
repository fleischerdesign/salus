<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import FormField from '$components/forms/FormField.svelte';
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

  const canSave = $derived(name.trim().length > 0);

  async function handleSave() {
    if (!canSave) return;
    saving = true;
    try {
      const payload = {
        name: name.trim(),
        brand: brand.trim() || undefined,
        calories_per_serving: calories,
        protein_g: protein,
        carbs_g: carbs,
        fat_g: fat,
        serving_size: servingSize,
        serving_unit: servingUnit.trim() || 'g'
      };
      if (food) {
        await updateFoodItem(food.id ?? '', payload);
      } else {
        await createFoodItem({ ...payload, barcode: initialBarcode ?? undefined });
      }
      onClose();
      onSaved?.();
    } finally {
      saving = false;
    }
  }
</script>

<Modal
  {open}
  onclose={onClose}
  title={food
    ? 'Edit Food Item'
    : initialBarcode
      ? `Create Food (barcode ${initialBarcode})`
      : 'New Food Item'}
  size="md"
>
  <div class="flex flex-col gap-4">
    {#if !food && initialBarcode}
      <div
        class="flex items-center gap-2 rounded-lg border border-surface-200 bg-surface-50 px-3 py-2"
      >
        <Icon name="info" size="sm" class="text-surface-400" />
        <span class="text-xs text-surface-500">Barcode</span>
        <span class="font-mono text-xs font-medium text-surface-800">{initialBarcode}</span>
      </div>
    {/if}

    <FormField label="Name" required>
      <Input name="food_name" placeholder="e.g. Haferflocken" bind:value={name} />
    </FormField>
    <FormField label="Brand">
      <Input name="brand" placeholder="e.g. Alnatura" bind:value={brand} />
    </FormField>
    <div class="grid grid-cols-2 gap-4">
      <FormField label="Serving Size">
        <Input name="serving_size" type="number" bind:value={servingSize} min={1} />
      </FormField>
      <FormField label="Unit">
        <Input name="serving_unit" placeholder="g" bind:value={servingUnit} />
      </FormField>
    </div>
    <div class="grid grid-cols-2 gap-4">
      <FormField label="Calories (per serving)">
        <Input name="calories" type="number" bind:value={calories} step={0.1} />
      </FormField>
      <FormField label="Protein (g)">
        <Input name="protein" type="number" bind:value={protein} step={0.1} />
      </FormField>
      <FormField label="Carbs (g)">
        <Input name="carbs" type="number" bind:value={carbs} step={0.1} />
      </FormField>
      <FormField label="Fat (g)">
        <Input name="fat" type="number" bind:value={fat} step={0.1} />
      </FormField>
    </div>
    <div class="flex justify-end gap-3 pt-2">
      <Btn variant="ghost" onclick={onClose}>Cancel</Btn>
      <Btn variant="primary" onclick={handleSave} disabled={!canSave || saving}>
        {saving ? 'Saving...' : food ? 'Save' : 'Create'}
      </Btn>
    </div>
  </div>
</Modal>
