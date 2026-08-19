<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Btn from '$components/ui/Btn.svelte';

  export interface ChartPoint {
    date: string;
    val: number;
    ema?: number;
  }

  interface Props {
    data?: ChartPoint[];
    metricName?: string;
    unit?: string;
    targetValue?: number | null;
    onaddclick?: () => void;
  }

  let {
    data = [],
    metricName = 'Messwert',
    unit = '',
    targetValue = null,
    onaddclick
  }: Props = $props();

  let selectedRange = $state<'7D' | '30D' | '90D' | '1Y'>('30D');

  const hasData = $derived(data.length > 0);

  // Scaled coordinates
  const chartBounds = $derived.by(() => {
    if (data.length === 0) return { min: 0, max: 100, range: 100 };
    const values = data.map((d) => d.val);
    if (targetValue != null) values.push(targetValue);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const pad = (max - min) * 0.15 || 5;
    return {
      min: Math.floor(min - pad),
      max: Math.ceil(max + pad),
      range: Math.max(1, Math.ceil(max + pad) - Math.floor(min - pad))
    };
  });

  function getY(val: number): number {
    const { min, range } = chartBounds;
    const ratio = (val - min) / range;
    return Math.round(180 - ratio * 140); // 40px top padding, 20px bottom
  }

  function getX(index: number, total: number): number {
    if (total <= 1) return 350;
    const step = 640 / (total - 1);
    return Math.round(30 + index * step);
  }

  const svgPath = $derived.by(() => {
    if (data.length === 0) return '';
    if (data.length === 1) return `M 30 ${getY(data[0].val)} L 670 ${getY(data[0].val)}`;
    return data
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i, data.length)} ${getY(p.val)}`)
      .join(' ');
  });

  const areaPath = $derived.by(() => {
    if (data.length === 0) return '';
    if (data.length === 1) return '';
    const firstX = getX(0, data.length);
    const lastX = getX(data.length - 1, data.length);
    return `${svgPath} L ${lastX} 190 L ${firstX} 190 Z`;
  });
</script>

<div class="rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card">
  <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
    <div>
      <div class="flex items-center gap-1.5 text-sm font-bold text-text-main">
        <Icon name="show-chart" class="text-primary" />
        <span>{metricName} Verlauf &amp; Trend</span>
      </div>
      <p class="mt-0.5 text-xs text-text-muted">
        {#if hasData}
          {data.length} Messpunkte im gewählten Zeitraum ({selectedRange})
        {:else}
          Keine Messdaten im ausgewählten Zeitraum vorhanden
        {/if}
      </p>
    </div>

    <!-- Time Range Selector -->
    <div class="flex gap-1 rounded-lg border border-border-subtle bg-surface-50 p-1">
      {#each ['7D', '30D', '90D', '1Y'] as const as r}
        <button
          type="button"
          onclick={() => (selectedRange = r)}
          class="cursor-pointer rounded-md px-2.5 py-1 text-xs font-bold transition-all {selectedRange ===
          r
            ? 'bg-primary text-white shadow-xs'
            : 'text-text-muted hover:text-text-main'}"
        >
          {r}
        </button>
      {/each}
    </div>
  </div>

  <!-- SVG Chart Stage -->
  <div class="relative flex h-[220px] w-full items-center justify-center overflow-hidden">
    {#if hasData}
      <svg class="h-full w-full overflow-visible" viewBox="0 0 700 200" preserveAspectRatio="none">
        <defs>
          <linearGradient id="metricChartGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.25" />
            <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0.0" />
          </linearGradient>
        </defs>

        <!-- Horizontal Baseline Grid Lines -->
        <line
          x1="20"
          y1="50"
          x2="680"
          y2="50"
          stroke="var(--border-subtle)"
          stroke-width="1"
          stroke-dasharray="3 3"
        />
        <line
          x1="20"
          y1="120"
          x2="680"
          y2="120"
          stroke="var(--border-subtle)"
          stroke-width="1"
          stroke-dasharray="3 3"
        />
        <line x1="20" y1="180" x2="680" y2="180" stroke="var(--border-subtle)" stroke-width="1" />

        <!-- Target Line (if targetValue is provided) -->
        {#if targetValue != null}
          {@const targetY = getY(targetValue)}
          <line
            x1="20"
            y1={targetY}
            x2="680"
            y2={targetY}
            stroke="var(--color-primary)"
            stroke-dasharray="4 4"
            stroke-width="1.5"
            opacity="0.75"
          />
          <text
            x="675"
            y={targetY - 5}
            text-anchor="end"
            class="fill-primary text-[10px] font-bold"
          >
            🎯 Ziel: {targetValue}
            {unit}
          </text>
        {/if}

        <!-- Area fill -->
        {#if areaPath}
          <path d={areaPath} fill="url(#metricChartGradient)" />
        {/if}

        <!-- Spline Line -->
        {#if svgPath}
          <path
            d={svgPath}
            fill="none"
            stroke="var(--color-primary)"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        {/if}

        <!-- Data Points -->
        {#each data as p, i}
          {@const x = getX(i, data.length)}
          {@const y = getY(p.val)}
          <circle
            cx={x}
            cy={y}
            r="4.5"
            fill="var(--bg-surface-0)"
            stroke="var(--color-primary)"
            stroke-width="2.5"
            class="cursor-pointer transition-all hover:scale-125"
          >
            <title>{p.date}: {p.val} {unit}</title>
          </circle>
        {/each}
      </svg>
    {:else}
      <!-- Pristine Empty Chart State -->
      <div class="flex flex-col items-center justify-center p-6 text-center">
        <div
          class="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-primary-soft text-primary"
        >
          <Icon name="monitoring" size="md" />
        </div>
        <p class="text-xs font-bold text-text-main">Noch kein Zeitreihen-Verlauf vorhanden</p>
        <p class="mt-0.5 max-w-xs text-[0.6875rem] text-text-muted">
          Sobald du Messwerte erfasst, zeichnet Salus hier deinen realen Längsschnitt-Trend und
          7-Tage-EMA ein.
        </p>
        {#if onaddclick}
          <div class="mt-3">
            <Btn variant="primary" size="sm" onclick={onaddclick}>+ Ersten Messwert erfassen</Btn>
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- X-Axis Labels -->
  {#if hasData}
    <div
      class="mt-2 flex justify-between border-t border-border-subtle pt-2 text-[0.6875rem] text-text-muted"
    >
      {#each data as p}
        <span class="truncate px-1">{p.date}</span>
      {/each}
    </div>
  {/if}
</div>
