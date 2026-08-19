<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';

  interface RingData {
    current: number;
    target: number;
    percent: number;
    label: string;
  }

  let {
    activity: propActivity,
    hydration: propHydration,
    habits: propHabits,
    date = todayString()
  } = $props<{
    activity?: RingData;
    hydration?: RingData;
    habits?: RingData;
    date?: string;
  }>();

  // Reactive Dexie Query for Goals and Measurements if not passed via props
  const ringsQuery = useQuery(
    async () => {
      const dayStart = new Date(date + 'T00:00:00').toISOString();
      const dayEnd = new Date(date + 'T23:59:59.999').toISOString();

      const [measurements, goals, habits, habitLogs] = await Promise.all([
        db.measurement.where('start_time').between(dayStart, dayEnd).toArray(),
        db.goal.toArray(),
        db.habit.toArray(),
        db.habit_log.where('log_date').equals(date).toArray()
      ]);

      const validM = measurements.filter((m) => !m.deleted_at);
      const validGoals = goals.filter((g) => !g.deleted_at);
      const activeHabits = habits.filter((h) => !h.deleted_at && !h.is_archived);
      const doneHabits = habitLogs.filter((l) => !l.deleted_at && l.completed).length;

      // 1. Steps (Activity)
      const stepsMeasurements = validM.filter((m) => m.metric_code === 'steps');
      const currentSteps = stepsMeasurements.reduce((sum, m) => sum + (m.value_numeric || 0), 0);
      const stepGoal = validGoals.find((g) => g.metric_code === 'steps')?.target_value ?? 10000;
      const stepPercent =
        stepGoal > 0 ? Math.min(100, Math.round((currentSteps / stepGoal) * 100)) : 0;

      // 2. Hydration (Water)
      const waterMeasurements = validM.filter(
        (m) => m.metric_code === 'hydration' || m.metric_code === 'water'
      );
      const currentWater = waterMeasurements.reduce((sum, m) => sum + (m.value_numeric || 0), 0);
      const waterGoal =
        validGoals.find((g) => g.metric_code === 'hydration' || g.metric_code === 'water')
          ?.target_value ?? 2500;
      const waterPercent =
        waterGoal > 0 ? Math.min(100, Math.round((currentWater / waterGoal) * 100)) : 0;

      // 3. Habits
      const habitsTotal = activeHabits.length;
      const habitPercent =
        habitsTotal > 0 ? Math.min(100, Math.round((doneHabits / habitsTotal) * 100)) : 0;

      return {
        activity: {
          current: currentSteps,
          target: stepGoal,
          percent: stepPercent,
          label: 'Schritte'
        },
        hydration: {
          current: currentWater,
          target: waterGoal,
          percent: waterPercent,
          label: 'Wasser'
        },
        habits: {
          current: doneHabits,
          target: habitsTotal,
          percent: habitPercent,
          label: 'Gewohnheiten'
        }
      };
    },
    () => date
  );

  const liveData = $derived(ringsQuery.value);

  const activity = $derived(
    propActivity ??
      liveData?.activity ?? { current: 0, target: 10000, percent: 0, label: 'Schritte' }
  );
  const hydration = $derived(
    propHydration ??
      liveData?.hydration ?? { current: 0, target: 2500, percent: 0, label: 'Wasser' }
  );
  const habits = $derived(
    propHabits ?? liveData?.habits ?? { current: 0, target: 0, percent: 0, label: 'Gewohnheiten' }
  );

  const avgPercent = $derived(
    habits.target > 0
      ? Math.round((activity.percent + hydration.percent + habits.percent) / 3)
      : Math.round((activity.percent + hydration.percent) / 2)
  );

  const rings = $derived([
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
  class="flex flex-col justify-between space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-card"
>
  <div class="flex items-start justify-between gap-3">
    <div class="flex min-w-0 items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
        style="background-color: color-mix(in srgb, var(--color-primary) 12%, transparent); color: var(--color-primary);"
      >
        <Icon name="emoji-events" size="md" />
      </div>
      <div class="min-w-0">
        <h3 class="truncate text-sm font-extrabold tracking-tight text-text-main">
          Hero Ziel-Ringe
        </h3>
        <p class="truncate text-xs text-text-muted">Tages-Status der Hauptziele</p>
      </div>
    </div>
    <Badge variant={avgPercent >= 70 ? 'success' : 'default'} class="text-[0.625rem] font-bold">
      {avgPercent}% Schnitt
    </Badge>
  </div>

  <div class="relative mx-auto my-2 flex h-[180px] w-[180px] items-center justify-center">
    <svg class="h-full w-full -rotate-90" viewBox="0 0 180 180">
      {#each rings as ring (ring.id)}
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
      <span class="text-2xl font-extrabold text-text-main tabular-nums">
        {avgPercent}%
      </span>
      <span class="text-[0.6875rem] font-bold tracking-wider text-text-muted uppercase">
        Erfüllt
      </span>
    </div>
  </div>

  <div class="grid grid-cols-3 gap-2 border-t border-border-subtle pt-3 text-center text-xs">
    <div>
      <span class="block font-extrabold text-activity tabular-nums">
        {activity.current.toLocaleString('de-DE')}
      </span>
      <span class="text-[0.6875rem] text-text-muted">
        / {activity.target.toLocaleString('de-DE')}
        {activity.label}
      </span>
    </div>
    <div>
      <span class="block font-extrabold text-hydrate tabular-nums">
        {hydration.current.toLocaleString('de-DE')} ml
      </span>
      <span class="text-[0.6875rem] text-text-muted">
        / {hydration.target.toLocaleString('de-DE')} ml {hydration.label}
      </span>
    </div>
    <div>
      <span class="block font-extrabold text-circadian tabular-nums">
        {habits.current}/{habits.target}
      </span>
      <span class="text-[0.6875rem] text-text-muted">{habits.label}</span>
    </div>
  </div>
</div>
