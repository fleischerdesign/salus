<script lang="ts">
  interface Candle {
    label: string;
    open: number;
    high: number;
    low: number;
    close: number;
  }

  interface Props {
    data?: Candle[];
    color?: string;
    width?: number;
    height?: number;
  }

  let {
    data = [],
    color = 'var(--color-primary-500)',
    width = 260,
    height = 80
  }: Props = $props();

  const padLeft = 4;
  const padRight = 4;
  const axisHeight = 16;
  let chartW = $derived(width - padLeft - padRight);
  let chartH = $derived(height - axisHeight);
  let barW = $derived(Math.max(2, Math.min(8, chartW / (data.length * 2 + 1))));
  let gap = $derived(barW);

  let allValues = $derived(data.flatMap((d) => [d.high, d.low]));
  let min = $derived(allValues.length > 0 ? Math.min(...allValues) : 0);
  let max = $derived(allValues.length > 0 ? Math.max(...allValues) : 100);
  let range = $derived(max - min || 1);

  function y(val: number): number {
    return chartH - ((val - min) / range) * chartH;
  }

  function candleColor(c: Candle): string {
    if (c.close > c.open) return color;
    if (c.close < c.open) return 'var(--color-error-500)';
    return 'var(--color-surface-400)';
  }
</script>

<div class="flex flex-col gap-1">
  <svg width={width} height={height} viewBox="0 0 {width} {height}">
    {#each data as candle, i}
      {@const cx = padLeft + i * (barW + gap) + barW / 2}
      {@const isBullish = candle.close >= candle.open}
      {@const bodyTop = y(Math.max(candle.open, candle.close))}
      {@const bodyH = Math.max(1, Math.abs(y(candle.open) - y(candle.close)))}

      <line
        x1={cx}
        y1={y(candle.high)}
        x2={cx}
        y2={y(candle.low)}
        stroke={candleColor(candle)}
        stroke-width="1"
      />

      <rect
        x={padLeft + i * (barW + gap)}
        y={bodyTop}
        width={barW}
        height={bodyH}
        rx="1"
        fill={isBullish ? candleColor(candle) : 'transparent'}
        stroke={candleColor(candle)}
        stroke-width="1"
      />

      <text
        x={cx}
        y={height - 2}
        text-anchor="middle"
        class="fill-surface-400 text-[8px]"
      >
        {candle.label}
      </text>
    {/each}
  </svg>
</div>
