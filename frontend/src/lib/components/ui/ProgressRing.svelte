<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    value: number;
    max?: number;
    size?: number;
    strokeWidth?: number;
    color?: string;
    trackColor?: string;
    children?: Snippet;
    below?: Snippet;
  }

  let {
    value,
    max = 100,
    size = 120,
    strokeWidth = 8,
    color = 'var(--color-primary-500)',
    trackColor = 'var(--color-surface-100)',
    children,
    below
  }: Props = $props();

  const radius = $derived((size - strokeWidth) / 2);
  const circumference = $derived(2 * Math.PI * radius);
  const percent = $derived(max > 0 ? Math.min(Math.max(value / max, 0), 1) : 0);
  const dashOffset = $derived(circumference * (1 - percent));
  const center = $derived(size / 2);
</script>

<div class="flex flex-col items-center gap-2">
  <svg
    width={size}
    height={size}
    viewBox="0 0 {size} {size}"
    role="progressbar"
    aria-valuenow={value}
  >
    <circle
      cx={center}
      cy={center}
      r={radius}
      fill="none"
      stroke={trackColor}
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
    {#if children}
      <foreignObject x={0} y={0} width={size} height={size}>
        <div class="flex h-full w-full flex-col items-center justify-center">
          {@render children()}
        </div>
      </foreignObject>
    {/if}
  </svg>

  {#if below}
    {@render below()}
  {/if}
</div>
