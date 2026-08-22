<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import WeeklyScheduleGrid from '../workouts/WeeklyScheduleGrid.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  const splitQuery = useQuery(async () => {
    const [programs, slots, workouts, planExercises] = await Promise.all([
      db.program.toArray(),
      db.program_workout.toArray(),
      db.workout.toArray(),
      db.workout_exercise.toArray()
    ]);
    const workoutMap = new Map(workouts.filter((w) => !w.deleted_at).map((w) => [w.id, w]));
    const exerciseCountMap = new Map<string, number>();
    for (const pe of planExercises) {
      if (!pe.deleted_at) {
        exerciseCountMap.set(pe.workout_id, (exerciseCountMap.get(pe.workout_id) ?? 0) + 1);
      }
    }

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
            workoutId: s.workout_id,
            name: workoutMap.get(s.workout_id)?.name ?? 'Workout',
            exercisesCount: exerciseCountMap.get(s.workout_id) ?? 0
          })),
          rotation: rotation.map((s) => ({
            workoutId: s.workout_id,
            name: workoutMap.get(s.workout_id)?.name ?? 'Workout',
            exercisesCount: exerciseCountMap.get(s.workout_id) ?? 0
          })),
          dated: dated.map((s) => ({
            date: s.scheduled_date as string,
            workoutId: s.workout_id,
            name: workoutMap.get(s.workout_id)?.name ?? 'Workout',
            exercisesCount: exerciseCountMap.get(s.workout_id) ?? 0
          }))
        };
      });
    return activePrograms;
  });

  const programs = $derived(splitQuery.value ?? []);
</script>

<div class="rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
  <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-2">
      <Icon name="calendar_view_week" class="text-primary" />
      <div>
        <h2 class="text-base font-extrabold text-text-main">Wöchentliche Periodisierung</h2>
        <p class="text-xs text-text-muted">Dein aktiver Trainingsrhythmus und Wochenplan</p>
      </div>
    </div>
    <Badge variant={programs.length > 0 ? 'success' : 'default'} class="text-[0.6875rem]">
      {programs.length > 0 ? `${programs.length} aktiv` : 'Inaktiv'}
    </Badge>
  </div>

  {#if programs.length === 0}
    <div
      class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border-subtle bg-surface-50/50 py-8 text-center"
    >
      <div
        class="flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-100 text-text-muted"
      >
        <Icon name="calendar_view_week" size="lg" />
      </div>
      <p class="mt-3 text-sm font-extrabold text-text-main">Kein Programm aktiv</p>
      <p class="mt-1 max-w-sm text-xs text-text-muted">
        Wähle eines der wissenschaftlichen Programme (z. B. Ganzkörper, OK/UK oder PPL), um deinen
        strukturierten Wochenplan zu aktivieren.
      </p>
      <a
        href="/workouts/programs"
        class="mt-4 inline-flex cursor-pointer items-center gap-1.5 rounded-2xl bg-primary px-4 py-2 text-xs font-bold text-white no-underline shadow-sm transition-all hover:opacity-90 active:scale-95"
      >
        <Icon name="play_arrow" class="text-sm" />
        <span>Programme entdecken &amp; aktivieren</span>
      </a>
    </div>
  {:else}
    <div class="space-y-4">
      {#each programs as program}
        <div class="rounded-2xl border border-border-subtle bg-surface-50 p-4">
          <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
            <a
              href="/workouts/programs/{program.id}"
              class="group flex items-center gap-1.5 text-sm font-extrabold text-text-main no-underline transition-colors hover:text-primary"
            >
              <span>{program.name}</span>
              <Icon
                name="chevron_right"
                class="text-sm text-text-muted transition-transform group-hover:translate-x-0.5"
              />
            </a>
            <Badge variant="primary" class="text-[0.625rem]">
              {program.progression_scheme === 'linear' ? 'Linear' : 'Autoreguliert'}
            </Badge>
          </div>

          {#if program.weekly.length > 0}
            <WeeklyScheduleGrid slots={program.weekly} interactive={true} />
          {/if}

          {#if program.rotation.length > 0}
            <div class="mt-3 flex flex-wrap items-center gap-1.5 text-xs">
              <span class="font-bold text-text-soft">Rotations-Reihenfolge:</span>
              {#each program.rotation as item, i}
                <a
                  href="/workouts/plans/{item.workoutId}"
                  class="font-extrabold text-primary no-underline transition-colors hover:underline"
                >
                  {item.name}
                </a>
                {#if i < program.rotation.length - 1}
                  <Icon name="arrow_forward" class="text-xs text-text-muted" />
                {/if}
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
