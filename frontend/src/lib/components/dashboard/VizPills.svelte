<script lang="ts">
  export interface PillBucket {
    label: string;
    min: number;
    max: number;
    avg?: number;
    count?: number;
  }

  interface Props {
    value?: string | number;
    unit?: string;
    subtitle?: string;
    color?: string;
    buckets?: PillBucket[];
    items?: PillBucket[];
    height?: number;
  }

  let {
    value,
    unit = 'bpm',
    subtitle,
    color = '#f43f5e',
    buckets,
    items,
    height = 88
  }: Props = $props();

  let resolvedBuckets = $derived(buckets ?? items ?? []);

  // Compute active buckets with data
  let activeBuckets = $derived(resolvedBuckets.filter((b) => (b.count ?? 0) > 0 && b.max > 0));

  // Determine global min and max for scaling
  let minBpm = $derived(
    activeBuckets.length > 0 ? Math.min(...activeBuckets.map((b) => b.min)) : 50
  );
  let maxBpm = $derived(
    activeBuckets.length > 0 ? Math.max(...activeBuckets.map((b) => b.max)) : 160
  );

  // Pad domain for clean grid boundaries
  let yMin = $derived(Math.max(30, Math.floor((minBpm - 5) / 10) * 10));
  let yMax = $derived(Math.min(220, Math.ceil((maxBpm + 5) / 10) * 10));
  let yRange = $derived(Math.max(30, yMax - yMin));

  const padTop = 4;
  const padBottom = 16;
  const totalWidth = 300;
  const pillWidth = 5;

  let chartH = $derived(height - padTop - padBottom);

  // Distribute 24 pills so index 0 starts at x = 0 and index 23 ends at x = totalWidth
  function getCenterX(h: number): number {
    return pillWidth / 2 + (h * (totalWidth - pillWidth)) / 23;
  }

  function getY(val: number): number {
    const clamped = Math.max(yMin, Math.min(yMax, val));
    return padTop + chartH - ((clamped - yMin) / yRange) * chartH;
  }

  let hoveredBucket = $state<PillBucket | null>(null);
</script>

<div class="flex flex-col gap-2">
  <!-- Header: Primary Value & Daily Range Summary (Flush Left & Right) -->
  <div class="flex items-baseline justify-between">
    <div class="flex items-baseline gap-1.5">
      <span class="text-2xl font-black text-[var(--text-main)] tabular-nums">{value ?? '—'}</span>
      {#if unit}
        <span class="text-xs font-bold tracking-wider text-[var(--text-soft)] uppercase"
          >{unit}</span
        >
      {/if}
    </div>

    {#if hoveredBucket}
      <span class="text-xs font-bold text-rose-500 transition-all">
        {hoveredBucket.label}: {hoveredBucket.min}–{hoveredBucket.max} bpm
      </span>
    {:else if subtitle}
      <span class="text-xs font-semibold text-[var(--text-muted)]">{subtitle}</span>
    {/if}
  </div>

  <!-- Apple Health 24h Range Pill Chart (Flush 100% Left-to-Right) -->
  <div class="relative w-full overflow-hidden select-none">
    <svg
      viewBox="0 0 {totalWidth} {height}"
      preserveAspectRatio="none"
      class="w-full overflow-visible"
      style="height: {height}px;"
    >
      <!-- Grid Guide Lines (Spanning full width from 0 to totalWidth) -->
      <line
        x1="0"
        y1={getY(yMax)}
        x2={totalWidth}
        y2={getY(yMax)}
        stroke="var(--color-surface-200)"
        stroke-dasharray="2 3"
        stroke-width="0.75"
        stroke-opacity="0.6"
      />
      <line
        x1="0"
        y1={getY((yMin + yMax) / 2)}
        x2={totalWidth}
        y2={getY((yMin + yMax) / 2)}
        stroke="var(--color-surface-200)"
        stroke-dasharray="2 3"
        stroke-width="0.75"
        stroke-opacity="0.6"
      />
      <line
        x1="0"
        y1={getY(yMin)}
        x2={totalWidth}
        y2={getY(yMin)}
        stroke="var(--color-surface-200)"
        stroke-dasharray="2 3"
        stroke-width="0.75"
        stroke-opacity="0.6"
      />

      <!-- 24 Hourly Range Pills -->
      {#each resolvedBuckets as bucket, h}
        {@const cx = getCenterX(h)}
        {@const hasData = (bucket.count ?? 0) > 0 && bucket.max > 0}
        {@const slotW = totalWidth / 24}

        {#if hasData}
          {@const yTop = getY(bucket.max)}
          {@const yBottom = getY(bucket.min)}
          {@const pillH = Math.max(pillWidth, yBottom - yTop)}
          {@const isHovered = hoveredBucket === bucket}

          <!-- Interactive Hover Zone -->
          <!-- svelte-ignore a11y_no_static_element_interactions -->
          <rect
            x={cx - slotW / 2}
            y={padTop}
            width={slotW}
            height={chartH}
            fill="transparent"
            class="cursor-pointer"
            onpointerenter={() => (hoveredBucket = bucket)}
            onpointerleave={() => (hoveredBucket = null)}
          />

          <!-- Apple Health Range Pill -->
          <rect
            x={cx - pillWidth / 2}
            y={yTop}
            width={pillWidth}
            height={pillH}
            rx={pillWidth / 2}
            fill={color}
            opacity={hoveredBucket && !isHovered ? 0.35 : 0.9}
            class="duration-micro transition-opacity"
          />

          <!-- Single Point Dot when Min = Max -->
          {#if bucket.min === bucket.max}
            <circle {cx} cy={yTop + pillWidth / 2} r={pillWidth / 2} fill={color} />
          {/if}
        {:else}
          <!-- Empty Hour Indicator Dot -->
          <circle
            {cx}
            cy={padTop + chartH / 2}
            r="1"
            fill="var(--color-surface-200)"
            opacity="0.25"
          />
        {/if}
      {/each}

      <!-- X-Axis Hour Markers (Flush Left at 0 and Flush Right at totalWidth) -->
      <text
        x="0"
        y={height - 2}
        text-anchor="start"
        class="fill-surface-400 text-[10px] font-medium"
      >
        00:00
      </text>
      <text
        x={getCenterX(6)}
        y={height - 2}
        text-anchor="middle"
        class="fill-surface-400 text-[10px] font-medium"
      >
        06:00
      </text>
      <text
        x={getCenterX(12)}
        y={height - 2}
        text-anchor="middle"
        class="fill-surface-400 text-[10px] font-medium"
      >
        12:00
      </text>
      <text
        x={getCenterX(18)}
        y={height - 2}
        text-anchor="middle"
        class="fill-surface-400 text-[10px] font-medium"
      >
        18:00
      </text>
      <text
        x={totalWidth}
        y={height - 2}
        text-anchor="end"
        class="fill-surface-400 text-[10px] font-medium"
      >
        23:00
      </text>
    </svg>
  </div>
</div>
