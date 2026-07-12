<script lang="ts">
  import Icon from './Icon.svelte';

  interface Props {
    value: string | number;
    unit?: string;
    label?: string;
    compact?: boolean;
    class?: string;
  }

  let {
    value,
    unit,
    label,
    compact = false,
    class: extraClass = ''
  }: Props = $props();
</script>

<div class="flex flex-col {compact ? '' : 'items-start gap-0.5'} {extraClass}">
  <div class="flex items-baseline gap-1">
    <span class="text-[28px] font-semibold leading-[36px] text-surface-900 tabular-nums">
      {typeof value === 'number' ? value.toLocaleString() : value}
    </span>
    {#if unit}
      <span class="text-sm text-surface-500">{unit}</span>
    {/if}
  </div>
  {#if label}
    <span class="text-[13px] font-semibold uppercase tracking-[0.05em] text-surface-500">{label}</span>
  {/if}
</div>
