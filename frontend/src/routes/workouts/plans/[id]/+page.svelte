<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import { startWorkout } from '$lib/mutations/workout';
  import { deleteWorkout, copyWorkout } from '$lib/mutations/plan';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import MuscleHeatmap2D from '$components/track/MuscleHeatmap2D.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { sessionVolume } from '$lib/utils/workout';
  import { parseMuscles, formatMuscleName } from '$lib/types/workouts';
  import type { WorkoutExercise } from '$lib/db/types';

  const planId = $derived(page.params.id as string);

  const planQuery = useQuery(
    () => db.workout.get(planId!).then((p) => (p && !p.deleted_at ? p : null)),
    () => planId
  );
  const plan = $derived(planQuery.value);

  const planExercisesQuery = useQuery(
    () =>
      db.workout_exercise
        .where('workout_id')
        .equals(planId!)
        .toArray()
        .then((arr) => arr.filter((pe) => !pe.deleted_at).sort((a, b) => a.sequence - b.sequence)),
    () => planId
  );
  const planExercises = $derived(planExercisesQuery.value);

  const exercisesQuery = useQuery(() =>
    db.exercise.toArray().then((arr) => {
      const map = new Map(arr.filter((e) => !e.deleted_at).map((e) => [e.id, e]));
      return map;
    })
  );
  const exercises = $derived(exercisesQuery.value);

  const sessionsQuery = useQuery(
    () =>
      db.workout_session
        .where('workout_id')
        .equals(planId!)
        .toArray()
        .then((arr) =>
          arr
            .filter((s) => !s.deleted_at && s.completed_at != null)
            .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
        ),
    () => planId
  );
  const sessions = $derived(sessionsQuery.value);

  const logsQuery = useQuery(
    async () => {
      const sessionIds = (sessions ?? []).slice(0, 10).map((s) => s.id);
      if (sessionIds.length === 0) return [];
      return db.workout_set
        .where('session_id')
        .anyOf(sessionIds)
        .filter((l) => !l.deleted_at)
        .toArray();
    },
    () => `${planId}:${(sessions ?? []).length}`
  );
  const logs = $derived(logsQuery.value);

  const isSystem = $derived(Boolean(plan && !plan.user_id));
  const loading = $derived(planQuery.loading || planExercisesQuery.loading);
  const estimatedDuration = $derived(`${(planExercises?.length ?? 0) * 10 || 45} Min`);
  const totalTargetSets = $derived(
    (planExercises ?? []).reduce((sum, pe) => sum + (pe.target_sets || 3), 0)
  );

  function restSeconds(pe: WorkoutExercise): number {
    return pe.rest_seconds ?? exercises?.get(pe.exercise_id)?.suggested_rest_seconds ?? 90;
  }

  let starting = $state(false);
  let duplicating = $state(false);
  let deleteOpen = $state(false);

  async function startSession() {
    starting = true;
    try {
      await startWorkout(planId!);
      await goto('/workouts/active');
    } finally {
      starting = false;
    }
  }

  async function duplicateAsTemplate() {
    duplicating = true;
    try {
      await copyWorkout(planId!);
      await goto('/workouts/plans');
    } finally {
      duplicating = false;
    }
  }

  async function handleDelete() {
    deleteOpen = false;
    await deleteWorkout(planId!);
    await goto('/workouts/plans');
  }

  function formatDuration(sessStart: string, sessEnd: string | null): string {
    if (!sessStart || !sessEnd) return '—';
    const mins = Math.round((new Date(sessEnd).getTime() - new Date(sessStart).getTime()) / 60000);
    return `${mins} Min`;
  }
</script>

<svelte:head><title>Salus — {plan?.name ?? 'Workout-Plan'}</title></svelte:head>

