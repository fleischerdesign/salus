<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    activity = { current: 8420, target: 10000, percent: 84, label: 'Schritte' },
    hydration = { current: 2250, target: 3000, percent: 75, label: 'Wasser' },
    habits = { current: 3, target: 4, percent: 75, label: 'Habits' }
  } = $props<{
    activity?: { current: number; target: number; percent: number; label: string };
    hydration?: { current: number; target: number; percent: number; label: string };
    habits?: { current: number; target: number; percent: number; label: string };
  }>();

  let rings = $derived([
    { id: 'activity', radius: 72, strokeWidth: 10, color: 'var(--color-activity)', percent: activity.percent },
    { id: 'hydration', radius: 58, strokeWidth: 10, color: 'var(--color-hydrate)', percent: hydration.percent },
    { id: 'habits', radius: 44, strokeWidth: 10, color: 'var(--color-circadian)', percent: habits.percent }
  ]);

  function getOffset(radius: number, percent: number) {
    const c = 2 * Math.PI * radius;
    return c * (1 - Math.min(percent / 100, 1));
  }
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-[18px] shadow-[var(--shadow-card)] flex flex-col justify-between">
  <div class="flex items-center justify-between mb-2">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="chart" class="text-[var(--color-primary)]" />
      <span>Tages-Status Ringe</span>
    </div>
    <Badge variant="success">84% Schnitt</Badge>
  </div>

  <div class="relative w-[180px] h-[180px] mx-auto my-1 flex items-center justify-center">
    <svg class="w-full h-full -rotate-90" viewBox="0 0 180 180">
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
      <span class="text-xl font-extrabold font-mono tabular-nums text-[var(--text-main)]">
        {Math.round((activity.percent + hydration.percent + habits.percent) / 3)}%
      </span>
      <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase tracking-wider">Erfüllt</span>
    </div>
  </div>

  <div class="grid grid-cols-3 gap-1 pt-2 border-t border-[var(--border-subtle)] text-center text-xs">
    <div>
      <span class="text-[var(--color-activity)] font-bold block">{activity.current.toLocaleString('de-DE')}</span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">{activity.label}</span>
    </div>
    <div>
      <span class="text-[var(--color-hydrate)] font-bold block">{hydration.current} ml</span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">{hydration.label}</span>
    </div>
    <div>
      <span class="text-[var(--color-circadian)] font-bold block">{habits.current}/{habits.target}</span>
      <span class="text-[0.6875rem] text-[var(--text-muted)]">{habits.label}</span>
    </div>
  </div>
</div>
