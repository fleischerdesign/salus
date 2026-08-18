<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    activity = { current: 0, target: 10000, percent: 0, label: 'Schritte' },
    hydration = { current: 0, target: 3000, percent: 0, label: 'Wasser' },
    habits = { current: 0, target: 0, percent: 0, label: 'Habits' }
  } = $props<{
    activity?: { current: number; target: number; percent: number; label: string };
    hydration?: { current: number; target: number; percent: number; label: string };
    habits?: { current: number; target: number; percent: number; label: string };
  }>();

  let avgPercent = $derived(
    habits.target > 0
      ? Math.round((activity.percent + hydration.percent + habits.percent) / 3)
      : Math.round((activity.percent + hydration.percent) / 2)
  );

  let rings = $derived([
    {
      id: 'activity',
      radius: 72,
      strokeWidth: 10,
      color: 'var(--color-activity)',
      percent: activity.percent
    },
    {
      id: 'hydration',
      radius: 58,
      strokeWidth: 10,
      color: 'var(--color-hydrate)',
      percent: hydration.percent
    },
    {
      id: 'habits',
      radius: 44,
      strokeWidth: 10,
      color: 'var(--color-circadian)',
      percent: habits.percent
    }
  ]);

  function getOffset(radius: number, percent: number) {
    const c = 2 * Math.PI * radius;
    return c * (1 - Math.min(percent / 100, 1));
  }
</script>

<div
  class="flex flex-col justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-[18px] shadow-[var(--shadow-card)]"
>
  <div class="mb-2 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
      <Icon name="show-chart" class="text-[var(--color-primary)]" />
      <span>Tages-Status Ringe</span>
    </div>
    <Badge variant={avgPercent >= 70 ? 'success' : 'default'}>{avgPercent}% Schnitt</Badge>
  </div>

  <div class="relative mx-auto my-1 flex h-[180px] w-[180px] items-center justify-center">
    <svg class="h-full w-full -rotate-90" viewBox="0 0 180 180">
      {#each rings as ring}
        <!-- Background Track -->
        <circle
          cx="90"
          cy="90"
          r={ring.radius}
          fill="none"
          stroke={ring.color}
          stroke-opacity="0.15"
          stroke-width={ring.strokeWidth}
        />
        <!-- Progress Arc -->
        <circle
          cx="90"
          cy="90"
          r={ring.radius}
          fill="none"
          stroke={ring.color}
          stroke-width={ring.strokeWidth}
          stroke-dasharray={2 * Math.PI * ring.radius}
          stroke-dashoffset={getOffset(ring.radius, ring.percent)}
          stroke-linecap="round"
          class="transition-all duration-700 ease-out"
        />
      {/each}
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
      <span class="font-mono text-xl font-extrabold text-[var(--text-main)] tabular-nums">
        {avgPercent}%
      </span>
      <span class="text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >Erfüllt</span
      >
    </div>
  </div>

  <div
    class="grid grid-cols-3 gap-1 border-t border-[var(--border-subtle)] pt-2 text-center text-xs"
  >
    <div>
      <span class="block font-bold text-[var(--color-activity)]"
        >{activity.current.toLocaleString('de-DE')}</span
      >
      <span class="text-[0.6875rem] text-[var(--text-muted)]">{activity.label}</span>
    </div>
    <div>
      <span class="block font-bold text-[var(--color-hydrate)]">{hydration.current} ml</span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">{hydration.label}</span>
    </div>
    <div>
      <span class="block font-bold text-[var(--color-circadian)]"
        >{habits.current}/{habits.target}</span
      >
      <span class="text-[0.6875rem] text-[var(--text-muted)]">{habits.label}</span>
    </div>
  </div>
</div>
