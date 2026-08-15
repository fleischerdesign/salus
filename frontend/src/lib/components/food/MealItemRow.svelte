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

<div class="flex items-center justify-between rounded-lg bg-surface-50 px-3 py-2">
  <div class="min-w-0 flex-1">
    {#if onViewFood}
      <button
        type="button"
        onclick={onViewFood}
        class="block max-w-full truncate text-left text-sm font-medium text-surface-800 hover:text-primary-600"
      >
        {name}
      </button>
    {:else}
      <div class="truncate text-sm font-medium text-surface-800">{name}</div>
    {/if}
    <div class="text-xs text-surface-400">
      {quantity}
      {servingUnit} · {Math.round(calories)} kcal · {Math.round(proteinG)}P ·{' '}
      {Math.round(carbsG)}C · {Math.round(fatG)}F
    </div>
  </div>

  <div class="ml-3 flex flex-shrink-0 items-center gap-2">
    <button
      onclick={onDecrement}
      disabled={servings <= 0.25}
      class="flex h-7 w-7 items-center justify-center rounded-full border border-surface-200 text-surface-400 hover:bg-surface-100 disabled:opacity-30"
    >
      <Icon name="remove" size="sm" />
    </button>
    <span class="w-8 text-center text-sm font-medium text-surface-700 tabular-nums">{servings}</span
    >
    <button
      onclick={onIncrement}
      class="flex h-7 w-7 items-center justify-center rounded-full border border-surface-200 text-surface-400 hover:bg-surface-100"
    >
      <Icon name="add" size="sm" />
    </button>
    <button
      onclick={onRemove}
      class="flex h-7 w-7 items-center justify-center rounded text-surface-400 hover:bg-surface-100 hover:text-error-500"
    >
      <Icon name="close" size="sm" />
    </button>
  </div>
</div>
