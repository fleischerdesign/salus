<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    name: string;
    servings: number;
    amountG: number | null;
    calories: number;
    proteinG: number;
    carbsG: number;
    fatG: number;
    onRemove: () => void;
    onIncrement: () => void;
    onDecrement: () => void;
  }

  let {
    name,
    servings,
    amountG,
    calories,
    proteinG,
    carbsG,
    fatG,
    onRemove,
    onIncrement,
    onDecrement
  }: Props = $props();
</script>

<div class="flex items-center justify-between rounded-lg bg-surface-50 px-3 py-2">
  <div class="flex-1 min-w-0">
    <div class="text-sm font-medium text-surface-800 truncate">{name}</div>
    <div class="text-xs text-surface-400">
      {Math.round(calories)} kcal · {Math.round(proteinG)}P · {Math.round(carbsG)}C · {Math.round(fatG)}F
      {#if amountG}
        · {Math.round(amountG * servings)}g
      {/if}
    </div>
  </div>

  <div class="flex items-center gap-2 flex-shrink-0 ml-3">
    <button
      onclick={onDecrement}
      disabled={servings <= 0.25}
      class="flex h-7 w-7 items-center justify-center rounded-full border border-surface-200 text-surface-400 hover:bg-surface-100 disabled:opacity-30"
    >
      <Icon name="remove" size="sm" />
    </button>
    <span class="w-8 text-center text-sm font-medium tabular-nums text-surface-700">{servings}</span>
    <button
      onclick={onIncrement}
      class="flex h-7 w-7 items-center justify-center rounded-full border border-surface-200 text-surface-400 hover:bg-surface-100"
    >
      <Icon name="add" size="sm" />
    </button>
    <button onclick={onRemove} class="flex h-7 w-7 items-center justify-center rounded text-surface-400 hover:bg-surface-100 hover:text-error-500">
      <Icon name="close" size="sm" />
    </button>
  </div>
</div>
