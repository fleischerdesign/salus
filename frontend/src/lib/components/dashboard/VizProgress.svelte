<script lang="ts">
  interface Props {
    value: number;
    target?: number;
    unit?: string;
    color?: string;
    showPercent?: boolean;
    size?: number;
  }

  let {
    value,
    target,
    unit,
    color = 'var(--color-primary-500)',
    showPercent = true,
    size = 100
  }: Props = $props();

  const strokeWidth = 6;
  let radius = $derived((size - strokeWidth) / 2);
  let circumference = $derived(2 * Math.PI * radius);

  let percent = $derived(target && target > 0 ? Math.min(value / target, 1) : 0);
  let dashOffset = $derived(circumference * (1 - percent));
  let display = $derived(showPercent ? `${Math.round(percent * 100)}%` : `${value}`);
  let center = $derived(size / 2);
</script>

<div class="flex flex-col items-center gap-2">
  <svg width={size} height={size} viewBox="0 0 {size} {size}">
    <circle
      cx={center}
      cy={center}
      r={radius}
      fill="none"
      stroke="var(--color-surface-100)"
      stroke-width={strokeWidth}
    />
    <circle
      cx={center}
      cy={center}
      r={radius}
      fill="none"
      stroke={color}
      stroke-width={strokeWidth}
      stroke-linecap="round"
      stroke-dasharray={circumference}
      stroke-dashoffset={dashOffset}
      transform="rotate(-90 {center} {center})"
      style="transition: stroke-dashoffset var(--duration-slow) var(--ease-out)"
    />
    <text
      x={center}
      y={center}
      text-anchor="middle"
      dominant-baseline="central"
      class="fill-surface-900 text-sm font-bold"
    >
      {display}
    </text>
  </svg>

  {#if target}
    <span class="text-xs text-surface-400">
      of {target}{unit ? ` ${unit}` : ''}
    </span>
  {/if}
</div>
