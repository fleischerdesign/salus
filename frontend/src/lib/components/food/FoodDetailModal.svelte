<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import type { FoodItem } from '$lib/db/types';

  interface Props {
    food: FoodItem | null;
    onAddToMeal?: (food: FoodItem) => void;
    onEdit?: (food: FoodItem) => void;
    onDelete?: (food: FoodItem) => void;
    onClose: () => void;
  }

  let { food, onAddToMeal, onEdit, onDelete, onClose }: Props = $props();

  const isOwn = $derived(Boolean(food?.user_id));

  const macroRows = $derived(
    food
      ? [
          { label: 'Protein', value: food.protein_g, unit: 'g' },
          { label: 'Carbs', value: food.carbs_g, unit: 'g' },
          { label: 'Fat', value: food.fat_g, unit: 'g' },
          { label: 'Fiber', value: food.fiber_g, unit: 'g', optional: true },
          { label: 'Sugar', value: food.sugar_g, unit: 'g', optional: true }
        ]
      : []
  );
</script>

<Modal open={Boolean(food)} onclose={onClose} title={food?.name ?? ''} size="md">
  {#if food}
    <div class="flex flex-col gap-5">
      <div class="flex items-center justify-between">
        <div class="min-w-0">
          {#if food.brand}
            <p class="text-sm text-surface-400">{food.brand}</p>
          {/if}
          <div class="mt-1 flex items-center gap-2">
            {#if food.is_verified}
              <Badge variant="success">Verified</Badge>
            {:else if isOwn}
              <Badge variant="default">Custom</Badge>
            {/if}
            {#if food.barcode}
              <span class="font-mono text-xs text-surface-400">{food.barcode}</span>
            {/if}
          </div>
        </div>
        <div class="flex flex-shrink-0 gap-1">
          {#if isOwn && onEdit}
            <button
              type="button"
              class="flex h-8 w-8 items-center justify-center rounded-lg text-surface-400 hover:bg-surface-100 hover:text-primary-600"
              aria-label="Edit food"
              onclick={() => onEdit(food)}
            >
              <Icon name="edit" size="sm" />
            </button>
          {/if}
          {#if isOwn && onDelete}
            <button
              type="button"
              class="flex h-8 w-8 items-center justify-center rounded-lg text-surface-400 hover:bg-surface-100 hover:text-error-500"
              aria-label="Delete food"
              onclick={() => onDelete(food)}
            >
              <Icon name="delete" size="sm" />
            </button>
          {/if}
        </div>
      </div>

      <div class="flex items-end justify-between rounded-xl bg-surface-50 px-4 py-3">
        <div>
          <div class="text-3xl font-bold text-surface-900 tabular-nums">
            {Math.round(food.calories_per_serving)}
          </div>
          <div class="text-xs text-surface-400">kcal per serving</div>
        </div>
        <div class="text-right text-xs text-surface-500">
          <span class="text-sm font-semibold text-surface-800 tabular-nums">
            {food.serving_size}
          </span>
          {food.serving_unit}
        </div>
      </div>

      <div>
        <h3 class="mb-2 text-xs font-semibold tracking-wider text-surface-400 uppercase">Macros</h3>
        <div class="grid grid-cols-2 gap-2">
          {#each macroRows as row}
            {#if !row.optional || row.value != null}
              <div
                class="flex items-center justify-between rounded-lg border border-surface-100 bg-surface-50 px-3 py-2"
              >
                <span class="text-xs text-surface-500">{row.label}</span>
                <span class="text-sm font-semibold text-surface-800 tabular-nums">
                  {row.value != null ? Math.round(row.value) : '—'}{row.value != null
                    ? row.unit
                    : ''}
                </span>
              </div>
            {/if}
          {/each}
        </div>
      </div>

      <div class="flex justify-end gap-3 border-t border-surface-100 pt-4">
        <Btn variant="ghost" onclick={onClose}>Close</Btn>
        {#if onAddToMeal}
          <Btn variant="primary" onclick={() => onAddToMeal(food)}>
            <Icon name="restaurant" size="sm" />
            Add to Meal
          </Btn>
        {/if}
      </div>
    </div>
  {/if}
</Modal>
