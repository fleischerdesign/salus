<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  const splitQuery = useQuery(async () => {
    const [programs, slots, workouts] = await Promise.all([
      db.program.toArray(),
      db.program_workout.toArray(),
      db.workout.toArray()
    ]);
    const workoutNames = new Map(workouts.map((w) => [w.id, w.name]));
    const weekly = new Map<number, string>();
    for (const slot of slots) {
      if (!slot.deleted_at && slot.day_of_week !== null && slot.day_of_week !== undefined) {
        weekly.set(slot.day_of_week, workoutNames.get(slot.workout_id) ?? 'Workout');
      }
    }
    return {
      programCount: programs.filter((p) => !p.deleted_at).length,
      weekly
    };
  });

  const data = $derived(splitQuery.value);
  const weekly = $derived(data?.weekly ?? new Map<number, string>());
  const hasSchedule = $derived((data?.weekly.size ?? 0) > 0);
  const daysOfWeek = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
</script>

<div class="rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-text-main">
      <Icon name="calendar-view-week" class="text-primary" />
      <span>Wöchentliche Periodisierung</span>
    </div>
    <Badge variant="activity">{data?.programCount ?? 0} Programme</Badge>
  </div>

  {#if !hasSchedule}
    <div class="space-y-1 py-6 text-center text-xs text-text-muted">
      <p class="font-semibold text-text-main">Noch kein Wochenplan definiert</p>
      <p class="text-[0.6875rem]">
        Lege in einem Programm Wochentage fest, um deinen Wochen-Split zu sehen.
      </p>
    </div>
  {:else}
    <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 md:grid-cols-7">
      {#each daysOfWeek as day, idx}
        <div
          class="flex flex-col justify-between rounded-2xl border border-border-subtle bg-surface-50 p-3"
        >
          <span
            class="mb-1 rounded bg-surface-0 px-1.5 py-0.5 font-mono text-xs font-bold text-text-main"
          >
            {day}
          </span>
          <div class="mt-1 truncate text-xs font-bold text-text-main">
            {weekly.get(idx) ?? 'Ruhetag'}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
