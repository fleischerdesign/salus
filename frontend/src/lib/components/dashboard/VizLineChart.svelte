<script lang="ts">
  interface ChartSeries {
    label: string;
    data: number[];
    color: string;
    yAxis?: 'left' | 'right';
  }

  interface Props {
    labels: string[];
    series: ChartSeries[];
    height?: number;
    unit?: string;
  }

  let { labels, series, height = 160, unit }: Props = $props();

  const padLeft = 40;
  const padRight = 10;
  const padTop = 8;
  const padBottom = 20;
  const tickCount = 3;

  let width = $state(560);
  let containerEl: HTMLDivElement | null = $state(null);

  const chartW = $derived(width - padLeft - padRight);
  const chartH = $derived(height - padTop - padBottom);

  function niceScale(data: number[]): { min: number; max: number; step: number } {
    if (data.length === 0) return { min: 0, max: 1, step: 0.5 };
    const rawMin = Math.min(...data);
    const rawMax = Math.max(...data);
    if (rawMin === rawMax) {
      return { min: rawMin - 5, max: rawMax + 5, step: 5 };
    }
    const range = rawMax - rawMin;
    const mag = Math.pow(10, Math.floor(Math.log10(range)));
    const norm = range / mag;
    let step: number;
    if (norm <= 1.5) step = 0.25 * mag;
    else if (norm <= 3) step = 0.5 * mag;
    else if (norm <= 7) step = 1 * mag;
    else step = 2 * mag;
    const min = Math.floor(rawMin / step) * step;
    const max = Math.ceil(rawMax / step) * step;
    return { min, max, step };
  }

  const allData = $derived(series.flatMap((s) => s.data));
  const scale = $derived(niceScale(allData));

  function scaleY(v: number): number {
    const range = scale.max - scale.min || 1;
    return padTop + chartH - ((v - scale.min) / range) * chartH;
  }

  function scaleX(i: number): number {
    if (labels.length <= 1) return padLeft;
    return padLeft + (i / (labels.length - 1)) * chartW;
  }

  function buildPath(data: number[]): string {
    if (data.length === 0) return '';
    return data
      .map((v, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(i).toFixed(1)} ${scaleY(v).toFixed(1)}`)
      .join(' ');
  }

  function buildArea(data: number[]): string {
    if (data.length === 0) return '';
    const path = buildPath(data);
    const lastX = scaleX(data.length - 1);
    const baseY = padTop + chartH;
    return `${path} L ${lastX.toFixed(1)} ${baseY.toFixed(1)} L ${padLeft.toFixed(1)} ${baseY.toFixed(1)} Z`;
  }

  const ticks = $derived.by(() => {
    const ts: number[] = [];
    for (let i = 0; i <= tickCount; i++) {
      ts.push(scale.min + (i / tickCount) * (scale.max - scale.min));
    }
    return ts;
  });

  const labelStep = $derived(labels.length > 10 ? Math.ceil(labels.length / 6) : 1);

  const gradientId = `vizlc-grad-${Math.random().toString(36).slice(2, 9)}`;

  const ro = new ResizeObserver((entries) => {
    for (const entry of entries) {
      width = entry.contentRect.width;
    }
  });

  $effect(() => {
    if (containerEl) {
      width = containerEl.clientWidth;
      ro.observe(containerEl);
      return () => ro.disconnect();
    }
  });
</script>

<div bind:this={containerEl} class="relative w-full">
  <svg {width} {height} viewBox="0 0 {width} {height}" preserveAspectRatio="none">
    <defs>
      {#each series as s, i}
        <linearGradient id="{gradientId}-{i}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color={s.color} stop-opacity="0.15" />
          <stop offset="100%" stop-color={s.color} stop-opacity="0.01" />
        </linearGradient>
      {/each}
    </defs>

    {#each ticks as tick}
      {@const y = scaleY(tick)}
      <line
        x1={padLeft}
        y1={y}
        x2={width - padRight}
        y2={y}
        stroke="var(--color-surface-100)"
        stroke-width="1"
      />
      <text
        x={padLeft - 6}
        y={y + 4}
        text-anchor="end"
        class="fill-surface-400 text-[10px] tabular-nums"
      >
        {tick >= 1000 ? (tick / 1000).toFixed(1) + 'k' : tick.toFixed(tick % 1 === 0 ? 0 : 1)}
      </text>
    {/each}

    {#if unit}
      <text
        x={padLeft + chartW / 2}
        y={padTop + 8}
        text-anchor="middle"
        class="fill-surface-400 text-[10px] font-medium"
      >
        {unit}
      </text>
    {/if}

    {#each labels as label, i}
      {#if i % labelStep === 0 || i === labels.length - 1}
        <text x={scaleX(i)} y={height - 4} text-anchor="middle" class="fill-surface-400 text-[9px]">
          {label}
        </text>
      {/if}
    {/each}

    {#each series as s, i}
      <path d={buildArea(s.data)} fill="url(#{gradientId}-{i})" />
      <path
        d={buildPath(s.data)}
        fill="none"
        stroke={s.color}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    {/each}
  </svg>

  <div class="mt-1.5 flex flex-wrap items-center justify-center gap-x-4 gap-y-0.5">
    {#each series as s}
      <div class="flex items-center gap-1.5">
        <span class="inline-block h-2 w-2 rounded-full" style="background-color: {s.color}"></span>
        <span class="text-[11px] text-surface-500">{s.label}</span>
      </div>
    {/each}
  </div>
</div>