{#if loading}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else if plan && planExercises}
  <div class="space-y-6">
    <!-- Breadcrumb Navigation -->
    <div>
      <a
        href="/workouts/plans"
        class="inline-flex items-center gap-1.5 text-xs font-bold text-text-muted transition-colors hover:text-text-main"
      >
        <Icon name="arrow_back" class="text-sm" />
        <span>Zurück zu Workouts</span>
      </a>
    </div>

    <!-- Hero Header -->
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div class="space-y-2">
        <div class="flex flex-wrap items-center gap-2">
          <h1 class="text-2xl font-extrabold tracking-tight text-text-main sm:text-3xl">
            {plan.name}
          </h1>
          <Badge variant={isSystem ? 'primary' : 'activity'}>
            {isSystem ? 'Standard-Vorlage' : 'Individueller Plan'}
          </Badge>
          <span
            class="inline-flex items-center gap-1 rounded-full border border-border-subtle bg-surface-100 px-2.5 py-0.5 text-xs font-semibold text-text-muted select-none"
          >
            <Icon name="timer" class="text-xs" />
            <span>{estimatedDuration}</span>
          </span>
        </div>
        <p class="max-w-2xl text-xs text-text-muted sm:text-sm">
          {plan.description ||
            'Strukturierter Trainingsplan mit progressiver Satz- und Wiederholungssteuerung.'}
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        {#if isSystem}
          <button
            type="button"
            onclick={duplicateAsTemplate}
            disabled={duplicating}
            class="flex cursor-pointer items-center gap-1.5 rounded-2xl border border-border-subtle bg-surface-0 px-4 py-2.5 text-xs font-bold text-text-main shadow-xs transition-all hover:bg-surface-50 active:scale-95 disabled:opacity-50"
          >
            <Icon name="content_copy" class="text-sm text-text-muted" />
            <span>{duplicating ? 'Kopiere...' : 'Als eigene Vorlage kopieren'}</span>
          </button>
        {:else}
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
          onclick={startSession}
          disabled={starting}
          class="flex cursor-pointer items-center gap-2 rounded-2xl bg-primary px-5 py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-90 active:scale-95 disabled:opacity-50"
        >
          <Icon name="play_arrow" class="text-base" />
          <span>{starting ? 'Startet...' : 'Training starten'}</span>
        </button>
      </div>
    </div>

    <!-- KPI Metric Cards Grid -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <div class="flex items-center gap-1.5 text-xs font-bold text-text-muted">
          <Icon name="fitness_center" class="text-sm text-primary" />
          <span>Übungen</span>
        </div>
        <div class="mt-2 text-xl font-extrabold text-text-main tabular-nums">
          {planExercises.length}
        </div>
        <p class="mt-0.5 text-[0.6875rem] text-text-soft">Geplante Übungseinheiten</p>
      </div>

      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <div class="flex items-center gap-1.5 text-xs font-bold text-text-muted">
          <Icon name="timer" class="text-sm text-activity" />
          <span>Geschätzte Zeit</span>
        </div>
        <div class="mt-2 text-xl font-extrabold text-text-main tabular-nums">
          {estimatedDuration}
        </div>
        <p class="mt-0.5 text-[0.6875rem] text-text-soft">Inkl. Pausenzeiten</p>
      </div>

      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <div class="flex items-center gap-1.5 text-xs font-bold text-text-muted">
          <Icon name="layers" class="text-sm text-emerald-500" />
          <span>Gesamtsätze</span>
        </div>
        <div class="mt-2 text-xl font-extrabold text-text-main tabular-nums">
          {totalTargetSets} Sätze
        </div>
        <p class="mt-0.5 text-[0.6875rem] text-text-soft">Geplantes Arbeitsvolumen</p>
      </div>

      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <div class="flex items-center gap-1.5 text-xs font-bold text-text-muted">
          <Icon name="history" class="text-sm text-amber-500" />
          <span>Absolviert</span>
        </div>
        <div class="mt-2 text-xl font-extrabold text-text-main tabular-nums">
          {sessions?.length ?? 0}×
        </div>
        <p class="mt-0.5 text-[0.6875rem] text-text-soft">Abgeschlossene Einheiten</p>
      </div>
    </div>

    <!-- Two Column Layout: Exercises & 2D Vector Heatmap / History -->
    <div class="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <!-- Left Column: Exercises Breakdown -->
      <div class="space-y-4">
        <div class="rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <div class="mb-4 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Icon name="format_list_numbered" class="text-primary" />
              <h2 class="text-base font-extrabold text-text-main">Geplante Übungsreihenfolge</h2>
            </div>
            <span class="text-xs font-bold text-text-muted">{planExercises.length} Übungen</span>
          </div>

          {#if planExercises.length === 0}
            <EmptyState
              title="Keine Übungen im Plan"
              description="Diesem Workout-Plan wurden noch keine Übungen hinzugefügt."
              icon="fitness_center"
            />
          {:else}
            <div class="space-y-3">
              {#each planExercises as pe, idx (pe.id)}
                {@const ex = exercises?.get(pe.exercise_id)}
                <div
                  class="group flex flex-col justify-between gap-3 rounded-2xl border border-border-subtle bg-surface-50 p-4 transition-all hover:border-primary/50 hover:bg-surface-0 sm:flex-row sm:items-center"
                >
                  <div class="flex min-w-0 items-start gap-3.5">
                    <span
                      class="flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-surface-200/80 font-mono text-xs font-extrabold text-text-muted"
                    >
                      {String(idx + 1).padStart(2, '0')}
                    </span>

                    <div class="min-w-0">
                      <a
                        href="/workouts/exercises/{pe.exercise_id}"
                        class="truncate text-sm font-extrabold text-text-main no-underline transition-colors group-hover:text-primary hover:underline"
                      >
                        {ex?.name ?? 'Übung'}
                      </a>
                      <div class="mt-1 flex flex-wrap items-center gap-1.5 text-xs text-text-muted">
                        <span
                          class="inline-flex items-center gap-1 rounded-md bg-surface-100 px-1.5 py-0.5 text-[0.6875rem] font-semibold text-text-soft"
                        >
                          <Icon name="fitness_center" class="text-[10px]" />
                          <span class="capitalize">{ex?.equipment || 'Frei'}</span>
                        </span>
                        <span>·</span>
                        <span class="text-[0.6875rem] font-medium text-text-soft">
                          {parseMuscles(ex?.primary_muscles).map(formatMuscleName).join(', ') ||
                            'Ganzkörper'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Exercise Target Specs Grid -->
                  <div
                    class="flex shrink-0 flex-wrap items-center gap-2 border-t border-border-subtle pt-2 sm:border-t-0 sm:pt-0"
                  >
                    <div
                      class="rounded-xl border border-border-subtle bg-surface-0 px-3 py-1.5 text-right shadow-2xs"
                    >
                      <span class="block text-[0.625rem] font-bold text-text-soft uppercase"
                        >Ziel</span
                      >
                      <span class="font-mono text-xs font-extrabold text-text-main tabular-nums">
                        {pe.target_sets || 3} &times; {pe.target_reps || 8} Wdh
                      </span>
                    </div>

                    <div
                      class="rounded-xl border border-border-subtle bg-surface-0 px-2.5 py-1.5 text-center shadow-2xs"
                    >
                      <span class="block text-[0.625rem] font-bold text-text-soft uppercase"
                        >RPE</span
                      >
                      <span class="font-mono text-xs font-extrabold text-primary tabular-nums">
                        @{pe.target_rpe ?? 8}
                      </span>
                    </div>

                    <div
                      class="rounded-xl border border-border-subtle bg-surface-0 px-2.5 py-1.5 text-center shadow-2xs"
                    >
                      <span class="block text-[0.625rem] font-bold text-text-soft uppercase"
                        >Pause</span
                      >
                      <span class="font-mono text-xs font-extrabold text-text-muted tabular-nums">
                        {restSeconds(pe)}s
                      </span>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>

      <!-- Right Column: Reusable 2D Muscle Heatmap & History -->
      <div class="space-y-6">
        <!-- Canonical 2D Anatomical Heatmap & Matrix Component -->
        <MuscleHeatmap2D {planExercises} />

        <!-- Session History Card -->
        <div class="rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <div class="mb-3 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Icon name="history" class="text-primary" />
              <h2 class="text-base font-extrabold text-text-main">Trainingshistorie</h2>
            </div>
            <span class="text-xs font-bold text-text-muted">{sessions?.length ?? 0} Einheiten</span>
          </div>

          {#if !sessions || sessions.length === 0}
            <div class="py-6 text-center text-xs text-text-muted">
              <Icon name="history" size="lg" class="mx-auto text-text-muted opacity-60" />
              <p class="mt-2 font-bold text-text-main">Noch kein Training absolviert</p>
              <p class="mt-0.5 text-[0.6875rem]">
                Starte das Workout, um deinen Fortschritt aufzuzeichnen.
              </p>
            </div>
          {:else}
            <div class="space-y-2">
              {#each sessions.slice(0, 5) as sess (sess.id)}
                <a
                  href="/workouts/sessions/{sess.id}"
                  class="flex items-center justify-between rounded-xl border border-border-subtle bg-surface-50 p-3 no-underline transition-all hover:border-primary hover:bg-surface-0"
                >
                  <div>
                    <span class="block text-xs font-extrabold text-text-main">
                      {new Date(sess.completed_at ?? sess.started_at).toLocaleDateString('de-DE', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric'
                      })}
                    </span>
                    <span class="text-[0.6875rem] text-text-muted">
                      {formatDuration(sess.started_at, sess.completed_at)} · {sessionVolume(
                        logs,
                        sess.id
                      ).toFixed(0)} kg Volumen
                    </span>
                  </div>
                  <Icon name="chevron_right" class="text-sm text-text-muted" />
                </a>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
{:else}
  <EmptyState
    title="Workout-Plan nicht gefunden"
    description="Der gesuchte Trainingsplan existiert nicht oder wurde gelöscht."
    icon="assignment"
  />
{/if}

<ConfirmDialog
  open={deleteOpen}
  title="Workout-Plan löschen?"
  message="Möchtest du diesen Trainingsplan wirklich unwiderruflich löschen?"
  confirmLabel="Plan löschen"
  variant="danger"
  onconfirm={handleDelete}
  oncancel={() => (deleteOpen = false)}
/>
