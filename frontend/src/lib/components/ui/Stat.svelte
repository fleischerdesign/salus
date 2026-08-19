<script lang="ts">
  interface Props {
    value: string | number;
    unit?: string;
    label?: string;
    compact?: boolean;
    class?: string;
  }

  let { value, unit, label, compact = false, class: extraClass = '' }: Props = $props();
</script>

<div class="flex flex-col {compact ? '' : 'items-start gap-0.5'} {extraClass}">
  <div class="flex items-baseline gap-1">
    <span class="text-3xl leading-[36px] font-semibold text-surface-900 tabular-nums">
      {typeof value === 'number' ? value.toLocaleString() : value}
    </span>
    {#if unit}
      <span class="text-sm text-surface-500">{unit}</span>
    {/if}
  </div>
  {#if label}
    <span class="tracking-label text-xs font-semibold text-surface-500 uppercase">{label}</span>
  {/if}
</div>
