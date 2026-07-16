<script lang="ts">
  import { goto } from '$app/navigation';
  import { quantileRank } from '$lib/analytics/stats';
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';

  interface Props {
    metric: string;
    year?: number;
  }

  let { metric, year = new Date().getFullYear() }: Props = $props();

  let hovered: {
    date: string;
    dayOfMonth: string;
    value: number | null;
    percentile: number | null;
    x: number;
    y: number;
  } | null = $state(null);

  let data = $derived.by(() => {
    const m = metric;
    const y = year;
    return liveQuery(async () => {
      const start = new Date(+y, 0, 1).toISOString();
      const end = new Date(+y + 1, 0, 1).toISOString();
      const measurements = await db.measurement
        .where('start_time')
        .between(start, end, true, true)
        .filter((item) => item.data_type === m && item.value_numeric != null)
        .toArray();
      const daily = new Map<string, number>();
      for (const item of measurements) {
        const d = item.start_time.slice(0, 10);
        const cur = daily.get(d) ?? -Infinity;
        daily.set(d, Math.max(cur, item.value_numeric!));
      }
      return daily;
    });
  });

  let values = $derived([...($data?.values() ?? [])]);

  function getValue(d: Date): number | null {
    const k = d.toISOString().slice(0, 10);
    return $data?.get(k) ?? null;
  }

  function percentile(value: number): number {
    return quantileRank(values, value) ?? 0;
  }

  function colorScale(value: number | null): string {
    if (value == null) return 'var(--color-surface-100)';
    if (value === 0) return 'var(--color-surface-200)';
    const p = percentile(value);
    if (p < 0.25) return 'var(--color-primary-100)';
    if (p < 0.5) return 'var(--color-primary-200)';
    if (p < 0.75) return 'var(--color-primary-400)';
    return 'var(--color-primary-600)';
  }

  const CELL = 14;
  const GAP = 3;
  const STEP = CELL + GAP;
  const LEFT = 36;
  const TOP = 22;

  let days: Array<{ date: Date; col: number; row: number }> = $derived.by(() => {
    const result: Array<{ date: Date; col: number; row: number }> = [];
    const d = new Date(+year, 0, 1);
    const end = new Date(+year + 1, 0, 1);
    const startDay = (d.getDay() + 6) % 7;
    d.setDate(d.getDate() - startDay);
    let col = 0;
    while (d < end) {
      for (let row = 0; row < 7; row++) {
        if (d.getFullYear() === year) {
          result.push({ date: new Date(d), col, row });
        }
        d.setDate(d.getDate() + 1);
      }
      col++;
    }
    return result;
  });

  let svgWidth = $derived(LEFT + (days.at(-1)?.col ?? 0) * STEP + CELL + 12);

  function handleMouseEnter(d: { date: Date; col: number; row: number }, e: MouseEvent) {
    const v = getValue(d.date);
    const p = v != null ? percentile(v) : null;
    hovered = {
      date: d.date.toISOString().slice(0, 10),
      dayOfMonth: d.date.toLocaleDateString('en', {
        weekday: 'short',
        month: 'short',
        day: 'numeric'
      }),
      value: v,
      percentile: p,
      x: e.clientX,
      y: e.clientY
    };
  }

  const MONTHS = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
  ];
  const DAY_LABELS = ['Mon', '', 'Wed', '', 'Fri', '', ''];
</script>

<div class="overflow-x-auto">
  <svg
    width={svgWidth}
    height={TOP + 7 * STEP + 28}
    class="block"
    role="img"
    aria-label="{metric} activity calendar for {year}"
  >
    {#each MONTHS as m, mi}
      {@const firstDay = new Date(+year, mi, 1)}
      {@const offset = Math.floor(
        (firstDay.getTime() - new Date(days[0]?.date ?? firstDay).getTime()) / 864e5 / 7
      )}
      {#if offset >= 0 && offset <= (days.at(-1)?.col ?? 53)}
        <text x={LEFT + offset * STEP} y={TOP - 6} class="fill-surface-400 text-[10px]">{m}</text>
      {/if}
    {/each}
    {#each DAY_LABELS as label, i}
      {#if label}
        <text
          x={LEFT - 8}
          y={TOP + i * STEP + CELL / 2 + 4}
          class="fill-surface-400 text-[9px]"
          text-anchor="end">{label}</text
        >
      {/if}
    {/each}
    {#each days as d (d.date.toISOString())}
      <rect
        x={LEFT + d.col * STEP}
        y={TOP + d.row * STEP}
        width={CELL}
        height={CELL}
        rx={3}
        fill={colorScale(getValue(d.date))}
        class="cursor-pointer transition-colors hover:stroke-surface-500 hover:stroke-[1.5]"
        role="cell"
        tabindex={0}
        onmouseenter={(e) => handleMouseEnter(d, e)}
        onmouseleave={() => (hovered = null)}
        onclick={() => goto(`/entries?date=${d.date.toISOString().slice(0, 10)}`)}
        onkeydown={(e) => {
          if (e.key === 'Enter') goto(`/entries?date=${d.date.toISOString().slice(0, 10)}`);
        }}
      >
        <title>{d.date.toISOString().slice(0, 10)}: {getValue(d.date) ?? 'No data'}</title>
      </rect>
    {/each}
  </svg>
</div>

{#if hovered}
  <div
    class="pointer-events-none fixed z-60 rounded-md border border-surface-200 bg-surface-0 px-3 py-2 text-xs shadow-lg"
    style="left:{hovered.x + 14}px;top:{hovered.y - 40}px"
  >
    <div class="font-medium text-surface-800">{hovered.dayOfMonth}</div>
    {#if hovered.value != null}
      <div class="mt-0.5 text-surface-600 tabular-nums">
        {metric}: {hovered.value.toLocaleString()}
      </div>
      <div class="text-[11px] text-surface-400 tabular-nums">
        percentile: {(hovered.percentile! * 100).toFixed(0)}%
      </div>
    {:else}
      <div class="text-surface-400">No data</div>
    {/if}
  </div>
{/if}
