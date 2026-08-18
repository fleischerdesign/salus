<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';

  let {
    data: _data = [],
    metricCode: _metricCode = '',
    unit: _unit = ''
  } = $props<{
    data?: unknown[];
    metricCode?: string;
    unit?: string;
  }>();

  let selectedRange = $state<'7D' | '30D' | '90D' | '1Y'>('30D');

  const points = [
    { date: '16. Jul', val: 83.2, ema: 83.4 },
    { date: '21. Jul', val: 82.8, ema: 83.1 },
    { date: '26. Jul', val: 82.5, ema: 82.7 },
    { date: '31. Jul', val: 82.9, ema: 82.6 },
    { date: '05. Aug', val: 82.2, ema: 82.4 },
    { date: '10. Aug', val: 81.9, ema: 82.1 },
    { date: '14. Aug', val: 81.8, ema: 82.0 }
  ];
</script>

<div
  class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
>
  <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
    <div>
      <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
        <Icon name="show-chart" class="text-[var(--color-primary)]" />
        <span>Körpergewicht und 7-Tage-EMA Glättung</span>
      </div>
      <p class="mt-0.5 text-xs text-[var(--text-muted)]">
        Trend: ↘ -1.4 kg / Monat • Zielkorridor: 78–80 kg
      </p>
    </div>

    <!-- Time Range Selector -->
    <div
      class="flex gap-1 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-1"
    >
      {#each ['7D', '30D', '90D', '1Y'] as const as r}
        <button
          type="button"
          onclick={() => (selectedRange = r)}
          class="cursor-pointer rounded-md px-2.5 py-1 text-xs font-bold transition-all {selectedRange ===
          r
            ? 'bg-[var(--color-primary)] text-white shadow-xs'
            : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        >
          {r}
        </button>
      {/each}
    </div>
  </div>

  <!-- SVG Chart Stage -->
  <div class="relative h-[220px] w-full">
    <svg class="h-full w-full overflow-visible" viewBox="0 0 700 200" preserveAspectRatio="none">
      <defs>
        <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.25" />
          <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0.0" />
        </linearGradient>
      </defs>

      <!-- Target Range Band (78 - 80 kg) -->
      <rect
        x="0"
        y="110"
        width="700"
        height="40"
        fill="var(--color-success)"
        opacity="0.08"
        rx="4"
      />
      <line
        x1="0"
        y1="110"
        x2="700"
        y2="110"
        stroke="var(--color-success)"
        stroke-dasharray="4 4"
        stroke-width="1"
        opacity="0.4"
      />
      <line
        x1="0"
        y1="150"
        x2="700"
        y2="150"
        stroke="var(--color-success)"
        stroke-dasharray="4 4"
        stroke-width="1"
        opacity="0.4"
      />

      <!-- Area fill -->
      <path
        d="M 20 50 L 120 75 L 220 90 L 320 70 L 420 105 L 520 120 L 620 125 L 620 180 L 20 180 Z"
        fill="url(#chartGradient)"
      />

      <!-- 7D EMA Line (Dashed) -->
      <path
        d="M 20 40 Q 120 60, 220 80 T 420 95 T 620 115"
        fill="none"
        stroke="var(--color-primary)"
        stroke-width="2"
        stroke-dasharray="6 4"
        opacity="0.6"
      />

      <!-- Actual Measurements Spline -->
      <path
        d="M 20 50 L 120 75 L 220 90 L 320 70 L 420 105 L 520 120 L 620 125"
        fill="none"
        stroke="var(--color-primary)"
        stroke-width="3"
      />

      <!-- Data Points -->
      {#each points as p, i}
        {@const x = 20 + i * 100}
        {@const y = 50 + (p.val - 83.2) * -40}
        <circle
          cx={x}
          cy={y}
          r="5"
          fill="var(--bg-surface-0)"
          stroke="var(--color-primary)"
          stroke-width="2.5"
          class="cursor-pointer transition-all hover:scale-125"
        />
      {/each}
    </svg>
  </div>

  <!-- X-Axis Labels -->
  <div
    class="mt-2 flex justify-between border-t border-[var(--border-subtle)] pt-2 font-mono text-[0.6875rem] text-[var(--text-muted)]"
  >
    {#each points as p}
      <span>{p.date}</span>
    {/each}
  </div>
</div>
