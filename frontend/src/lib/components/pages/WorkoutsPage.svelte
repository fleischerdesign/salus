<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Input from '../ui/Input.svelte';
  import StatusDot from '../ui/StatusDot.svelte';
  import ActiveWorkoutSession from '../workouts/ActiveWorkoutSession.svelte';
  import MuscleHeatmap2D from '../track/MuscleHeatmap2D.svelte';
  import Exercise1RMChart from '../track/Exercise1RMChart.svelte';
  import WorkoutSplitCard from '../track/WorkoutSplitCard.svelte';
  import WorkoutPlanEditorModal from '../workouts/WorkoutPlanEditorModal.svelte';
  import CreateExerciseModal from '../workouts/CreateExerciseModal.svelte';
  import type {
    WorkoutPlan,
    WorkoutHistorySession,
    LiveWorkoutExercise,
    DetailedMuscleKey
  } from '../../types/workouts';
  import {
    MUSCLE_GROUPS,
    DETAILED_MUSCLE_MAP,
    parseMuscles,
    resolveMuscleGroup
  } from '../../types/workouts';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { startWorkout, completeWorkout } from '$lib/mutations/workout';
  import { deleteExercise } from '$lib/mutations/exercise';

  export type WorkoutTab = 'active' | 'plans' | 'sessions' | 'exercises';

  let { initialTab = 'plans' } = $props<{
    initialTab?: WorkoutTab;
  }>();

  let activeTab = $derived<WorkoutTab>(
    page.url.pathname.includes('/workouts/active')
      ? 'active'
      : page.url.pathname.includes('/workouts/sessions')
        ? 'sessions'
        : page.url.pathname.includes('/workouts/exercises')
          ? 'exercises'
          : initialTab
  );

  // 1. Reactive Query for Plans, Active Session & Past Sessions
  const workoutsQuery = useQuery(async () => {
    const [plans, planExercises, sessions, logs, exercises] = await Promise.all([
      db.workout_plan.toArray(),
      db.workout_plan_exercise.toArray(),
      db.workout_session.toArray(),
      db.workout_log_entry.toArray(),
      db.exercise.toArray()
    ]);

    const validPlans = plans.filter((p) => !p.deleted_at);
    const validSessions = sessions.filter((s) => !s.deleted_at && s.completed_at);
    const activeSession = sessions.find((s) => !s.deleted_at && !s.completed_at) ?? null;
    const validExercises = exercises.filter((e) => !e.deleted_at);
    const exMap = new Map(validExercises.map((e) => [e.id, e]));

    // Format plans
    const formattedPlans: WorkoutPlan[] = validPlans.map((p) => {
      const pExs = planExercises
        .filter((pe) => pe.plan_id === p.id && !pe.deleted_at)
        .sort((a, b) => a.sequence - b.sequence);

      return {
        id: p.id,
        name: p.name,
        split: 'Individueller Split',
        subtitle: p.description || 'Ganzkörper / Split',
        exercisesCount: pExs.length,
        estimatedDuration: `${pExs.length * 10 || 45} Min`,
        targetVolume: 'Individuell',
        targetVolumeKg: 0,
        exercises: pExs.map((pe) => {
          const ex = exMap.get(pe.exercise_id);
          return {
            name: ex?.name || 'Übung',
            muscle: (ex?.primary_muscles as unknown as 'Brust') || 'Brust',
            targetSets: pe.target_sets || 3,
            targetReps: `${pe.target_reps || 10} Wdh`,
            targetRir: 2
          };
        })
      };
    });

    // Format active session exercises if active
    let activePlanName = 'Freies Training';
    let activeExercises: LiveWorkoutExercise[] = [];
    if (activeSession) {
      const plan = validPlans.find((p) => p.id === activeSession.plan_id);
      if (plan) {
        activePlanName = plan.name;
        const pExs = planExercises
          .filter((pe) => pe.plan_id === plan.id && !pe.deleted_at)
          .sort((a, b) => a.sequence - b.sequence);

        activeExercises = pExs.map((pe) => {
          const ex = exMap.get(pe.exercise_id);
          return {
            id: `ex_${pe.id}`,
            name: ex?.name || 'Übung',
            muscleGroup: (ex?.primary_muscles as unknown as 'Brust') || 'Brust',
            category: 'Grundübung',
            equipment: (ex?.equipment as unknown as 'Langhantel') || 'Langhantel',
            e1RM: 100,
            sets: Array.from({ length: pe.target_sets || 3 }, (_, sIdx) => ({
              id: `set_${pe.id}_${sIdx + 1}`,
              setNumber: sIdx + 1,
              type: 'normal',
              previous: { weightKg: 50, reps: 10 },
              weightKg: 50,
              reps: pe.target_reps || 10,
              rpe: 8,
              completed: false
            }))
          };
        });
      }
    }

    // Format past sessions
    const formattedSessions: WorkoutHistorySession[] = validSessions.map((s) => {
      const plan = validPlans.find((p) => p.id === s.plan_id);
      const sessionLogs = logs.filter((l) => l.session_id === s.id && !l.deleted_at);
      const totalVolumeKg = sessionLogs.reduce((sum, l) => sum + l.weight * l.reps, 0);
      const durationMs = s.completed_at
        ? new Date(s.completed_at).getTime() - new Date(s.started_at).getTime()
        : 0;
      const durationMin = Math.round(durationMs / 60000) || 45;

      return {
        id: s.id,
        date: new Date(s.started_at).toLocaleDateString('de-DE', {
          weekday: 'long',
          day: 'numeric',
          month: 'long',
          year: 'numeric'
        }),
        planName: plan?.name || 'Freies Workout',
        duration: `${durationMin} Min`,
        durationMinutes: durationMin,
        tonnage: `${totalVolumeKg.toLocaleString('de-DE')} kg`,
        tonnageKg: totalVolumeKg,
        setsCount: sessionLogs.length,
        prCount: 0,
        prNote: '',
        avgHeartRate: 140,
        activeKcal: Math.round(durationMin * 8),
        exercises: []
      };
    });

    return {
      plans: formattedPlans,
      sessions: formattedSessions,
      allExercises: validExercises,
      activeSession,
      activePlanName,
      activeExercises
    };
  });

  const workoutData = $derived(workoutsQuery.value);
  const savedPlans = $derived(workoutData?.plans ?? []);
  const pastSessions = $derived(workoutData?.sessions ?? []);
  const dbExercises = $derived(workoutData?.allExercises ?? []);
  const activeSession = $derived(workoutData?.activeSession ?? null);
  const activePlanName = $derived(workoutData?.activePlanName ?? 'Freies Training');
  const activeExercises = $derived(workoutData?.activeExercises ?? []);

  // Plan Editor Modal State
  let isPlanEditorOpen = $state(false);
  let planToEdit = $state<WorkoutPlan | null>(null);

  // Create Exercise Modal State
  let isCreateExerciseOpen = $state(false);

  function openCreatePlan() {
    planToEdit = null;
    isPlanEditorOpen = true;
  }

  function openEditPlan(plan: WorkoutPlan) {
    planToEdit = plan;
    isPlanEditorOpen = true;
  }

  function handleSavePlan(_saved: WorkoutPlan) {
    isPlanEditorOpen = false;
  }

  async function handleStartPlan(planId?: string) {
    await startWorkout(planId ?? null);
    goto('/workouts/active');
  }

  async function handleFinishActiveWorkout(stats: {
    duration: string;
    tonnageKg: number;
    totalSets: number;
  }) {
    if (activeSession) {
      await completeWorkout(
        activeSession.id,
        `Abgeschlossen in ${stats.duration}. Gesamttonnage: ${stats.tonnageKg} kg`
      );
    }
    goto('/workouts/sessions');
  }

  // ─── EXERCISE DATABASE STATE ───
  let selectedMuscle = $state<string>('all');
  let exerciseSearch = $state<string>('');

  const muscleFilterOptions = [
    { value: 'all', label: 'Alle Muskeln' },
    ...MUSCLE_GROUPS.map((g) => ({ value: g, label: g }))
  ];

  let filteredExercises = $derived(
    dbExercises.filter((ex) => {
      const matchM =
        selectedMuscle === 'all' ||
        parseMuscles(ex.primary_muscles).some(
          (m) =>
            resolveMuscleGroup(m) === selectedMuscle ||
            m.toLowerCase() === selectedMuscle.toLowerCase()
        ) ||
        parseMuscles(ex.secondary_muscles).some(
          (m) =>
            resolveMuscleGroup(m) === selectedMuscle ||
            m.toLowerCase() === selectedMuscle.toLowerCase()
        );
      const matchQ =
        !exerciseSearch.trim() || ex.name.toLowerCase().includes(exerciseSearch.toLowerCase());
      return matchM && matchQ;
    })
  );

  async function handleDeleteCustomExercise(id: string) {
    if (confirm('Möchtest du diese Übung wirklich aus deinem Katalog löschen?')) {
      await deleteExercise(id);
    }
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Krafttraining und Workouts</h1>
      <p class="mt-0.5 text-sm text-[var(--text-muted)]">
        Live-Einheiten, progressive Überlastung, Periodisierung und Kraftkurven
      </p>
    </div>
    <div class="flex items-center gap-2">
      {#if !activeSession}
        <button
          type="button"
          onclick={openCreatePlan}
          class="flex cursor-pointer items-center gap-1.5 rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-md transition-all hover:opacity-90"
        >
          <span>+ Neuen Plan erstellen</span>
        </button>
      {/if}
    </div>
  </div>

  <!-- Primary Sub-Navigation Tabs (Live-Einheit is ONLY shown when a session is active!) -->
  <div
    class="no-scrollbar flex gap-2 overflow-x-auto rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-1.5"
  >
    <a
      href="/workouts/plans"
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
      'plans'
        ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="show_chart" class="text-[var(--color-primary)]" />
      <span>Trainingspläne</span>
      <Badge variant="default" class="text-[0.625rem]">{savedPlans.length}</Badge>
    </a>

    {#if activeSession}
      <a
        href="/workouts/active"
        class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
        'active'
          ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
          : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        <StatusDot status="active" pulse={true} size="sm" />
        <span>Live-Einheit</span>
        <Badge variant="activity" class="text-[0.625rem]">Aktiv</Badge>
      </a>
    {/if}

    <a
      href="/workouts/sessions"
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
      'sessions'
        ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="history" class="text-[var(--color-primary)]" />
      <span>Historie</span>
      <Badge variant="default" class="text-[0.625rem]">{pastSessions.length}</Badge>
    </a>

    <a
      href="/workouts/exercises"
      class="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
      'exercises'
        ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm'
        : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="fitness_center" class="text-[var(--color-primary)]" />
      <span>Übungskatalog &amp; 1RM</span>
      <Badge variant="default" class="text-[0.625rem]">{dbExercises.length}</Badge>
    </a>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- TAB 1: TRAININGSPLÄNE & PERIODISIERUNG                      -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if activeTab === 'plans'}
    <div class="space-y-6">
      <!-- Free Workout Quick-Start Card -->
      <div
        class="flex flex-col items-start justify-between gap-4 rounded-3xl border-2 border-dashed border-[var(--color-primary)]/40 bg-[var(--bg-surface-0)] p-5 shadow-xs transition-all hover:border-[var(--color-primary)] sm:flex-row sm:items-center"
      >
        <div class="flex items-center gap-3.5">
          <div
            class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
          >
            <Icon name="bolt" size="md" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-sm font-extrabold text-[var(--text-main)] sm:text-base">
                Freies Training (ohne Vorlage)
              </h3>
              <Badge variant="primary" class="text-[0.625rem]">Spontan</Badge>
            </div>
            <p class="mt-0.5 text-xs text-[var(--text-muted)]">
              Starte eine leere Session und füge deine Übungen, Sätze und Gewichte flexibel während
              des Trainings hinzu.
            </p>
          </div>
        </div>

        <button
          type="button"
          onclick={() => handleStartPlan()}
          class="flex shrink-0 cursor-pointer items-center gap-1.5 rounded-2xl bg-[var(--color-primary)] px-4 py-2.5 text-xs font-bold whitespace-nowrap text-white shadow-md transition-all hover:opacity-90"
        >
          <span>+ Freies Training starten &rarr;</span>
        </button>
      </div>

      <WorkoutSplitCard />

      <!-- Saved Plan Templates List -->
      <div
        class="rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
      >
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">
              Deine Trainingsplan-Vorlagen
            </h2>
            <p class="mt-0.5 text-xs text-[var(--text-muted)]">
              Strukturierte Pläne mit progressivem Belastungsziel
            </p>
          </div>
          <button
            type="button"
            onclick={openCreatePlan}
            class="flex cursor-pointer items-center gap-1.5 rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-sm transition-all hover:opacity-90"
          >
            <span>+ Neuen Plan erstellen</span>
          </button>
        </div>

        {#if savedPlans.length === 0}
          <div class="space-y-2 py-8 text-center text-xs text-[var(--text-muted)]">
            <Icon
              name="fitness_center"
              size="lg"
              class="mx-auto text-[var(--text-muted)] opacity-60"
            />
            <p class="text-xs font-bold text-[var(--text-main)]">Keine Trainingspläne vorhanden</p>
            <p class="mx-auto max-w-sm text-[0.6875rem]">
              Erstelle strukturierte Hypertrophie- und Kraftpläne mit individueller Satz- und
              Wiederholungssteuerung.
            </p>
          </div>
        {:else}
          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            {#each savedPlans as plan}
              <div
                class="flex flex-col justify-between space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 transition-all hover:border-[var(--color-primary)]"
              >
                <div>
                  <div class="mb-2 flex items-start justify-between">
                    <div>
                      <h3 class="text-sm font-extrabold text-[var(--text-main)]">{plan.name}</h3>
                      <span class="text-xs text-[var(--text-muted)]">{plan.split}</span>
                    </div>
                    <Badge variant="activity">{plan.estimatedDuration}</Badge>
                  </div>

                  <div class="my-3 space-y-1.5">
                    <span
                      class="block text-[0.6875rem] font-bold text-[var(--text-soft)] uppercase"
                    >
                      Enthaltene Übungen ({plan.exercisesCount}):
                    </span>
                    {#each plan.exercises as ex}
                      <div
                        class="flex items-center justify-between text-xs text-[var(--text-main)]"
                      >
                        <div class="flex items-center gap-1.5">
                          <span class="h-1.5 w-1.5 rounded-full bg-[var(--color-activity)]"></span>
                          <span class="font-semibold">{ex.name}</span>
                        </div>
                        <span class="text-[0.6875rem] text-[var(--text-muted)] tabular-nums"
                          >{ex.targetSets} &times; {ex.targetReps}</span
                        >
                      </div>
                    {/each}
                  </div>
                </div>

                <div
                  class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-3"
                >
                  <button
                    type="button"
                    onclick={() => openEditPlan(plan)}
                    class="cursor-pointer text-xs font-bold text-[var(--text-muted)] hover:text-[var(--color-primary)]"
                  >
                    Bearbeiten
                  </button>
                  <button
                    type="button"
                    onclick={() => handleStartPlan(plan.id)}
                    class="cursor-pointer rounded-xl bg-[var(--color-primary)] px-3.5 py-1.5 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
                  >
                    Plan starten &rarr;
                  </button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 2: LIVE WORKOUT RECORDER (Nur sichtbar bei Session)    -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'active' && activeSession}
    <ActiveWorkoutSession
      sessionId={activeSession.id}
      planName={activePlanName}
      initialExercises={activeExercises}
      startedAt={activeSession.started_at}
      onfinish={handleFinishActiveWorkout}
    />

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 3: VERGANGENE EINHEITEN (HISTORIE)                     -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'sessions'}
    {#if pastSessions.length === 0}
      <div
        class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-8 text-center shadow-xs"
      >
        <div
          class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
        >
          <Icon name="history" size="lg" />
        </div>
        <h3 class="text-base font-bold text-[var(--text-main)]">
          Noch keine absolvierten Workouts
        </h3>
        <p class="mx-auto max-w-sm text-xs text-[var(--text-muted)]">
          Starte dein erstes Training, um Trainingsvolumen, Tonnage und 1RM-Steigerungen zu
          protokollieren.
        </p>
      </div>
    {:else}
      <div class="space-y-4">
        {#each pastSessions as s}
          <div
            class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
          >
            <div class="mb-2 flex flex-wrap items-center justify-between gap-2">
              <div>
                <h3 class="text-base font-extrabold text-[var(--text-main)]">{s.planName}</h3>
                <p class="mt-0.5 text-xs text-[var(--text-muted)]">
                  {s.date} &bull; {s.duration} Dauer &bull; {s.activeKcal} kcal
                </p>
              </div>

              <div class="flex items-center gap-4">
                <div>
                  <span class="block text-right text-xs font-semibold text-[var(--text-muted)]"
                    >Volumen-Tonnage</span
                  >
                  <span
                    class="block text-right text-base font-extrabold text-[var(--color-activity)] tabular-nums"
                    >{s.tonnage}</span
                  >
                </div>
                <Badge variant="default" class="font-bold">{s.setsCount} Sätze</Badge>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- TAB 4: ÜBUNGSKATALOG & 1RM ANALYTIK                        -->
    <!-- ═══════════════════════════════════════════════════════════ -->
  {:else if activeTab === 'exercises'}
    <div class="space-y-6">
      <!-- Top Section: 1RM Chart & Muscle Heatmap -->
      <div class="grid grid-cols-1 gap-5 lg:grid-cols-12">
        <div class="lg:col-span-8">
          <Exercise1RMChart />
        </div>
        <div class="lg:col-span-4">
          <MuscleHeatmap2D />
        </div>
      </div>

      <!-- Comprehensive Exercise Catalog Table & Search -->
      <div
        class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
      >
        <div
          class="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border-subtle)]/60 pb-2"
        >
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">
              Übungskatalog &amp; Bewegungsdatenbank
            </h2>
            <p class="mt-0.5 text-xs text-[var(--text-muted)]">
              Offiziell verifizierte Grundübungen und benutzerdefinierte Kreationen
            </p>
          </div>
          <button
            type="button"
            onclick={() => (isCreateExerciseOpen = true)}
            class="flex cursor-pointer items-center gap-1.5 rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-sm transition-all hover:opacity-90"
          >
            <span>+ Eigene Übung anlegen</span>
          </button>
        </div>

        <!-- Search & Muscle Filters -->
        <div class="flex flex-col items-center justify-between gap-3 md:flex-row">
          <div class="w-full md:w-80">
            <Input icon="search" placeholder="Übung durchsuchen..." bind:value={exerciseSearch} />
          </div>

          <div class="no-scrollbar flex w-full gap-1.5 overflow-x-auto md:w-auto">
            {#each muscleFilterOptions as m}
              <button
                type="button"
                onclick={() => (selectedMuscle = m.value)}
                class="cursor-pointer rounded-xl px-3 py-1.5 text-xs font-semibold whitespace-nowrap transition-all {selectedMuscle ===
                m.value
                  ? 'bg-[var(--color-primary)] font-bold text-white'
                  : 'border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
              >
                {m.label}
              </button>
            {/each}
          </div>
        </div>

        <!-- Exercises List / Grid -->
        {#if filteredExercises.length === 0}
          <div class="space-y-2 py-10 text-center text-xs text-[var(--text-muted)]">
            <Icon name="search" size="lg" class="mx-auto text-[var(--text-muted)] opacity-60" />
            <p class="text-xs font-bold text-[var(--text-main)]">
              Keine passenden Übungen gefunden
            </p>
            <p class="mx-auto max-w-sm text-[0.6875rem]">
              Erstelle deine eigene Übung mit individueller Muskel- und Equipment-Zuordnung.
            </p>
            <button
              type="button"
              onclick={() => (isCreateExerciseOpen = true)}
              class="cursor-pointer rounded-2xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-sm transition-all hover:opacity-90"
            >
              + Eigene Übung anlegen
            </button>
          </div>
        {:else}
          <div class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
            {#each filteredExercises as ex}
              <div
                class="flex flex-col justify-between space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 transition-all hover:border-[var(--border-strong)]"
              >
                <div>
                  <div class="mb-1.5 flex items-start justify-between gap-2">
                    <a
                      href="/workouts/exercises/{ex.id}"
                      class="text-sm leading-snug font-extrabold text-[var(--text-main)] hover:text-[var(--color-primary)] transition-colors"
                    >
                      {ex.name}
                    </a>
                    <Badge
                      variant={ex.user_id ? 'activity' : 'default'}
                      class="shrink-0 text-[0.625rem]"
                    >
                      {ex.user_id ? 'Benutzerdefiniert' : 'System'}
                    </Badge>
                  </div>

                  <!-- Muscle Badges & Equipment -->
                  <div class="space-y-1.5 pt-0.5">
                    <div class="flex flex-wrap items-center gap-1.5 text-xs">
                      {#each parseMuscles(ex.primary_muscles) as pKey}
                        {@const pDef = DETAILED_MUSCLE_MAP[pKey as DetailedMuscleKey]}
                        <span
                          class="inline-flex items-center gap-1 rounded-md bg-[var(--color-primary-soft)] px-2 py-0.5 text-[11px] font-bold text-[var(--color-primary)]"
                          title={pDef?.latin}
                        >
                          {pDef?.name || pKey}
                        </span>
                      {/each}

                      {#each parseMuscles(ex.secondary_muscles) as sKey}
                        {@const sDef = DETAILED_MUSCLE_MAP[sKey as DetailedMuscleKey]}
                        <span
                          class="inline-flex items-center gap-1 rounded-md bg-[#818cf8]/10 px-2 py-0.5 text-[11px] font-medium text-[#818cf8]"
                          title={`Synergist: ${sDef?.latin || sKey}`}
                        >
                          {sDef?.name || sKey}
                        </span>
                      {/each}
                    </div>

                    <div class="flex items-center gap-1.5 text-[11px] text-[var(--text-muted)]">
                      <Icon name="fitness_center" class="text-xs" />
                      <span class="capitalize">{ex.equipment || 'Frei'}</span>
                    </div>
                  </div>

                  {#if ex.description || ex.instructions}
                    <p
                      class="mt-2 line-clamp-2 text-[0.6875rem] leading-relaxed text-[var(--text-muted)]"
                    >
                      {ex.description || ex.instructions}
                    </p>
                  {/if}
                </div>

                <div
                  class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-2.5 text-xs"
                >
                  <span class="font-mono text-[0.6875rem] text-[var(--text-muted)]">
                    Pause: {ex.suggested_rest_seconds || 90}s
                  </span>
                  <div class="flex items-center gap-2">
                    <a
                      href="/workouts/exercises/{ex.id}"
                      class="text-xs font-bold text-[var(--color-primary)] hover:underline"
                    >
                      Details &rarr;
                    </a>
                    {#if ex.user_id}
                      <button
                        type="button"
                        onclick={() => handleDeleteCustomExercise(ex.id)}
                        class="cursor-pointer text-xs font-bold text-[var(--text-muted)] hover:text-rose-500"
                      >
                        Löschen
                      </button>
                    {/if}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- Workout Plan Editor Modal -->
  <WorkoutPlanEditorModal
    open={isPlanEditorOpen}
    plan={planToEdit}
    onsave={handleSavePlan}
    onclose={() => (isPlanEditorOpen = false)}
  />

  <!-- Create Exercise Modal -->
  <CreateExerciseModal open={isCreateExerciseOpen} onclose={() => (isCreateExerciseOpen = false)} />
</div>
