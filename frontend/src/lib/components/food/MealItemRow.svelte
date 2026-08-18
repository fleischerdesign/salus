<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    name: string;
    servings: number;
    servingSize: number;
    servingUnit: string;
    calories: number;
    proteinG: number;
    carbsG: number;
    fatG: number;
    onRemove: () => void;
    onIncrement: () => void;
    onDecrement: () => void;
    onViewFood?: () => void;
  }

  let {
    name,
    servings,
    servingSize,
    servingUnit,
    calories,
    proteinG,
    carbsG,
    fatG,
    onRemove,
    onIncrement,
    onDecrement,
    onViewFood
  }: Props = $props();

  const quantity = $derived(Math.round(servings * servingSize * 10) / 10);
</script>

<div class="bg-surface-50 flex items-center justify-between rounded-lg px-3 py-2">
  <div class="min-w-0 flex-1">
    {#if onViewFood}
      <button
        type="button"
        onclick={onViewFood}
        class="text-surface-800 hover:text-primary-600 block max-w-full truncate text-left text-sm font-medium"
      >
        {name}
      </button>
    {:else}
      <div class="text-surface-800 truncate text-sm font-medium">{name}</div>
    {/if}
    <div class="text-surface-400 text-xs">
      {quantity}
      {servingUnit} · {Math.round(calories)} kcal · {Math.round(proteinG)}P ·{' '}
      {Math.round(carbsG)}C · {Math.round(fatG)}F
    </div>
  </div>

  <div class="ml-3 flex flex-shrink-0 items-center gap-2">
    <button
      onclick={onDecrement}
      disabled={servings <= 0.25}
      class="border-surface-200 text-surface-400 hover:bg-surface-100 flex h-7 w-7 items-center justify-center rounded-full border disabled:opacity-30"
    >
      <Icon name="remove" size="sm" />
    </button>
    <span class="text-surface-700 w-8 text-center text-sm font-medium tabular-nums">{servings}</span
    >
    <button
      onclick={onIncrement}
      class="border-surface-200 text-surface-400 hover:bg-surface-100 flex h-7 w-7 items-center justify-center rounded-full border"
    >
      <Icon name="add" size="sm" />
    </button>
    <button
      onclick={onRemove}
      class="text-surface-400 hover:bg-surface-100 hover:text-error-500 flex h-7 w-7 items-center justify-center rounded"
    >
      <Icon name="close" size="sm" />
    </button>
  </div>
</div>
