<script lang="ts">
  import { tweened } from 'svelte/motion';
  import { DURATIONS, EASINGS } from '$lib/utils/motion';
  import Icon from '$components/ui/Icon.svelte';

  interface Delta {
    value: string;
    direction: 'up' | 'down' | 'neutral';
    isGood?: boolean;
  }

  interface Props {
    value: string | number;
    unit?: string;
    delta?: Delta;
    subLabel?: string;
    color?: string;
    animate?: boolean;
  }

  let {
    value,
    unit,
    delta,
    subLabel,
    color = 'var(--color-surface-900)',
    animate = false
  }: Props = $props();

  let numValue = $derived(typeof value === 'number' ? value : parseFloat(String(value)));
  let isNumeric = $derived(!isNaN(numValue));

  const animVal = tweened(0, { duration: DURATIONS.slow, easing: EASINGS.out });
  let displayValue = $derived(
    animate && isNumeric ? String(Math.round($animVal * 10) / 10) : String(value)
  );

  $effect(() => {
    if (animate && isNumeric) {
      animVal.set(numValue, { duration: DURATIONS.slow, easing: EASINGS.out });
    }
  });

  function deltaColor(d: Delta): string {
    if (d.direction === 'neutral') return 'var(--color-surface-400)';
    if (d.isGood === undefined)
      return d.direction === 'up' ? 'var(--color-success-500)' : 'var(--color-error-500)';
    const good = d.isGood;
    if (d.direction === 'up') return good ? 'var(--color-success-500)' : 'var(--color-error-500)';
    return good ? 'var(--color-error-500)' : 'var(--color-success-500)';
  }

  function deltaIcon(d: Delta): string {
    if (d.direction === 'up') return 'trending-up';
    if (d.direction === 'down') return 'trending-down';
    return 'trending-flat';
  }
</script>

<div class="flex flex-col gap-1">
  <div class="flex items-baseline gap-1.5">
    <span class="text-3xl font-bold" style="color: {color}">{displayValue}</span>
    {#if unit}
      <span class="text-sm text-surface-400">{unit}</span>
    {/if}
  </div>

  {#if delta}
    {@const dc = deltaColor(delta)}
    <div class="flex items-center gap-1" style="color: {dc}">
      <Icon name={deltaIcon(delta)} size="sm" />
      <span class="text-xs font-medium">{delta.value}</span>
    </div>
  {/if}

  {#if subLabel}
    <span class="text-xs text-surface-400">{subLabel}</span>
  {/if}
</div>
