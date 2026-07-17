<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Card from '$components/ui/Card.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import CheckCircle from '$components/ui/CheckCircle.svelte';
  import { goto } from '$app/navigation';
  import type { Medication } from '$lib/db/types';

  interface Props {
    medication: Medication;
    nextDose: string | null;
    adherenceRate: number;
    onToggle: () => void;
  }

  let { medication, nextDose, adherenceRate, onToggle }: Props = $props();

  let toggling = $state(false);

  const formLabel = $derived(
    medication.form ? medication.form.charAt(0).toUpperCase() + medication.form.slice(1) : ''
  );

  const ratePercent = $derived(Math.round(adherenceRate * 100));

  async function handleToggle() {
    toggling = true;
    try {
      await onToggle();
    } finally {
      toggling = false;
    }
  }

  function navigateToDetail() {
    goto('/medications/' + medication.id);
  }
</script>

<div
  class="group block cursor-pointer"
  onclick={navigateToDetail}
  onkeydown={(e) => {
    if (e.key === 'Enter') navigateToDetail();
  }}
  role="link"
  tabindex="0"
>
  <Card hoverable padding={false}>
    <div class="p-4 pb-2">
      <div class="flex items-start gap-3">
        <div
          class="duration-micro flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-white transition-all"
          style="background-color: {medication.color_hex}"
        >
          <Icon name={medication.icon} size="md" />
        </div>

        <div class="min-w-0 flex-1 pt-0.5">
          <div class="font-semibold text-surface-900">{medication.name}</div>
          <div class="truncate text-xs text-surface-500">
            {#if medication.strength}
              {medication.strength}
            {/if}
            {#if medication.strength && formLabel}
              ·
            {/if}
            {formLabel}
          </div>
        </div>

        {#if ratePercent > 0}
          <Badge variant="default" class="mt-0.5 flex-shrink-0 text-[10px]">{ratePercent}%</Badge>
        {/if}
      </div>
    </div>

    <div class="border-t border-surface-100"></div>

    <div class="flex items-center justify-between px-4 py-2.5">
      <div class="flex items-center gap-1.5 text-xs text-surface-500">
        {#if nextDose}
          <Icon name="schedule" size="sm" />
          <span class="font-medium text-surface-600">{nextDose}</span>
        {:else}
          <span class="text-surface-400">As needed</span>
        {/if}
      </div>

      {#if nextDose}
        <CheckCircle checked={false} disabled={toggling} onchange={handleToggle} />
      {:else}
        <button
          onclick={(e) => {
            e.stopPropagation();
            handleToggle();
          }}
          disabled={toggling}
          class="rounded-full px-3 py-1 text-xs font-medium text-white transition-opacity hover:opacity-80 disabled:opacity-50"
          style="background-color: {medication.color_hex}"
        >
          Take now
        </button>
      {/if}
    </div>
  </Card>
</div>
