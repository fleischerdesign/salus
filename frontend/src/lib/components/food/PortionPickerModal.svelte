<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Stepper from '$components/ui/Stepper.svelte';
  import Input from '$components/ui/Input.svelte';
  import type { FoodItem } from '$lib/db/types';

  interface Props {
    food: FoodItem | null;
    onAdd: (food: FoodItem, servings: number) => void;
    onClose: () => void;
  }

  let { food, onAdd, onClose }: Props = $props();

  let servings = $state(1);

  $effect(() => {
    if (food) servings = 1;
  });

  const isWeightUnit = $derived(
    food ? ['g', 'ml', 'gramm', 'ml'].includes((food.serving_unit ?? '').toLowerCase()) : false
  );

  const amount = $derived(food ? Math.round(servings * (food.serving_size || 1) * 10) / 10 : 0);

  const macros = $derived.by(() => {
    if (!food) return null;
    return {
      calories: Math.round(food.calories_per_serving * servings),
      protein: Math.round(food.protein_g * servings * 10) / 10,
      carbs: Math.round(food.carbs_g * servings * 10) / 10,
      fat: Math.round(food.fat_g * servings * 10) / 10
    };
  });

  function handleAmountInput(e: Event) {
    const value = parseFloat((e.target as HTMLInputElement).value);
    if (!food || !food.serving_size || Number.isNaN(value)) return;
    servings = Math.max(0.05, value / food.serving_size);
  }
</script>

<Modal open={Boolean(food)} onclose={onClose} title={food?.name ?? ''} size="sm">
  {#if food}
    <div class="flex flex-col gap-5">
      <div class="bg-surface-50 flex items-end justify-between rounded-xl px-4 py-3">
        <div>
          <div class="text-surface-900 text-3xl font-bold tabular-nums">
            {macros ? macros.calories.toLocaleString() : '—'}
            <span class="text-surface-400 text-base font-medium"> kcal</span>
          </div>
          <div class="text-surface-500 mt-1 text-xs">
            {#if macros}
              {macros.protein}P · {macros.carbs}C · {macros.fat}F
            {/if}
          </div>
        </div>
        <div class="text-surface-400 text-right text-xs">
          <span class="text-surface-700 text-sm font-semibold tabular-nums">{amount}</span>
          {food.serving_unit}
        </div>
      </div>

      <div class="flex items-center justify-between gap-4">
        <Stepper name="servings" label="Servings" min={0.25} step={0.5} bind:value={servings} />
        {#if isWeightUnit}
          <div class="w-36">
            <Input
              name="amount"
              label={`Amount (${food.serving_unit})`}
              type="number"
              min={0}
              step={10}
              value={amount}
              oninput={handleAmountInput}
            />
          </div>
        {/if}
      </div>

      <div
        class="border-surface-100 bg-surface-50 text-surface-500 rounded-lg border px-3 py-2 text-xs"
      >
        1 serving = {food.serving_size}
        {food.serving_unit} ·{' '}
        {Math.round(food.calories_per_serving)} kcal
      </div>

      <div class="flex justify-end gap-3 pt-2">
        <Btn variant="ghost" onclick={onClose}>Cancel</Btn>
        <Btn variant="primary" onclick={() => onAdd(food, servings)}>Add to meal</Btn>
      </div>
    </div>
  {/if}
</Modal>
