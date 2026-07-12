<script lang="ts">
  interface ChartSeries {
    label: string;
    data: number[];
    color: string;
    yAxis: 'left' | 'right';
  }

  interface Props {
    labels: string[];
    series: ChartSeries[];
    height?: number;
    leftUnit?: string;
    rightUnit?: string;
  }

  let {
    labels,
    series,
    height = 280,
    leftUnit,
    rightUnit,
  }: Props = $props();

  const padLeft = 44;
  let padRight = $derived(series.some((s) => s.yAxis === 'right') ? 44 : 12);
  const padTop = 12;
  const padBottom = 24;
  const tickCount = 4;

  let width = $state(800);
  let containerEl: HTMLDivElement | null = $state(null);

  const chartW = $derived(width - padLeft - padRight);
  const chartH = $derived(height - padTop - padBottom);

  let leftSeries = $derived(series.filter((s) => s.yAxis === 'left'));
  let rightSeries = $derived(series.filter((s) => s.yAxis === 'right'));

  function niceScale(data: number[]): { min: number; max: number; step: number } {
    if (data.length === 0) return { min: 0, max: 1, step: 0.25 };
    const rawMin = Math.min(...data);
    const rawMax = Math.max(...data);
    if (rawMin === rawMax) {
      return { min: rawMin - 1, max: rawMax + 1, step: 0.5 };
    }
    const range = rawMax - rawMin;
    const mag = Math.pow(10, Math.floor(Math.log10(range)));
    const norm = range / mag;
    let step: number;
    if (norm <= 1) step = 0.25 * mag;
    else if (norm <= 2) step = 0.5 * mag;
    else if (norm <= 5) step = 1 * mag;
    else step = 2 * mag;
    const min = Math.floor(rawMin / step) * step;
    const max = Math.ceil(rawMax / step) * step;
    return { min, max, step };
  }

  let leftScale = $derived(
    niceScale(leftSeries.flatMap((s) => s.data))
  );
  let rightScale = $derived(
    rightSeries.length > 0
      ? niceScale(rightSeries.flatMap((s) => s.data))
      : { min: 0, max: 1, step: 0.25 }
  );

  function scaleY(value: number, axis: 'left' | 'right'): number {
    const scale = axis === 'left' ? leftScale : rightScale;
    const range = scale.max - scale.min || 1;
    return padTop + chartH - ((value - scale.min) / range) * chartH;
  }

  function scaleX(i: number): number {
    if (labels.length <= 1) return padLeft;
    return padLeft + (i / (labels.length - 1)) * chartW;
  }

  function buildPath(data: number[], axis: 'left' | 'right'): string {
    if (data.length === 0) return '';
    return data
      .map((v, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(i).toFixed(1)} ${scaleY(v, axis).toFixed(1)}`)
      .join(' ');
  }

  function buildArea(data: number[], axis: 'left' | 'right'): string {
    if (data.length === 0) return '';
    const path = buildPath(data, axis);
    const lastX = scaleX(data.length - 1);
    const baseY = padTop + chartH;
    return `${path} L ${lastX.toFixed(1)} ${baseY.toFixed(1)} L ${padLeft.toFixed(1)} ${baseY.toFixed(1)} Z`;
  }

  let leftTicks = $derived.by(() => {
    const ticks: number[] = [];
    for (let i = 0; i <= tickCount; i++) {
      ticks.push(leftScale.min + (i / tickCount) * (leftScale.max - leftScale.min));
    }
    return ticks;
  });

  let rightTicks = $derived.by(() => {
    if (rightSeries.length === 0) return [];
    const ticks: number[] = [];
    for (let i = 0; i <= tickCount; i++) {
      ticks.push(rightScale.min + (i / tickCount) * (rightScale.max - rightScale.min));
    }
    return ticks;
  });

  let labelStep = $derived(
    labels.length > 12 ? Math.ceil(labels.length / 8) : 1
  );

  let gradientId = `linechart-grad-${Math.random().toString(36).slice(2, 9)}`;

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
          <stop offset="0%" stop-color={s.color} stop-opacity="0.2" />
          <stop offset="100%" stop-color={s.color} stop-opacity="0.02" />
        </linearGradient>
      {/each}
    </defs>

    <!-- Horizontal grid lines + left axis ticks -->
    {#each leftTicks as tick}
      {@const y = scaleY(tick, 'left')}
      <line x1={padLeft} y1={y} x2={width - padRight} y2={y} stroke="var(--color-surface-100)" stroke-width="1" />
      <text x={padLeft - 6} y={y + 4} text-anchor="end" class="fill-surface-400 text-[10px] tabular-nums">
        {tick >= 1000 ? (tick / 1000).toFixed(1) + 'k' : tick.toFixed(tick % 1 === 0 ? 0 : 1)}
      </text>
    {/each}

    <!-- Right axis ticks -->
    {#each rightTicks as tick}
      {@const y = scaleY(tick, 'right')}
      <text x={width - padRight + 6} y={y + 4} text-anchor="start" class="fill-surface-400 text-[10px] tabular-nums">
        {tick >= 1000 ? (tick / 1000).toFixed(1) + 'k' : tick.toFixed(tick % 1 === 0 ? 0 : 1)}
      </text>
    {/each}

    <!-- X-axis labels (sparse) -->
    {#each labels as label, i}
      {#if i % labelStep === 0 || i === labels.length - 1}
        <text x={scaleX(i)} y={height - 6} text-anchor="middle" class="fill-surface-400 text-[10px]">
          {label}
        </text>
      {/if}
    {/each}

    <!-- Axis labels -->
    {#if leftUnit}
      <text x={4} y={padTop + chartH / 2} text-anchor="start" transform="rotate(-90 4 {padTop + chartH / 2})" class="fill-surface-400 text-[10px] font-medium">
        {leftUnit}
      </text>
    {/if}
    {#if rightUnit && rightSeries.length > 0}
      <text x={width - 4} y={padTop + chartH / 2} text-anchor="end" transform="rotate(-90 {width - 4} {padTop + chartH / 2})" class="fill-surface-400 text-[10px] font-medium">
        {rightUnit}
      </text>
    {/if}

    <!-- Series areas + lines -->
    {#each series as s, i}
      <path d={buildArea(s.data, s.yAxis)} fill="url(#{gradientId}-{i})" />
      <path d={buildPath(s.data, s.yAxis)} fill="none" stroke={s.color} stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
    {/each}
  </svg>

  <!-- Legend -->
  <div class="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1">
    {#each series as s}
      <div class="flex items-center gap-1.5">
        <span class="inline-block h-2 w-2 rounded-full" style="background-color: {s.color}"></span>
        <span class="text-xs text-surface-500">{s.label}</span>
      </div>
    {/each}
  </div>
</div>
