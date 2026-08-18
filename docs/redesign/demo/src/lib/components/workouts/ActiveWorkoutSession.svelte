<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import PlateCalculatorModal from './PlateCalculatorModal.svelte';
  import WorkoutRestTimerBar from './WorkoutRestTimerBar.svelte';
  import type { LiveWorkoutExercise, LiveWorkoutSet, SetType } from '../../types/workouts';

  let {
    planName = 'Push Day A (Hypertrophie und Kraft)',
    onfinish
  } = $props<{
    planName?: string;
    onfinish?: (stats: { duration: string; tonnageKg: number; totalSets: number }) => void;
  }>();

  // Multi-Exercise Active Session State
  let exercises = $state<LiveWorkoutExercise[]>([
    {
      id: 'ex_1',
      name: 'Bankdrücken (Langhantel)',
      muscleGroup: 'Brust',
      category: 'Grundübung',
      equipment: 'Langhantel',
      e1RM: 143.0,
      sets: [
        { id: 's1_1', setNumber: 1, type: 'warmup', previous: { weightKg: 60, reps: 10 }, weightKg: 60, reps: 10, rpe: 6, completed: true },
        { id: 's1_2', setNumber: 2, type: 'warmup', previous: { weightKg: 80, reps: 6 }, weightKg: 80, reps: 6, rpe: 7, completed: true },
        { id: 's1_3', setNumber: 3, type: 'normal', previous: { weightKg: 120, reps: 5 }, weightKg: 122.5, reps: 5, rpe: 8.5, completed: true, isPR: true },
        { id: 's1_4', setNumber: 4, type: 'normal', previous: { weightKg: 120, reps: 5 }, weightKg: 122.5, reps: 4, rpe: 9.0, completed: false }
      ]
    },
    {
      id: 'ex_2',
      name: 'Schrägbankdrücken (Kurzhantel)',
      muscleGroup: 'Brust',
      category: 'Hypertrophie',
      equipment: 'Kurzhantel',
      e1RM: 42.5,
      sets: [
        { id: 's2_1', setNumber: 1, type: 'normal', previous: { weightKg: 36, reps: 10 }, weightKg: 36, reps: 10, rpe: 8, completed: true },
        { id: 's2_2', setNumber: 2, type: 'normal', previous: { weightKg: 36, reps: 8 }, weightKg: 36, reps: 8, rpe: 8.5, completed: false },
        { id: 's2_3', setNumber: 3, type: 'drop', previous: { weightKg: 36, reps: 8 }, weightKg: 36, reps: 8, rpe: 9.5, completed: false }
      ]
    },
    {
      id: 'ex_3',
      name: 'Dips mit Zusatzgewicht',
      muscleGroup: 'Trizeps',
      category: 'Grundübung',
      equipment: 'Eigengewicht',
      e1RM: 125.0,
      supersetGroup: 'A1',
      sets: [
        { id: 's3_1', setNumber: 1, type: 'normal', previous: { weightKg: 20, reps: 10 }, weightKg: 22.5, reps: 10, rpe: 8, completed: false },
        { id: 's3_2', setNumber: 2, type: 'normal', previous: { weightKg: 20, reps: 8 }, weightKg: 22.5, reps: 8, rpe: 8.5, completed: false },
        { id: 's3_3', setNumber: 3, type: 'failure', previous: { weightKg: 20, reps: 8 }, weightKg: 22.5, reps: 8, rpe: 10, completed: false }
      ]
    },
    {
      id: 'ex_4',
      name: 'Seitheben am Kabelzug',
      muscleGroup: 'Schultern',
      category: 'Isolationsübung',
      equipment: 'Kabelzug',
      e1RM: 18.0,
      supersetGroup: 'A2',
      sets: [
        { id: 's4_1', setNumber: 1, type: 'normal', previous: { weightKg: 12.5, reps: 15 }, weightKg: 12.5, reps: 15, rpe: 8, completed: false },
        { id: 's4_2', setNumber: 2, type: 'normal', previous: { weightKg: 12.5, reps: 12 }, weightKg: 12.5, reps: 12, rpe: 8.5, completed: false },
        { id: 's4_3', setNumber: 3, type: 'drop', previous: { weightKg: 12.5, reps: 12 }, weightKg: 12.5, reps: 12, rpe: 9.5, completed: false }
      ]
    }
  ]);

  // Live Elapsed Workout Timer (Ticking in seconds)
  let elapsedSeconds = $state(2535); // ~42:15 min
  $effect(() => {
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

  function openPlateCalc(set: LiveWorkoutSet) {
    activeSetForPlateCalc = set;
    isPlateCalcOpen = true;
  }

  function handleApplyPlateWeight(weight: number) {
    if (activeSetForPlateCalc) {
      activeSetForPlateCalc.weightKg = weight;
    }
  }

  // Rest Timer State
  let isRestTimerRunning = $state(false);
  let restTimerSeconds = $state(90);

  function toggleSetCompletion(set: LiveWorkoutSet) {
    set.completed = !set.completed;
    if (set.completed) {
      // Trigger Rest Timer
      restTimerSeconds = 90;
      isRestTimerRunning = true;
    }
  }

  function cycleSetType(set: LiveWorkoutSet) {
    const types: SetType[] = ['warmup', 'normal', 'drop', 'failure'];
    const nextIdx = (types.indexOf(set.type) + 1) % types.length;
    set.type = types[nextIdx];
  }

  function addSet(ex: LiveWorkoutExercise) {
    const lastSet = ex.sets[ex.sets.length - 1];
    const newSet: LiveWorkoutSet = {
      id: `s_${Date.now()}_${Math.random()}`,
      setNumber: ex.sets.length + 1,
      type: 'normal',
      previous: lastSet ? { weightKg: lastSet.weightKg, reps: lastSet.reps } : { weightKg: 20, reps: 10 },
      weightKg: lastSet ? lastSet.weightKg : 20,
      reps: lastSet ? lastSet.reps : 10,
      rpe: 8.0,
      completed: false
    };
    ex.sets = [...ex.sets, newSet];
  }

  function removeSet(ex: LiveWorkoutExercise, setId: string) {
    ex.sets = ex.sets.filter(s => s.id !== setId).map((s, idx) => ({ ...s, setNumber: idx + 1 }));
  }

  function removeExercise(exId: string) {
    exercises = exercises.filter(e => e.id !== exId);
  }

  let isSummaryOpen = $state(false);
</script>

<div class="space-y-5">
  
  <!-- Active Workout HUD Bar -->
  <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-5 shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
    
    <div>
      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
        <h2 class="text-lg font-extrabold text-[var(--text-main)]">{planName}</h2>
        <Badge variant="activity">Live Session</Badge>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">
        Progressive Belastungssteuerung mit automatischer Erfassung
      </p>
    </div>

    <!-- Live Performance Counters -->
    <div class="flex items-center gap-6">
      
      <!-- Live Duration -->
      <div>
        <span class="text-[0.6875rem] text-[var(--text-muted)] font-bold uppercase block">Dauer</span>
        <span class="text-xl font-extrabold text-[var(--color-primary)] tabular-nums">
          {formattedDuration}
        </span>
      </div>

      <!-- Live Volume Tonnage -->
      <div>
        <span class="text-[0.6875rem] text-[var(--text-muted)] font-bold uppercase block">Tonnage</span>
        <span class="text-xl font-extrabold text-[var(--color-activity)] tabular-nums">
          {totalTonnageKg.toLocaleString('de-DE')} kg
        </span>
      </div>

      <!-- Sets Progress -->
      <div>
        <span class="text-[0.6875rem] text-[var(--text-muted)] font-bold uppercase block">Sätze</span>
        <span class="text-xl font-extrabold text-[var(--text-main)] tabular-nums">
          {completedSetsCount} / {totalSetsCount}
        </span>
      </div>

      <!-- Finish Button -->
      <button
        type="button"
        onclick={() => isSummaryOpen = true}
        class="px-4 py-2.5 rounded-2xl bg-emerald-500 text-white text-xs font-bold hover:bg-emerald-600 transition-all cursor-pointer shadow-md flex items-center gap-1.5"
      >
        <span>Training abschließen</span>
      </button>

    </div>
  </div>

  <!-- List of Exercises in Active Session -->
  <div class="space-y-4">
    {#each exercises as ex, exIdx (ex.id)}
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-3.5 relative">
        
        <!-- Exercise Header -->
        <div class="flex items-center justify-between flex-wrap gap-2 pb-2.5 border-b border-[var(--border-subtle)]/60">
          <div class="flex items-center gap-2.5">
            <span class="w-7 h-7 rounded-xl bg-[var(--color-activity)]/10 text-[var(--color-activity)] font-extrabold text-xs flex items-center justify-center tabular-nums">
              {exIdx + 1}
            </span>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-sm sm:text-base font-extrabold text-[var(--text-main)]">{ex.name}</h3>
                {#if ex.supersetGroup}
                  <Badge variant="vital" class="text-[0.5625rem]">Supersatz {ex.supersetGroup}</Badge>
                {/if}
              </div>
              <div class="flex items-center gap-2 text-xs text-[var(--text-muted)] mt-0.5">
                <Badge variant="default" class="text-[0.5625rem]">{ex.muscleGroup}</Badge>
                <span>&bull;</span>
                <span class="text-[0.6875rem]">{ex.equipment}</span>
                <span>&bull;</span>
                <span class="text-[0.6875rem] font-bold text-[var(--color-primary)]">1RM: {ex.e1RM} kg</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              type="button"
              onclick={() => removeExercise(ex.id)}
              class="text-xs text-[var(--text-muted)] hover:text-rose-500 cursor-pointer p-1"
              title="Übung entfernen"
            >
              &times;
            </button>
          </div>
        </div>

        <!-- SETS TABLE -->
        <div class="w-full overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.625rem]">
                <th class="py-2 px-2 w-14 text-center">Satz</th>
                <th class="py-2 px-2">Typ</th>
                <th class="py-2 px-2">Vorwoche</th>
                <th class="py-2 px-2">Gewicht (kg)</th>
                <th class="py-2 px-2">Wdh.</th>
                <th class="py-2 px-2">RIR / RPE</th>
                <th class="py-2 px-2 text-right">Status</th>
                <th class="py-2 px-1 w-6"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]/50">
              {#each ex.sets as set}
                <tr class="hover:bg-[var(--bg-surface-50)]/60 transition-colors {set.completed ? 'bg-emerald-500/5' : ''}">
                  
                  <!-- Set Number -->
                  <td class="py-2.5 px-2 text-center font-bold text-[var(--text-main)] tabular-nums">
                    {set.setNumber}
                  </td>

                  <!-- Set Type Button (W, N, D, F) -->
                  <td class="py-2.5 px-2">
                    <button
                      type="button"
                      onclick={() => cycleSetType(set)}
                      class="px-2 py-0.5 rounded-lg text-[0.625rem] font-extrabold uppercase cursor-pointer transition-transform active:scale-95 {set.type === 'warmup' ? 'bg-amber-400/10 text-amber-500 border border-amber-400/30' : set.type === 'drop' ? 'bg-purple-500/10 text-purple-500 border border-purple-500/30' : set.type === 'failure' ? 'bg-rose-500/10 text-rose-500 border border-rose-500/30' : 'bg-blue-500/10 text-blue-500 border border-blue-500/30'}"
                      title="Klicken zum Umschalten: Warmup, Normal, Drop-Set, Failure"
                    >
                      {set.type === 'warmup' ? 'Warmup' : set.type === 'drop' ? 'Drop' : set.type === 'failure' ? 'Failure' : 'Normal'}
                    </button>
                  </td>

                  <!-- Vorwoche Ghost -->
                  <td class="py-2.5 px-2 text-[var(--text-soft)] text-xs tabular-nums">
                    {set.previous.weightKg} kg &times; {set.previous.reps}
                  </td>

                  <!-- Weight Input + Plate Calculator Trigger -->
                  <td class="py-2.5 px-2">
                    <div class="flex items-center gap-1.5">
                      <input
                        type="number"
                        step="0.5"
                        bind:value={set.weightKg}
                        class="w-18 px-2 py-1 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] font-bold text-xs tabular-nums outline-none focus:border-[var(--color-primary)]"
                      />
                      <button
                        type="button"
                        onclick={() => openPlateCalc(set)}
                        class="w-6 h-6 rounded-lg bg-[var(--bg-surface-50)] hover:bg-[var(--color-activity)] hover:text-white text-[var(--text-muted)] flex items-center justify-center text-xs cursor-pointer transition-colors"
                        title="Hantelscheiben-Rechner öffnen"
                      >
                        
                      </button>
                    </div>
                  </td>

                  <!-- Reps Input -->
                  <td class="py-2.5 px-2">
                    <input
                      type="number"
                      bind:value={set.reps}
                      class="w-14 px-2 py-1 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] font-bold text-xs tabular-nums outline-none focus:border-[var(--color-primary)]"
                    />
                  </td>

                  <!-- RIR / RPE Selector -->
                  <td class="py-2.5 px-2">
                    <select
                      bind:value={set.rpe}
                      class="px-2 py-1 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--text-main)] outline-none cursor-pointer"
                    >
                      <option value={6}>RIR 4 (@6.0)</option>
                      <option value={7}>RIR 3 (@7.0)</option>
                      <option value={8}>RIR 2 (@8.0)</option>
                      <option value={8.5}>RIR 1.5 (@8.5)</option>
                      <option value={9}>RIR 1 (@9.0)</option>
                      <option value={9.5}>RIR 0.5 (@9.5)</option>
                      <option value={10}>RIR 0 / Failure (@10)</option>
                    </select>
                  </td>

                  <!-- Checkmark Completion Button -->
                  <td class="py-2.5 px-2 text-right">
                    <button
                      type="button"
                      onclick={() => toggleSetCompletion(set)}
                      class="px-3.5 py-1 rounded-xl font-bold text-xs transition-all cursor-pointer shadow-2xs flex items-center gap-1 ml-auto {set.completed ? 'bg-emerald-500 text-white hover:bg-emerald-600' : 'bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
                    >
                      <span>{set.completed ? 'Fertig' : 'Abhaken'}</span>
                    </button>
                  </td>

                  <!-- Delete Set -->
                  <td class="py-2.5 px-1 text-center">
                    <button
                      type="button"
                      onclick={() => removeSet(ex, set.id)}
                      class="text-[var(--text-soft)] hover:text-rose-500 cursor-pointer text-xs"
                      title="Satz löschen"
                    >
                      &times;
                    </button>
                  </td>

                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        <!-- Add Set Button -->
        <div class="pt-1 flex items-center justify-between">
          <button
            type="button"
            onclick={() => addSet(ex)}
            class="px-3 py-1.5 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--text-main)] hover:bg-[var(--bg-surface-100)] cursor-pointer transition-all flex items-center gap-1.5"
          >
            <span>+ Satz hinzufügen</span>
          </button>
        </div>

      </div>
    {/each}
  </div>

</div>

<!-- Floating Rest Timer Overlay -->
<WorkoutRestTimerBar
  initialSeconds={restTimerSeconds}
  running={isRestTimerRunning}
  oncomplete={() => isRestTimerRunning = false}
  onclose={() => isRestTimerRunning = false}
/>

<!-- Plate Calculator Modal -->
<PlateCalculatorModal
  open={isPlateCalcOpen}
  initialWeight={activeSetForPlateCalc?.weightKg || 100}
  onapplyweight={handleApplyPlateWeight}
  onclose={() => isPlateCalcOpen = false}
/>

<!-- Session Complete Summary Celebration Modal -->
{#if isSummaryOpen}
  <div class="fixed inset-0 bg-black/80 backdrop-blur-md z-70 flex items-center justify-center p-4">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl text-center space-y-5 animate-[scaleIn_0.2s_ease-out]">
      <div class="w-16 h-16 rounded-3xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center text-3xl mx-auto">
        
      </div>
      <div>
        <h2 class="text-xl font-extrabold text-[var(--text-main)]">Training erfolgreich beendet!</h2>
        <p class="text-xs text-[var(--text-muted)] mt-1">Hervorragende Leistung. Alle Daten wurden in deiner Historie und Muskel-Heatmap synchronisiert.</p>
      </div>

      <div class="grid grid-cols-3 gap-2 p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl">
        <div>
          <span class="text-[0.625rem] text-[var(--text-muted)] block">Dauer</span>
          <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums">{formattedDuration}</span>
        </div>
        <div>
          <span class="text-[0.625rem] text-[var(--text-muted)] block">Tonnage</span>
          <span class="text-sm font-extrabold text-[var(--color-activity)] tabular-nums">{totalTonnageKg.toLocaleString('de-DE')} kg</span>
        </div>
        <div>
          <span class="text-[0.625rem] text-[var(--text-muted)] block">Sätze</span>
          <span class="text-sm font-extrabold text-emerald-500 tabular-nums">{completedSetsCount} Sätze</span>
        </div>
      </div>

      <div class="pt-2">
        <button
          type="button"
          onclick={() => {
            isSummaryOpen = false;
            onfinish?.({ duration: formattedDuration, tonnageKg: totalTonnageKg, totalSets: completedSetsCount });
          }}
          class="w-full py-3 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md"
        >
          Fertig & Zurück zur Übersicht
        </button>
      </div>
    </div>
  </div>
{/if}
