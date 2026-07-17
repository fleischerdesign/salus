<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import type { MedicationInventory } from '$lib/db/types';

  interface Props {
    inventory: MedicationInventory | null;
    onUpdate: (data: {
      initial_count: number;
      remaining_count: number;
      refill_at_count: number;
    }) => void;
  }

  let { inventory, onUpdate }: Props = $props();

  let remaining = $state(inventory?.remaining_count ?? 0);
  let initial = $state(inventory?.initial_count ?? 0);
  let refillAt = $state(inventory?.refill_at_count ?? 0);

  $effect(() => {
    if (inventory) {
      remaining = inventory.remaining_count;
      initial = inventory.initial_count;
      refillAt = inventory.refill_at_count;
    }
  });

  const percentage = $derived(initial > 0 ? Math.round((remaining / initial) * 100) : 0);
  const needsRefill = $derived(remaining <= refillAt);
  const progressColor = $derived(
    needsRefill ? 'bg-error-500' : percentage > 50 ? 'bg-success-500' : 'bg-amber-500'
  );

  function handleDecrement() {
    if (remaining > 0) {
      remaining--;
      onUpdate({ initial_count: initial, remaining_count: remaining, refill_at_count: refillAt });
    }
  }

  function handleIncrement() {
    remaining++;
    onUpdate({ initial_count: initial, remaining_count: remaining, refill_at_count: refillAt });
  }
</script>

<div class="rounded-lg border border-surface-200 p-4">
  <div class="mb-3 flex items-center justify-between">
    <h3 class="text-sm font-semibold text-surface-700">Inventory</h3>
    {#if needsRefill}
      <span
        class="flex items-center gap-1 rounded-full bg-error-50 px-2 py-0.5 text-xs font-medium text-error-600"
      >
        <Icon name="warning" size="sm" />
        Refill needed
      </span>
    {/if}
  </div>

  <div class="mb-2">
    <div class="mb-1 flex justify-between text-xs text-surface-500">
      <span>{remaining} remaining</span>
      <span>{percentage}%</span>
    </div>
    <div class="h-2 w-full overflow-hidden rounded-full bg-surface-100">
      <div
        class="h-full rounded-full transition-all {progressColor}"
        style="width: {percentage}%"
      ></div>
    </div>
  </div>

  <div class="flex items-center gap-3">
    <button
      onclick={handleDecrement}
      class="flex h-8 w-8 items-center justify-center rounded-full border border-surface-200 text-surface-500 hover:bg-surface-100 disabled:opacity-30"
      disabled={remaining <= 0}
    >
      <Icon name="remove" size="sm" />
    </button>
    <span class="text-lg font-bold text-surface-800 tabular-nums">{remaining}</span>
    <button
      onclick={handleIncrement}
      class="flex h-8 w-8 items-center justify-center rounded-full border border-surface-200 text-surface-500 hover:bg-surface-100"
    >
      <Icon name="add" size="sm" />
    </button>
    <span class="text-xs text-surface-400">of {initial}</span>
  </div>

  <div class="mt-3 text-xs text-surface-400">
    Refill warning at {refillAt} remaining
  </div>
</div>
