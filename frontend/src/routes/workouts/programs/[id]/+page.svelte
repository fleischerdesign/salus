<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import { startWorkout } from '$lib/mutations/workout';
  import { activateProgram, deactivateProgram, deleteProgram } from '$lib/mutations/program';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import WeeklyScheduleGrid, {
    type ScheduleSlot
  } from '$components/workouts/WeeklyScheduleGrid.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { resolveToday } from '$lib/utils/program-schedule';

  const programId = $derived(page.params.id as string);

  const programQuery = useQuery(
    () => db.program.get(programId!).then((p) => (p && !p.deleted_at ? p : null)),
    () => programId
  );
  const program = $derived(programQuery.value);

  const slotsQuery = useQuery(
    () =>
      db.program_workout
        .where('program_id')
        .equals(programId!)
        .toArray()
        .then((arr) => arr.filter((s) => !s.deleted_at).sort((a, b) => a.sequence - b.sequence)),
    () => programId
  );
  const slots = $derived(slotsQuery.value);

  const workoutsQuery = useQuery(() =>
    db.workout
      .toArray()
      .then((arr) => new Map(arr.filter((w) => !w.deleted_at).map((w) => [w.id, w])))
  );
  const workouts = $derived(workoutsQuery.value);

  const planExercisesQuery = useQuery(() =>
    db.workout_exercise.toArray().then((arr) => {
      const counts = new Map<string, number>();
      for (const we of arr) {
        if (we.deleted_at) continue;
        counts.set(we.workout_id, (counts.get(we.workout_id) ?? 0) + 1);
      }
      return counts;
    })
  );
  const exerciseCounts = $derived(planExercisesQuery.value);

  const sessionsQuery = useQuery(
    () =>
      db.workout_session
        .where('program_id')
        .equals(programId!)
        .toArray()
        .then((arr) =>
          arr
            .filter((s) => !s.deleted_at && s.completed_at != null)
            .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
        ),
    () => programId
  );
  const sessions = $derived(sessionsQuery.value ?? []);

  const isActive = $derived(program?.is_active ?? false);
  const isSystem = $derived(Boolean(program && !program.user_id));
  const loading = $derived(programQuery.loading || slotsQuery.loading);

  const weeklySlots = $derived((slots ?? []).filter((s) => s.day_of_week != null));
  const rotationSlots = $derived(
    (slots ?? []).filter((s) => s.day_of_week == null && s.scheduled_date == null)
  );

  const scheduleSlots = $derived<ScheduleSlot[]>(
    weeklySlots.map((s) => ({
      weekday: s.day_of_week as number,
      workoutId: s.workout_id,
      name: workouts?.get(s.workout_id)?.name ?? 'Workout',
      exercisesCount: exerciseCounts?.get(s.workout_id) ?? 0
    }))
  );

  const uniqueWorkoutIds = $derived([
    ...new Set((slots ?? []).map((s) => s.workout_id).filter(Boolean))
  ]);

  const todayResolution = $derived.by(() => {
    const now = new Date();
    const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(
      now.getDate()
    ).padStart(2, '0')}`;
    const weekday = (now.getDay() + 6) % 7;
    const lastWorkoutId = sessions[0]?.workout_id ?? null;
    return resolveToday(slots ?? [], lastWorkoutId, todayStr, weekday);
  });

  const todayWorkoutId = $derived(
    todayResolution?.workoutId ?? weeklySlots[0]?.workout_id ?? rotationSlots[0]?.workout_id ?? null
  );

  function progressionInfo(scheme: string): { title: string; desc: string; scientific: string } {
    switch (scheme) {
      case 'linear':
        return {
          title: 'Lineare Progression',
          desc: 'Feste, periodische Gewichtssteigerungen bei Erreichen der Zielwiederholungen.',
          scientific:
            'Das Trainingsgewicht wird kontinuierlich in festen Schritten erhöht (z. B. +2.5 kg). Sobald alle Sätze im Zielbereich absolviert wurden, erfolgt die nächste Steigerung.'
        };
      case 'autoregulated':
        return {
          title: 'Autoregulierte Progression (RPE & Recovery)',
          desc: 'Dynamische Lastanpassung anhand von Erholungsdaten, Schlaf und tatsächlichem RPE.',
          scientific:
            'Die Trainingsbelastung passt sich täglich deiner physiologischen Erholung (Schlaf, HRV, Subjektives Wohlbefinden) und der RIR/RPE-Auslastung der vorherigen Einheit an.'
        };
      default:
        return {
          title: scheme || 'Standard-Progression',
          desc: 'Fortschrittssteuerung für diesen Trainingsplan.',
          scientific: 'Manuelle Progression mit Dokumentation der Sätze und Wiederholungen.'
        };
    }
  }

  let toggling = $state(false);
  let starting = $state(false);
  let deleteOpen = $state(false);

  async function toggleActive() {
    if (!program) return;
    toggling = true;
    try {
      if (isActive) {
        await deactivateProgram(program.id);
      } else {
        await activateProgram(program.id);
      }
    } finally {
      toggling = false;
    }
  }

  async function startToday() {
    if (!todayWorkoutId || !program) return;
    starting = true;
    try {
      await startWorkout(todayWorkoutId, program.id);
      await goto('/workouts/active');
    } finally {
      starting = false;
    }
  }

  async function handleDelete() {
    deleteOpen = false;
    await deleteProgram(programId);
    await goto('/workouts/programs');
  }
</script>

<svelte:head><title>Salus — {program?.name ?? 'Trainingsprogramm'}</title></svelte:head>

{#if loading}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else if program && slots}
  <div class="space-y-6">
    <!-- Breadcrumb Navigation -->
    <div>
      <a
        href="/workouts/programs"
        class="inline-flex items-center gap-1.5 text-xs font-bold text-text-muted transition-colors hover:text-text-main"
      >
        <Icon name="arrow_back" class="text-sm" />
        <span>Zurück zu Programme</span>
      </a>
    </div>

    <!-- Hero Header -->
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div class="space-y-2">
        <div class="flex flex-wrap items-center gap-2">
          <h1 class="text-2xl font-extrabold tracking-tight text-text-main sm:text-3xl">
            {program.name}
          </h1>
          <Badge variant={isSystem ? 'primary' : 'activity'}>
            {isSystem ? 'Standard-Programm' : 'Eigenes Programm'}
          </Badge>
          <Badge variant={isActive ? 'success' : 'default'}>
            {isActive ? 'Aktiv' : 'Inaktiv'}
          </Badge>
          <Badge variant={program.progression_scheme === 'linear' ? 'primary' : 'activity'}>
            {progressionInfo(program.progression_scheme).title}
          </Badge>
        </div>
        <p class="max-w-2xl text-xs text-text-muted sm:text-sm">
          {program.description ||
            'Strukturiertes Mehr-Tage-Trainingsprogramm mit integrierter Periodisierung.'}
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        {#if !isSystem}
          <button
            type="button"
            onclick={() => (deleteOpen = true)}
            class="flex cursor-pointer items-center gap-1.5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-2.5 text-xs font-bold text-rose-600 transition-all hover:bg-rose-100 active:scale-95"
          >
            <Icon name="delete" class="text-sm" />
            <span>Löschen</span>
          </button>
        {/if}

        <button
          type="button"
          onclick={toggleActive}
          disabled={toggling}
          class="flex cursor-pointer items-center gap-2 rounded-2xl border border-border-subtle bg-surface-0 px-4 py-2.5 text-xs font-bold text-text-main shadow-xs transition-all hover:bg-surface-50 active:scale-95 disabled:opacity-50"
        >
          <Icon name={isActive ? 'pause' : 'check'} class="text-sm text-text-muted" />
          <span>{isActive ? 'Programm pausieren' : 'Programm aktivieren'}</span>
        </button>

        {#if todayWorkoutId}
          <button
            type="button"
            onclick={startToday}
            disabled={starting}
            class="flex cursor-pointer items-center gap-2 rounded-2xl bg-primary px-5 py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-90 active:scale-95 disabled:opacity-50"
          >
            <Icon name="play_arrow" class="text-base" />
            <span>{starting ? 'Startet...' : 'Heutiges Training starten'}</span>
          </button>
        {/if}
      </div>
    </div>

    <!-- KPI Metric Cards Grid -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <div class="flex items-center gap-1.5 text-xs font-bold text-text-muted">
          <Icon name="calendar_view_week" class="text-sm text-primary" />
          <span>Trainingstage</span>
        </div>
        <div class="mt-2 text-xl font-extrabold text-text-main tabular-nums">
          {slots.length} Tage
        </div>
        <p class="mt-0.5 text-[0.6875rem] text-text-soft">
          {weeklySlots.length > 0 ? `${weeklySlots.length} feste Wochentage` : 'Rotations-Zyklus'}
        </p>
      </div>

      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <div class="flex items-center gap-1.5 text-xs font-bold text-text-muted">
          <Icon name="fitness_center" class="text-sm text-activity" />
          <span>Workouts</span>
        </div>
        <div class="mt-2 text-xl font-extrabold text-text-main tabular-nums">
          {uniqueWorkoutIds.length} Pläne
        </div>
        <p class="mt-0.5 text-[0.6875rem] text-text-soft">Im Programm enthalten</p>
      </div>

      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <div class="flex items-center gap-1.5 text-xs font-bold text-text-muted">
          <Icon name="trending_up" class="text-sm text-emerald-500" />
          <span>Progression</span>
        </div>
        <div class="mt-2 truncate text-base font-extrabold text-text-main">
          {program.progression_scheme === 'linear' ? 'Linear' : 'Autoreguliert'}
        </div>
        <p class="mt-0.5 text-[0.6875rem] text-text-soft">Adaptive Laststeuerung</p>
      </div>

      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <div class="flex items-center gap-1.5 text-xs font-bold text-text-muted">
          <Icon name="history" class="text-sm text-amber-500" />
          <span>Absolviert</span>
        </div>
        <div class="mt-2 text-xl font-extrabold text-text-main tabular-nums">
          {sessions.length}×
        </div>
        <p class="mt-0.5 text-[0.6875rem] text-text-soft">Einheiten in diesem Programm</p>
      </div>
    </div>

    <!-- 7-Day Weekly Schedule Card -->
    <div class="rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
      <div class="mb-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Icon name="calendar_view_week" class="text-primary" />
          <h2 class="text-base font-extrabold text-text-main">Wochenplan &amp; Periodisierung</h2>
        </div>
      </div>

      {#if weeklySlots.length === 0}
        <div class="space-y-2 py-4">
          <p class="text-xs font-semibold text-text-soft">
            Dieses Programm verwendet eine flexible Rotation der Workouts:
          </p>
          <div class="flex flex-wrap items-center gap-2">
            {#each rotationSlots as slot, i}
              {@const w = workouts?.get(slot.workout_id)}
              <a
                href="/workouts/plans/{slot.workout_id}"
                class="inline-flex items-center gap-1.5 rounded-xl border border-border-subtle bg-surface-50 px-3 py-2 text-xs font-bold text-text-main transition-colors hover:border-primary hover:text-primary"
              >
                <span class="font-mono text-[10px] text-text-muted">#{i + 1}</span>
                <span>{w?.name ?? 'Workout'}</span>
              </a>
              {#if i < rotationSlots.length - 1}
                <Icon name="arrow_forward" class="text-xs text-text-muted" />
              {/if}
            {/each}
          </div>
        </div>
      {:else}
        <WeeklyScheduleGrid slots={scheduleSlots} interactive={true} />
      {/if}
    </div>

    <!-- Bottom Two Columns: Progression Mechanics & Included Workouts -->
    <div class="grid gap-6 lg:grid-cols-2">
      <!-- Progression Explanation Card -->
      <div class="rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
        <div class="mb-3 flex items-center gap-2">
          <Icon name="psychology" class="text-primary" />
          <h2 class="text-base font-extrabold text-text-main">
            {progressionInfo(program.progression_scheme).title}
          </h2>
        </div>
        <p class="text-xs leading-relaxed text-text-muted">
          {progressionInfo(program.progression_scheme).scientific}
        </p>

        <div class="mt-4 space-y-2 rounded-2xl border border-border-subtle bg-surface-50 p-3.5">
          <div class="flex items-center gap-2 text-xs font-bold text-text-main">
            <Icon name="auto_awesome" class="text-sm text-primary" />
            <span>Evidenzbasierte Salus-Steuerung</span>
          </div>
          <p class="text-[0.6875rem] leading-relaxed text-text-soft">
            Deine Gewichte und Wiederholungen werden nicht starr vorgegeben, sondern orientieren
            sich an deinen individuellen RPE-Eingaben und Erholungswerten für nachhaltigen Kraft-
            und Muskelaufbau.
          </p>
        </div>
      </div>

      <!-- Included Workouts Overview -->
      <div class="rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
        <div class="mb-3 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Icon name="fitness_center" class="text-primary" />
            <h2 class="text-base font-extrabold text-text-main">Enthaltene Workout-Tage</h2>
          </div>
          <span class="text-xs font-bold text-text-muted">{uniqueWorkoutIds.length} Pläne</span>
        </div>

        <div class="space-y-2.5">
          {#each uniqueWorkoutIds as wid}
            {@const w = workouts?.get(wid)}
            <a
              href="/workouts/plans/{wid}"
              class="flex items-center justify-between rounded-2xl border border-border-subtle bg-surface-50 p-3.5 no-underline transition-all hover:border-primary hover:bg-surface-0"
            >
              <div class="min-w-0">
                <span class="block truncate text-xs font-extrabold text-text-main">
                  {w?.name ?? 'Workout'}
                </span>
                <span class="text-[0.6875rem] text-text-muted">
                  {w?.description || 'Strukturierter Trainingsplan'} · {exerciseCounts?.get(wid) ??
                    0}
                  Übungen
                </span>
              </div>
              <div class="flex shrink-0 items-center gap-1.5 text-xs font-bold text-primary">
                <span>Plan ansehen</span>
                <Icon name="chevron_right" class="text-sm text-text-muted" />
              </div>
            </a>
          {/each}
        </div>
      </div>
    </div>
  </div>
{:else}
  <EmptyState
    title="Programm nicht gefunden"
    description="Das gesuchte Trainingsprogramm existiert nicht oder wurde gelöscht."
    icon="calendar_view_week"
  />
{/if}

<ConfirmDialog
  open={deleteOpen}
  title="Programm löschen?"
  message="Möchtest du dieses Trainingsprogramm wirklich unwiderruflich löschen?"
  confirmLabel="Programm löschen"
  variant="danger"
  onconfirm={handleDelete}
  oncancel={() => (deleteOpen = false)}
/>
