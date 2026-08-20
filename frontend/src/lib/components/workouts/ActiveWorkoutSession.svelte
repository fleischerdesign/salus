<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import PlateCalculatorModal from './PlateCalculatorModal.svelte';
  import WorkoutRestTimerBar from './WorkoutRestTimerBar.svelte';
  import type { LiveWorkoutExercise, LiveWorkoutSet, SetType } from '../../types/workouts';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { logSet } from '$lib/mutations/workout';

  let {
    sessionId = null,
    planName = 'Freies Training',
    initialExercises = [],
    startedAt = null,
    onfinish
  } = $props<{
    sessionId?: string | null;
    planName?: string;
    initialExercises?: LiveWorkoutExercise[];
    startedAt?: string | null;
    onfinish?: (stats: { duration: string; tonnageKg: number; totalSets: number }) => void;
  }>();

  // Multi-Exercise Active Session State
  let exercises = $state<LiveWorkoutExercise[]>([]);
  let isInitialized = $state(false);

  // Helper to extract the catalog Exercise ID reliably
  function getCatalogId(ex: LiveWorkoutExercise): string {
    if (ex.exerciseId) return ex.exerciseId;
    if (ex.id.startsWith('inst_')) {
      const parts = ex.id.split('_');
      return parts[1] || ex.id;
    }
    if (ex.id.startsWith('ex_')) {
      return ex.id.replace('ex_', '');
    }
    return ex.id;
  }

  // Query catalog exercises for adding & details
  const catalogQuery = useQuery(async () => {
    const list = await db.exercise.toArray();
    return list.filter((e) => !e.deleted_at);
  });
  const catalogExercises = $derived(catalogQuery.value ?? []);
  const catalogMap = $derived(new Map(catalogExercises.map((e) => [e.id, e])));

  // Query historical logs to provide ghosted targets & progressive overload detection
  const historicalLogsQuery = useQuery(async () => {
    const logs = await db.workout_set.toArray();
    const validLogs = logs.filter(
      (l) => !l.deleted_at && (sessionId ? l.session_id !== sessionId : true)
    );

    // Group by exercise_id -> sort by date desc -> get latest sets
    const exHistMap = new Map<string, { weight: number; reps: number; rpe?: number }[]>();
    for (const log of validLogs) {
      if (!exHistMap.has(log.exercise_id)) {
        exHistMap.set(log.exercise_id, []);
      }
      exHistMap.get(log.exercise_id)!.push({
        weight: log.weight,
        reps: log.reps,
        rpe: log.rpe ?? undefined
      });
    }
    return exHistMap;
  });
  const historicalLogs = $derived(historicalLogsQuery.value ?? new Map());

  $effect(() => {
    if (!isInitialized) {
      if (sessionId && typeof window !== 'undefined') {
        const saved = localStorage.getItem(`salus_workout_draft_${sessionId}`);
        if (saved) {
          try {
            const parsed: LiveWorkoutExercise[] = JSON.parse(saved);
            // Ensure all loaded exercises have unique instance IDs
            exercises = parsed.map((e, idx) => ({
              ...e,
              id: e.id && !e.id.startsWith('inst_') ? `inst_${e.id}_${idx}` : e.id || `inst_${idx}`
            }));
            isInitialized = true;
            return;
          } catch (e) {
            void e;
          }
        }
      }
      if (initialExercises && initialExercises.length > 0) {
        exercises = (initialExercises as LiveWorkoutExercise[]).map(
          (e: LiveWorkoutExercise, idx: number) => ({
            ...e,
            id: `inst_${e.id}_${idx}`
          })
        );
      }
      isInitialized = true;
    }
  });

  // Auto-persist active session draft to localStorage
  $effect(() => {
    if (sessionId && isInitialized && typeof window !== 'undefined') {
      localStorage.setItem(`salus_workout_draft_${sessionId}`, JSON.stringify(exercises));
    }
  });

  // Live Elapsed Workout Timer (Ticking in seconds from actual start)
  let elapsedSeconds = $state(0);

  $effect(() => {
    elapsedSeconds = startedAt
      ? Math.max(0, Math.floor((Date.now() - new Date(startedAt).getTime()) / 1000))
      : 0;
    const timer = setInterval(() => {
      elapsedSeconds++;
    }, 1000);
    return () => clearInterval(timer);
  });

  let formattedDuration = $derived.by(() => {
    const hrs = Math.floor(elapsedSeconds / 3600);
    const mins = Math.floor((elapsedSeconds % 3600) / 60);
    const secs = elapsedSeconds % 60;
    if (hrs > 0) {
      return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  });

  // Total Completed Tonnage (Sum of all weight * reps of completed sets)
  let totalTonnageKg = $derived.by(() => {
    let sum = 0;
    for (const ex of exercises) {
      for (const set of ex.sets) {
        if (set.completed) {
          sum += set.weightKg * set.reps;
        }
      }
    }
    return sum;
  });

  let completedSetsCount = $derived.by(() => {
    let count = 0;
    for (const ex of exercises) {
      for (const set of ex.sets) {
        if (set.completed) count++;
      }
    }
    return count;
  });

  let totalSetsCount = $derived.by(() => {
    let count = 0;
    for (const ex of exercises) {
      count += ex.sets.length;
    }
    return count;
  });

  // Plate Calculator Modal State
  let isPlateCalcOpen = $state(false);
  let activeSetForPlateCalc = $state<LiveWorkoutSet | null>(null);
  let activeMenuExId = $state<string | null>(null);

  function openPlateCalcForExercise(ex: LiveWorkoutExercise) {
    const targetSet = ex.sets.find((s) => !s.completed) || ex.sets[0];
    if (targetSet) {
      activeSetForPlateCalc = targetSet;
      isPlateCalcOpen = true;
    }
  }

  function handleApplyPlateWeight(weight: number) {
    if (activeSetForPlateCalc) {
      activeSetForPlateCalc.weightKg = weight;
    }
  }

  // Rest Timer State
  let isRestTimerRunning = $state(false);
  let restTimerSeconds = $state(90);

  async function toggleSetCompletion(ex: LiveWorkoutExercise, set: LiveWorkoutSet) {
    set.completed = !set.completed;
    if (set.completed) {
      const cleanExId = getCatalogId(ex);
      const catEx = catalogMap.get(cleanExId);
      restTimerSeconds = catEx?.suggested_rest_seconds || 90;
      isRestTimerRunning = true;

      if (sessionId) {
        await logSet(sessionId, cleanExId, set.setNumber, set.weightKg, set.reps, set.rpe);
      }
    } else {
      isRestTimerRunning = false;
    }
  }

  function cycleSetType(set: LiveWorkoutSet) {
    const types: SetType[] = ['warmup', 'normal', 'drop', 'failure'];
    const nextIdx = (types.indexOf(set.type) + 1) % types.length;
    set.type = types[nextIdx];
  }

  function adjustWeight(set: LiveWorkoutSet, delta: number) {
    set.weightKg = Math.max(0, Number((set.weightKg + delta).toFixed(2)));
  }

  function adjustReps(set: LiveWorkoutSet, delta: number) {
    set.reps = Math.max(1, set.reps + delta);
  }

  function addSet(ex: LiveWorkoutExercise) {
    const cleanExId = getCatalogId(ex);
    const history = historicalLogs.get(cleanExId) ?? [];
    const nextSetIdx = ex.sets.length;
    const lastSet = ex.sets[nextSetIdx - 1];
    const prevHistory = history[nextSetIdx] || history[history.length - 1];

    const defaultWeight = lastSet ? lastSet.weightKg : prevHistory ? prevHistory.weight : 20;
    const defaultReps = lastSet ? lastSet.reps : prevHistory ? prevHistory.reps : 10;

    const newSet: LiveWorkoutSet = {
      id: `s_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      setNumber: ex.sets.length + 1,
      type: 'normal',
      previous: prevHistory
        ? { weightKg: prevHistory.weight, reps: prevHistory.reps }
        : { weightKg: defaultWeight, reps: defaultReps },
      weightKg: defaultWeight,
      reps: defaultReps,
      rpe: 8.0,
      completed: false
    };
    ex.sets = [...ex.sets, newSet];
  }

  function removeSet(ex: LiveWorkoutExercise, setId: string) {
    if (ex.sets.length <= 1) {
      removeExercise(ex.id);
      return;
    }
    ex.sets = ex.sets.filter((s) => s.id !== setId).map((s, idx) => ({ ...s, setNumber: idx + 1 }));
  }

  function removeExercise(exId: string) {
    exercises = exercises.filter((e) => e.id !== exId);
  }

  function moveExercise(idx: number, direction: 'up' | 'down') {
    const targetIdx = direction === 'up' ? idx - 1 : idx + 1;
    if (targetIdx < 0 || targetIdx >= exercises.length) return;
    const reordered = [...exercises];
    const temp = reordered[idx];
    reordered[idx] = reordered[targetIdx];
    reordered[targetIdx] = temp;
    exercises = reordered;
  }

  // Add Exercise Modal State
  let isAddExerciseOpen = $state(false);
  let exerciseSearch = $state('');

  let filteredCatalogExercises = $derived(
    catalogExercises.filter(
      (e) => !exerciseSearch.trim() || e.name.toLowerCase().includes(exerciseSearch.toLowerCase())
    )
  );

  function handleSelectExercise(ex: (typeof catalogExercises)[0]) {
    const history = historicalLogs.get(ex.id) ?? [];
    const prevFirst = history[0];

    const uniqueInstanceId = `inst_${ex.id}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;

    const newLiveEx: LiveWorkoutExercise = {
      id: uniqueInstanceId,
      exerciseId: ex.id,
      name: ex.name,
      muscleGroup: (ex.primary_muscles as unknown as 'Brust') || 'Brust',
      category: 'Grundübung',
      equipment: (ex.equipment as unknown as 'Langhantel') || 'Langhantel',
      e1RM: 0,
      sets: [
        {
          id: `set_${Date.now()}_1`,
          setNumber: 1,
          type: 'normal',
          previous: prevFirst
            ? { weightKg: prevFirst.weight, reps: prevFirst.reps }
            : { weightKg: 20, reps: 10 },
          weightKg: prevFirst ? prevFirst.weight : 20,
          reps: prevFirst ? prevFirst.reps : 10,
          rpe: 8,
          completed: false
        }
      ]
    };
    exercises = [...exercises, newLiveEx];
    isAddExerciseOpen = false;
    exerciseSearch = '';
  }

  function handleFinishSession() {
    if (sessionId && typeof window !== 'undefined') {
      localStorage.removeItem(`salus_workout_draft_${sessionId}`);
    }
    onfinish?.({
      duration: formattedDuration,
      tonnageKg: totalTonnageKg,
      totalSets: completedSetsCount
    });
  }
</script>

<div class="space-y-5">
  <!-- Active Workout HUD Bar (Without blinking dot & without finish button) -->
  <div
    class="flex flex-col items-start justify-between gap-4 rounded-3xl border border-border-subtle bg-glass-dock p-5 shadow-lg backdrop-blur-2xl sm:flex-row sm:items-center"
  >
    <div>
      <h2 class="text-lg font-extrabold text-text-main">{planName}</h2>
    </div>

    <!-- Live Performance Counters & Add Action -->
    <div class="flex flex-wrap items-center gap-4 sm:gap-6">
      <!-- Live Duration -->
      <div>
        <span class="block text-[0.6875rem] font-bold text-text-muted uppercase">Dauer</span>
        <span class="text-base font-extrabold text-primary tabular-nums sm:text-lg">
          {formattedDuration}
        </span>
      </div>

      <!-- Live Volume Tonnage -->
      <div>
        <span class="block text-[0.6875rem] font-bold text-text-muted uppercase">Tonnage</span>
        <span class="text-base font-extrabold text-activity tabular-nums sm:text-lg">
          {totalTonnageKg.toLocaleString('de-DE')} kg
        </span>
      </div>

      <!-- Sets Progress -->
      <div>
        <span class="block text-[0.6875rem] font-bold text-text-muted uppercase">Sätze</span>
        <span class="text-base font-extrabold text-text-main tabular-nums sm:text-lg">
          {completedSetsCount} / {totalSetsCount}
        </span>
      </div>

      <!-- Add Exercise Button directly in HUD Bar (Only when exercises exist) -->
      {#if exercises.length > 0}
        <button
          type="button"
          onclick={() => (isAddExerciseOpen = true)}
          class="flex shrink-0 cursor-pointer items-center gap-1.5 rounded-2xl bg-primary px-3 py-1.5 text-xs font-bold text-white shadow-sm transition-all hover:opacity-90"
          title="Übung zum Training hinzufügen"
        >
          <Icon name="add" size="sm" />
          <span>Übung</span>
        </button>
      {/if}
    </div>
  </div>

  <!-- Rest Timer Floating Dock -->
  <WorkoutRestTimerBar
    running={isRestTimerRunning}
    initialSeconds={restTimerSeconds}
    onclose={() => (isRestTimerRunning = false)}
  />

  <!-- List of Exercises in Active Session -->
  {#if exercises.length === 0}
    <div
      class="space-y-3 rounded-3xl border border-border-subtle bg-surface-0 p-8 text-center shadow-xs"
    >
      <div
        class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary-soft text-primary"
      >
        <Icon name="fitness_center" size="lg" />
      </div>
      <h3 class="text-base font-bold text-text-main">Noch keine Übungen in dieser Einheit</h3>
      <p class="mx-auto max-w-sm text-xs text-text-muted">
        Füge deine erste Übung hinzu, um Sätze, Gewichte und Pausen live zu protokollieren.
      </p>
      <button
        type="button"
        onclick={() => (isAddExerciseOpen = true)}
        class="cursor-pointer rounded-2xl bg-primary px-4 py-2 text-xs font-bold text-white shadow-sm transition-all hover:opacity-90"
      >
        + Übung auswählen
      </button>
    </div>
  {:else}
    <div class="space-y-5">
      {#each exercises as ex, exIdx (ex.id)}
        <div
          class="group relative space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-4 shadow-xs transition-colors hover:border-border-strong sm:p-5"
        >
          <!-- Exercise Header with Scheibenrechner, Reorder & Remove Actions -->
          <div
            class="flex flex-wrap items-center justify-between gap-2 border-b border-border-subtle/60 pb-3"
          >
            <div class="flex items-center gap-3">
              <span
                class="flex h-8 w-8 items-center justify-center rounded-2xl bg-activity/10 text-xs font-extrabold text-activity tabular-nums"
              >
                #{exIdx + 1}
              </span>
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="text-base font-extrabold text-text-main">{ex.name}</h3>
                  <Badge variant="default" class="text-[0.625rem]">{ex.muscleGroup}</Badge>
                </div>
                <span class="text-xs text-text-muted">{ex.category} &bull; {ex.equipment}</span>
              </div>
            </div>

            <!-- Exercise 3-Dots Options Menu Trigger & Dropdown -->
            <div class="relative">
              <button
                type="button"
                onclick={() => (activeMenuExId = activeMenuExId === ex.id ? null : ex.id)}
                class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-2xl border border-border-subtle bg-surface-50 text-text-muted shadow-2xs transition-colors hover:bg-surface-100 hover:text-text-main"
                title="Übungsoptionen"
              >
                <Icon name="more-vert" size="sm" />
              </button>

              <!-- Floating Context Dropdown -->
              {#if activeMenuExId === ex.id}
                <!-- Backdrop click catcher -->
                <div
                  class="fixed inset-0 z-40 bg-transparent"
                  onclick={() => (activeMenuExId = null)}
                  role="presentation"
                ></div>

                <div
                  class="glass-panel absolute top-10 right-0 z-50 w-56 animate-[slideDown_0.15s_ease-out] space-y-0.5 rounded-2xl border border-border-subtle p-1.5 text-xs shadow-2xl"
                >
                  <!-- 1. Plate Calculator -->
                  <button
                    type="button"
                    onclick={() => {
                      openPlateCalcForExercise(ex);
                      activeMenuExId = null;
                    }}
                    class="flex w-full cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-left font-semibold text-text-main transition-colors hover:bg-surface-50"
                  >
                    <Icon name="calculate" size="sm" class="text-primary" />
                    <span>Scheibenrechner</span>
                  </button>

                  <!-- 2. Move Up -->
                  <button
                    type="button"
                    disabled={exIdx === 0}
                    onclick={() => {
                      moveExercise(exIdx, 'up');
                      activeMenuExId = null;
                    }}
                    class="flex w-full cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-left font-semibold text-text-main transition-colors hover:bg-surface-50 disabled:pointer-events-none disabled:opacity-30"
                  >
                    <Icon name="arrow-upward" size="sm" class="text-text-muted" />
                    <span>Nach oben verschieben</span>
                  </button>

                  <!-- 3. Move Down -->
                  <button
                    type="button"
                    disabled={exIdx === exercises.length - 1}
                    onclick={() => {
                      moveExercise(exIdx, 'down');
                      activeMenuExId = null;
                    }}
                    class="flex w-full cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-left font-semibold text-text-main transition-colors hover:bg-surface-50 disabled:pointer-events-none disabled:opacity-30"
                  >
                    <Icon name="arrow-downward" size="sm" class="text-text-muted" />
                    <span>Nach unten verschieben</span>
                  </button>

                  <div class="my-1 h-px bg-border-subtle"></div>

                  <!-- 4. Delete Exercise -->
                  <button
                    type="button"
                    onclick={() => {
                      removeExercise(ex.id);
                      activeMenuExId = null;
                    }}
                    class="flex w-full cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-left font-semibold text-rose-500 transition-colors hover:bg-rose-500/10"
                  >
                    <Icon name="delete" size="sm" />
                    <span>Übung entfernen</span>
                  </button>
                </div>
              {/if}
            </div>
          </div>

          <!-- Sets Table & Clean Input Rows -->
          <div class="space-y-2.5">
            <!-- Column Headers (Desktop Only) -->
            <div
              class="hidden grid-cols-12 gap-3 px-3 text-[0.6875rem] font-extrabold tracking-wider text-text-muted uppercase md:grid"
            >
              <div class="col-span-2">Satz / Typ</div>
              <div class="col-span-2">Vorherig</div>
              <div class="col-span-3">Gewicht (kg)</div>
              <div class="col-span-2">Wdh</div>
              <div class="col-span-1">RPE</div>
              <div class="col-span-2 pr-2 text-right">Status &amp; Aktion</div>
            </div>

            <!-- Set Rows (Mobile Touch Card + Desktop Table Row) -->
            {#each ex.sets as set (set.id)}
              {@const isOverload =
                set.previous.weightKg > 0 &&
                (set.weightKg > set.previous.weightKg ||
                  (set.weightKg === set.previous.weightKg && set.reps > set.previous.reps))}

              <!-- 📱 MOBILE TOUCH CARD (Screen < 768px: 44px Touch-Targets & Crystal-Clear Labels) -->
              <div
                class="block rounded-2xl border p-3.5 transition-all md:hidden {set.completed
                  ? 'border-emerald-500/30 bg-emerald-500/10'
                  : 'border-border-subtle bg-surface-50'} space-y-3"
              >
                <!-- Mobile Header: Satz #, Type, Ziel, Delete -->
                <div class="flex items-center justify-between gap-2">
                  <div class="flex items-center gap-2">
                    <span class="font-mono text-sm font-black text-text-main tabular-nums"
                      >Satz {set.setNumber}</span
                    >
                    <button
                      type="button"
                      onclick={() => cycleSetType(set)}
                      class="cursor-pointer rounded-lg px-2.5 py-1 font-mono text-xs font-bold uppercase transition-colors {set.type ===
                      'warmup'
                        ? 'bg-amber-400/20 text-amber-600'
                        : set.type === 'drop'
                          ? 'bg-purple-400/20 text-purple-600'
                          : set.type === 'failure'
                            ? 'bg-rose-400/20 text-rose-600'
                            : 'bg-surface-100 text-text-muted'}"
                    >
                      {set.type}
                    </button>
                    {#if isOverload}
                      <span
                        class="rounded bg-amber-400/20 px-2 py-0.5 text-[0.625rem] font-black text-amber-600"
                        title="Progressive Überlastung"
                      >
                        PR
                      </span>
                    {/if}
                  </div>

                  <div class="flex items-center gap-2">
                    {#if set.previous.weightKg > 0}
                      <span
                        class="rounded-lg bg-surface-100 px-2 py-0.5 font-mono text-xs text-text-muted"
                      >
                        Ziel: {set.previous.weightKg}kg × {set.previous.reps}
                      </span>
                    {/if}
                    <button
                      type="button"
                      onclick={() => removeSet(ex, set.id)}
                      class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-xl text-text-muted transition-colors hover:bg-rose-500/10 hover:text-rose-500"
                      title="Satz löschen"
                    >
                      <Icon name="delete" size="sm" />
                    </button>
                  </div>
                </div>

                <!-- Mobile Touch Steppers Grid (Clear Labels + 44px Height) -->
                <div class="grid grid-cols-12 items-end gap-2.5">
                  <!-- Weight Stepper (Col 1-5) -->
                  <div class="col-span-5 space-y-1">
                    <span
                      class="block text-[0.6875rem] font-extrabold tracking-wider text-text-muted uppercase"
                    >
                      Gewicht (kg)
                    </span>
                    <div
                      class="flex items-center overflow-hidden rounded-xl border border-border-subtle bg-surface-0 shadow-2xs focus-within:border-primary"
                    >
                      <button
                        type="button"
                        onclick={() => adjustWeight(set, -2.5)}
                        class="flex h-11 w-9 shrink-0 cursor-pointer items-center justify-center text-base font-black text-text-muted transition-transform select-none hover:bg-surface-100 hover:text-text-main active:scale-95"
                      >
                        -
                      </button>
                      <input
                        type="number"
                        step="0.5"
                        bind:value={set.weightKg}
                        class="h-11 w-full bg-transparent p-0 text-center font-mono text-sm font-extrabold text-text-main outline-none"
                      />
                      <button
                        type="button"
                        onclick={() => adjustWeight(set, 2.5)}
                        class="flex h-11 w-9 shrink-0 cursor-pointer items-center justify-center text-base font-black text-text-muted transition-transform select-none hover:bg-surface-100 hover:text-text-main active:scale-95"
                      >
                        +
                      </button>
                    </div>
                  </div>

                  <!-- Reps Stepper (Col 6-9) -->
                  <div class="col-span-4 space-y-1">
                    <span
                      class="block text-[0.6875rem] font-extrabold tracking-wider text-text-muted uppercase"
                    >
                      Wdh
                    </span>
                    <div
                      class="flex items-center overflow-hidden rounded-xl border border-border-subtle bg-surface-0 shadow-2xs focus-within:border-primary"
                    >
                      <button
                        type="button"
                        onclick={() => adjustReps(set, -1)}
                        class="flex h-11 w-8 shrink-0 cursor-pointer items-center justify-center text-base font-black text-text-muted transition-transform select-none hover:bg-surface-100 hover:text-text-main active:scale-95"
                      >
                        -
                      </button>
                      <input
                        type="number"
                        bind:value={set.reps}
                        class="h-11 w-full bg-transparent p-0 text-center font-mono text-sm font-extrabold text-text-main outline-none"
                      />
                      <button
                        type="button"
                        onclick={() => adjustReps(set, 1)}
                        class="flex h-11 w-8 shrink-0 cursor-pointer items-center justify-center text-base font-black text-text-muted transition-transform select-none hover:bg-surface-100 hover:text-text-main active:scale-95"
                      >
                        +
                      </button>
                    </div>
                  </div>

                  <!-- RPE (Col 10-12) -->
                  <div class="col-span-3 space-y-1">
                    <span
                      class="block text-[0.6875rem] font-extrabold tracking-wider text-text-muted uppercase"
                    >
                      RPE
                    </span>
                    <input
                      type="number"
                      step="0.5"
                      min="5"
                      max="10"
                      placeholder="8.0"
                      bind:value={set.rpe}
                      class="h-11 w-full rounded-xl border border-border-subtle bg-surface-0 text-center font-mono text-sm font-bold text-text-main shadow-2xs outline-none focus:border-primary"
                    />
                  </div>
                </div>

                <!-- Mobile Big Touch Completion Button -->
                <button
                  type="button"
                  onclick={() => toggleSetCompletion(ex, set)}
                  class="flex h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-xl text-xs font-extrabold shadow-sm transition-all {set.completed
                    ? 'bg-emerald-500 text-white shadow-emerald-500/20'
                    : 'border border-border-subtle bg-surface-100 text-text-main hover:bg-emerald-500/20 hover:text-emerald-600'}"
                >
                  <Icon name={set.completed ? 'check_circle' : 'check'} size="sm" />
                  <span>{set.completed ? 'Erledigt' : 'Abhaken'}</span>
                </button>
              </div>

              <!-- 💻 DESKTOP TABLE ROW (Screen >= 768px: Spacious 12-Col Table Layout) -->
              <div
                class="group/set hidden grid-cols-12 items-center gap-3 rounded-2xl border p-2.5 transition-all md:grid {set.completed
                  ? 'border-emerald-500/30 bg-emerald-500/10'
                  : 'border-border-subtle bg-surface-50'}"
              >
                <!-- Col 1-2: Set Number & Cycle Type -->
                <div class="col-span-2 flex items-center gap-2">
                  <span class="font-mono text-xs font-black text-text-main tabular-nums"
                    >#{set.setNumber}</span
                  >
                  <button
                    type="button"
                    onclick={() => cycleSetType(set)}
                    class="cursor-pointer rounded-lg px-2 py-0.5 font-mono text-[0.625rem] font-bold uppercase transition-colors {set.type ===
                    'warmup'
                      ? 'bg-amber-400/20 text-amber-600'
                      : set.type === 'drop'
                        ? 'bg-purple-400/20 text-purple-600'
                        : set.type === 'failure'
                          ? 'bg-rose-400/20 text-rose-600'
                          : 'bg-surface-100 text-text-muted'}"
                  >
                    {set.type}
                  </button>
                  {#if isOverload}
                    <span
                      class="rounded bg-amber-400/20 px-1.5 py-0.5 text-[0.5625rem] font-black text-amber-600"
                      title="Progressive Überlastung"
                    >
                      PR
                    </span>
                  {/if}
                </div>

                <!-- Col 3-4: Previous Target -->
                <div class="col-span-2 font-mono text-xs text-text-muted">
                  {set.previous.weightKg > 0
                    ? `${set.previous.weightKg}kg × ${set.previous.reps}`
                    : '—'}
                </div>

                <!-- Col 5-7: Weight Stepper -->
                <div
                  class="col-span-3 flex items-center overflow-hidden rounded-xl border border-border-subtle bg-surface-0 shadow-2xs focus-within:border-primary"
                >
                  <button
                    type="button"
                    onclick={() => adjustWeight(set, -2.5)}
                    class="flex h-9 w-8 shrink-0 cursor-pointer items-center justify-center text-sm font-black text-text-muted select-none hover:bg-surface-100 hover:text-text-main"
                    title="-2.5 kg"
                  >
                    -
                  </button>
                  <input
                    type="number"
                    step="0.5"
                    bind:value={set.weightKg}
                    class="h-9 w-full bg-transparent p-0 text-center font-mono text-xs font-bold text-text-main outline-none"
                  />
                  <button
                    type="button"
                    onclick={() => adjustWeight(set, 2.5)}
                    class="flex h-9 w-8 shrink-0 cursor-pointer items-center justify-center text-sm font-black text-text-muted select-none hover:bg-surface-100 hover:text-text-main"
                    title="+2.5 kg"
                  >
                    +
                  </button>
                </div>

                <!-- Col 8-9: Reps Stepper -->
                <div
                  class="col-span-2 flex items-center overflow-hidden rounded-xl border border-border-subtle bg-surface-0 shadow-2xs focus-within:border-primary"
                >
                  <button
                    type="button"
                    onclick={() => adjustReps(set, -1)}
                    class="flex h-9 w-8 shrink-0 cursor-pointer items-center justify-center text-sm font-black text-text-muted select-none hover:bg-surface-100 hover:text-text-main"
                    title="-1 Wdh"
                  >
                    -
                  </button>
                  <input
                    type="number"
                    bind:value={set.reps}
                    class="h-9 w-full bg-transparent p-0 text-center font-mono text-xs font-bold text-text-main outline-none"
                  />
                  <button
                    type="button"
                    onclick={() => adjustReps(set, 1)}
                    class="flex h-9 w-8 shrink-0 cursor-pointer items-center justify-center text-sm font-black text-text-muted select-none hover:bg-surface-100 hover:text-text-main"
                    title="+1 Wdh"
                  >
                    +
                  </button>
                </div>

                <!-- Col 10: RPE -->
                <div class="col-span-1">
                  <input
                    type="number"
                    step="0.5"
                    min="5"
                    max="10"
                    placeholder="RPE"
                    bind:value={set.rpe}
                    class="h-9 w-full rounded-xl border border-border-subtle bg-surface-0 text-center font-mono text-xs text-text-main shadow-2xs outline-none focus:border-primary"
                  />
                </div>

                <!-- Col 11-12: Status Checkmark & Smooth Hover Delete -->
                <div class="col-span-2 flex items-center justify-end gap-2 pr-1">
                  <button
                    type="button"
                    onclick={() => toggleSetCompletion(ex, set)}
                    class="flex h-9 w-9 cursor-pointer items-center justify-center rounded-xl border-2 transition-all {set.completed
                      ? 'border-emerald-500 bg-emerald-500 text-white shadow-xs'
                      : 'border-border-strong hover:border-emerald-500'}"
                    title={set.completed ? 'Satz als erledigt markiert' : 'Satz abhaken'}
                  >
                    {#if set.completed}
                      <Icon name="check" size={16} />
                    {/if}
                  </button>

                  <button
                    type="button"
                    onclick={() => removeSet(ex, set.id)}
                    class="flex h-9 w-9 cursor-pointer items-center justify-center rounded-xl text-text-muted opacity-0 transition-opacity duration-150 group-hover/set:opacity-100 focus-within:opacity-100 hover:bg-rose-500/10 hover:text-rose-500"
                    title="Satz löschen"
                  >
                    <Icon name="delete" size="sm" />
                  </button>
                </div>
              </div>
            {/each}
          </div>

          <!-- Add Set Action Bar -->
          <div class="flex flex-wrap items-center justify-between gap-2 pt-1">
            <button
              type="button"
              onclick={() => addSet(ex)}
              class="flex cursor-pointer items-center gap-1.5 rounded-xl border border-border-subtle bg-surface-50 px-3 py-1.5 text-xs font-bold text-text-main transition-colors hover:bg-surface-100"
            >
              <Icon name="add" size="sm" />
              <span>Satz</span>
            </button>
          </div>
        </div>
      {/each}
    </div>

    <!-- Bottom Finish Workout Section -->
    <div
      class="mt-8 flex flex-col items-center justify-between gap-4 rounded-3xl border border-border-subtle bg-surface-0 p-6 shadow-xs sm:flex-row"
    >
      <div>
        <h3 class="text-base font-extrabold text-text-main">Workout bereit zum Abschluss?</h3>
        <p class="mt-0.5 text-xs text-text-muted">
          {completedSetsCount} von {totalSetsCount} Sätzen absolviert &bull; {totalTonnageKg.toLocaleString(
            'de-DE'
          )} kg Gesamttonnage
        </p>
      </div>

      <button
        type="button"
        onclick={handleFinishSession}
        class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-6 py-3 text-sm font-extrabold text-white shadow-md transition-all hover:bg-emerald-600 sm:w-auto"
      >
        <Icon name="check_circle" size="md" />
        <span>Training abschließen</span>
      </button>
    </div>
  {/if}

  <!-- Add Exercise Selector Modal -->
  {#if isAddExerciseOpen}
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
    >
      <div
        class="w-full max-w-lg animate-[zoomIn_0.15s_ease-out] space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-6 shadow-2xl"
      >
        <div class="flex items-center justify-between border-b border-border-subtle pb-2">
          <div class="flex items-center gap-2.5">
            <div
              class="flex h-8 w-8 items-center justify-center rounded-xl bg-primary-soft text-primary"
            >
              <Icon name="fitness_center" size="sm" />
            </div>
            <h3 class="text-base font-extrabold text-text-main">Übung auswählen</h3>
          </div>
          <button
            type="button"
            onclick={() => (isAddExerciseOpen = false)}
            class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full bg-surface-50 text-text-muted hover:text-text-main"
          >
            &times;
          </button>
        </div>

        <div class="relative">
          <input
            type="text"
            placeholder="Übung durchsuchen..."
            bind:value={exerciseSearch}
            class="w-full rounded-2xl border border-border-subtle bg-surface-50 py-2.5 pr-3.5 pl-9 text-xs font-semibold text-text-main outline-none focus:border-primary"
          />
          <span class="absolute top-3 left-3 text-text-muted">
            <Icon name="search" size="sm" />
          </span>
        </div>

        <div class="no-scrollbar max-h-64 space-y-1.5 overflow-y-auto">
          {#each filteredCatalogExercises as ex}
            {@const isAlreadyInSession = exercises.some((e) => getCatalogId(e) === ex.id)}
            <button
              type="button"
              onclick={() => handleSelectExercise(ex)}
              class="flex w-full cursor-pointer items-center justify-between rounded-2xl border border-border-subtle bg-surface-50 p-3 text-left transition-all hover:border-primary hover:bg-primary-soft/20"
            >
              <div>
                <div class="flex items-center gap-2">
                  <span class="text-xs font-bold text-text-main">{ex.name}</span>
                  {#if isAlreadyInSession}
                    <Badge variant="default" class="text-[0.5625rem]">Im Workout</Badge>
                  {/if}
                </div>
                <span class="text-[0.6875rem] text-text-muted"
                  >{ex.primary_muscles || 'Ganzkörper'} &bull; {ex.equipment || 'Frei'}</span
                >
              </div>
              <span class="text-xs font-bold text-primary">+ Wählen</span>
            </button>
          {/each}
        </div>
      </div>
    </div>
  {/if}

  <!-- Plate Calculator Modal -->
  <PlateCalculatorModal
    open={isPlateCalcOpen}
    initialWeight={activeSetForPlateCalc?.weightKg || 100}
    onapplyweight={handleApplyPlateWeight}
    onclose={() => (isPlateCalcOpen = false)}
  />
</div>
