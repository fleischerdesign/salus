<script lang="ts">
  interface Props {
    value: string | number;
    unit?: string;
    points?: string;
    color?: string;
    fillColor?: string;
    width?: number;
    height?: number;
  }

  let {
    value,
    unit,
    points,
    color = 'var(--color-primary-500)',
    fillColor,
    width = 200,
    height = 60
  }: Props = $props();

  const gradientId = `sparkline-fill-${Math.random().toString(36).slice(2, 9)}`;
  let resolvedFill = $derived(fillColor ?? 'var(--color-primary-100)');
</script>

<div class="flex items-center gap-3">
  <div class="flex items-baseline gap-1">
    <span class="text-lg font-bold text-surface-900">{value}</span>
    {#if unit}
      <span class="text-xs text-surface-400">{unit}</span>
    {/if}
  </div>

  {#if points}
    <svg
      class="ml-auto"
      width={width}
      height={height}
      viewBox="0 0 {width} {height}"
      preserveAspectRatio="none"
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color={color} stop-opacity="0.3" />
          <stop offset="100%" stop-color={color} stop-opacity="0.02" />
        </linearGradient>
      </defs>

      <polygon
        fill={`url(#${gradientId})`}
        points="0,{height} {points} {width},{height}"
      />

      <polyline
        fill="none"
        stroke={color}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        points={points}
      />
    </svg>
  {/if}
</div>
