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

  let remaining = $state(0);
  let initial = $state(0);
  let refillAt = $state(0);

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
    needsRefill ? 'bg-error-500' : percentage > 50 ? 'bg-success-500' : 'bg-warning-500'
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

<div class="border-surface-200 rounded-lg border p-4">
  <div class="mb-3 flex items-center justify-between">
    <h3 class="text-surface-700 text-sm font-semibold">Inventory</h3>
    {#if needsRefill}
      <span
        class="bg-error-50 text-error-600 flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium"
      >
        <Icon name="warning" size="sm" />
        Refill needed
      </span>
    {/if}
  </div>

  <div class="mb-2">
    <div class="text-surface-500 mb-1 flex justify-between text-xs">
      <span>{remaining} remaining</span>
      <span>{percentage}%</span>
    </div>
    <div class="bg-surface-100 h-2 w-full overflow-hidden rounded-full">
      <div
        class="h-full rounded-full transition-all {progressColor}"
        style="width: {percentage}%"
      ></div>
    </div>
  </div>

  <div class="flex items-center gap-3">
    <button
      onclick={handleDecrement}
      class="border-surface-200 text-surface-500 hover:bg-surface-100 flex h-8 w-8 items-center justify-center rounded-full border disabled:opacity-30"
      disabled={remaining <= 0}
    >
      <Icon name="remove" size="sm" />
    </button>
    <span class="text-surface-800 text-lg font-bold tabular-nums">{remaining}</span>
    <button
      onclick={handleIncrement}
      class="border-surface-200 text-surface-500 hover:bg-surface-100 flex h-8 w-8 items-center justify-center rounded-full border"
    >
      <Icon name="add" size="sm" />
    </button>
    <span class="text-surface-400 text-xs">of {initial}</span>
  </div>

  <div class="text-surface-400 mt-3 text-xs">
    Refill warning at {refillAt} remaining
  </div>
</div>
