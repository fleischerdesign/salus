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
    const activePrograms = programs
      .filter((p) => !p.deleted_at && p.is_active)
      .map((p) => {
        const pSlots = slots
          .filter((s) => s.program_id === p.id && !s.deleted_at)
          .sort((a, b) => a.sequence - b.sequence);
        const weekly = pSlots.filter((s) => s.day_of_week != null);
        const rotation = pSlots.filter((s) => s.day_of_week == null && s.scheduled_date == null);
        const dated = pSlots.filter((s) => s.scheduled_date != null);
        return {
          ...p,
          weekly: weekly.map((s) => ({
            weekday: s.day_of_week as number,
            name: workoutNames.get(s.workout_id) ?? 'Workout'
          })),
          rotation: rotation.map((s) => workoutNames.get(s.workout_id) ?? 'Workout'),
          dated: dated.map((s) => ({
            date: s.scheduled_date as string,
            name: workoutNames.get(s.workout_id) ?? 'Workout'
          }))
        };
      });
    return activePrograms;
  });

  const programs = $derived(splitQuery.value ?? []);
  const daysOfWeek = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
</script>

<div class="rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-text-main">
      <Icon name="calendar-view-week" class="text-primary" />
      <span>Wöchentliche Periodisierung</span>
    </div>
    <Badge variant="activity">{programs.length} aktiv</Badge>
  </div>

  {#if programs.length === 0}
    <div class="space-y-1 py-6 text-center text-xs text-text-muted">
      <p class="font-semibold text-text-main">Kein Programm aktiv</p>
      <p class="text-[0.6875rem]">Aktiviere ein Programm, um deinen Wochenplan zu sehen.</p>
    </div>
  {:else}
    <div class="space-y-4">
      {#each programs as program}
        <div class="rounded-2xl border border-border-subtle bg-surface-50 p-4">
          <div class="mb-2 flex items-center justify-between">
            <span class="text-sm font-extrabold text-text-main">{program.name}</span>
            <Badge variant="default" class="text-[0.625rem]">{program.progression_scheme}</Badge>
          </div>

          {#if program.weekly.length > 0}
            <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 md:grid-cols-7">
              {#each daysOfWeek as day, idx}
                {@const slot = program.weekly.find((w) => w.weekday === idx)}
                <div class="rounded-xl border border-border-subtle bg-surface-0 p-2">
                  <span class="block font-mono text-[0.625rem] font-bold text-text-muted"
                    >{day}</span
                  >
                  <span class="mt-1 block truncate text-xs font-bold text-text-main">
                    {slot?.name ?? 'Ruhetag'}
                  </span>
                </div>
              {/each}
            </div>
          {/if}

          {#if program.rotation.length > 0}
            <div class="mt-2 flex flex-wrap items-center gap-1.5 text-xs">
              <span class="font-bold text-text-soft">Rotation:</span>
              {#each program.rotation as name, i}
                <span class="text-text-main">{name}</span>
                {#if i < program.rotation.length - 1}
                  <Icon name="arrow_forward" size="sm" class="text-text-muted" />
                {/if}
              {/each}
            </div>
          {/if}

          {#if program.dated.length > 0}
            <div class="mt-2 space-y-1 text-xs">
              {#each program.dated as d}
                <div class="flex items-center justify-between text-text-main">
                  <span class="font-semibold">{d.name}</span>
                  <span class="text-text-muted">{d.date}</span>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
