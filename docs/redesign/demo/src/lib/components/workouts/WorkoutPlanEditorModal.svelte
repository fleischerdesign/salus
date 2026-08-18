<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import type { WorkoutPlan, MuscleGroup } from '../../types/workouts';

  let {
    open = false,
    plan = null,
    onsave,
    onclose
  } = $props<{
    open: boolean;
    plan: WorkoutPlan | null;
    onsave: (plan: WorkoutPlan) => void;
    onclose: () => void;
  }>();

  let name = $state('Neuer Trainingsplan');
  let split = $state('Push / Pull / Legs');
  let subtitle = $state('Hypertrophie und Kraftaufbau');
  let exercises = $state<WorkoutPlan['exercises']>([
    { name: 'Bankdrücken (Langhantel)', muscle: 'Brust', targetSets: 4, targetReps: '6–8 Wdh', targetRir: 2 },
    { name: 'Schrägbankdrücken (Kurzhantel)', muscle: 'Brust', targetSets: 3, targetReps: '8–10 Wdh', targetRir: 1 },
    { name: 'Dips mit Zusatzgewicht', muscle: 'Trizeps', targetSets: 3, targetReps: '8–10 Wdh', targetRir: 1 }
  ]);

  $effect(() => {
    if (open && plan) {
      name = plan.name;
      split = plan.split;
      subtitle = plan.subtitle;
      exercises = [...plan.exercises];
    } else if (open && !plan) {
      name = 'Neuer Trainingsplan';
      split = 'Push / Pull / Legs';
      subtitle = 'Hypertrophie und Kraftaufbau';
      exercises = [
        { name: 'Bankdrücken (Langhantel)', muscle: 'Brust', targetSets: 4, targetReps: '6–8 Wdh', targetRir: 2 },
        { name: 'Schrägbankdrücken (Kurzhantel)', muscle: 'Brust', targetSets: 3, targetReps: '8–10 Wdh', targetRir: 1 }
      ];
    }
  });

  const availableExercises: { name: string; muscle: MuscleGroup }[] = [
    { name: 'Bankdrücken (Langhantel)', muscle: 'Brust' },
    { name: 'Schrägbankdrücken (Kurzhantel)', muscle: 'Brust' },
    { name: 'Dips mit Zusatzgewicht', muscle: 'Trizeps' },
    { name: 'Seitheben am Kabelzug', muscle: 'Schultern' },
    { name: 'Trizepsdrücken am Kabelzug', muscle: 'Trizeps' },
    { name: 'Kniebeugen (High Bar)', muscle: 'Quadrizeps' },
    { name: 'Rumänisches Kreuzheben', muscle: 'Hamstrings' },
    { name: 'Beinpresse 45°', muscle: 'Quadrizeps' },
    { name: 'Klimmzüge mit Zusatzgewicht', muscle: 'Rücken' },
    { name: 'Langhantelrudern', muscle: 'Rücken' },
    { name: 'Latzug enger Griff', muscle: 'Rücken' },
    { name: 'Incline Dumbbell Curls', muscle: 'Bizeps' },
    { name: 'Face Pulls', muscle: 'Schultern' }
  ];

  let selectedExerciseToAdd = $state('Seitheben am Kabelzug');

  function addExercise() {
    const item = availableExercises.find(e => e.name === selectedExerciseToAdd);
    if (item) {
      exercises = [...exercises, {
        name: item.name,
        muscle: item.muscle,
        targetSets: 3,
        targetReps: '10–12 Wdh',
        targetRir: 2
      }];
    }
  }

  function removeExercise(idx: number) {
    exercises = exercises.filter((_, i) => i !== idx);
  }

  function moveUp(idx: number) {
    if (idx <= 0) return;
    const item = exercises[idx];
    const arr = [...exercises];
    arr.splice(idx, 1);
    arr.splice(idx - 1, 0, item);
    exercises = arr;
  }

  function moveDown(idx: number) {
    if (idx >= exercises.length - 1) return;
    const item = exercises[idx];
    const arr = [...exercises];
    arr.splice(idx, 1);
    arr.splice(idx + 1, 0, item);
    exercises = arr;
  }

  let totalSets = $derived(exercises.reduce((acc, e) => acc + e.targetSets, 0));
  let estimatedDuration = $derived(`${totalSets * 3.5} Min`);
  let estimatedVolume = $derived(`${(totalSets * 320).toLocaleString('de-DE')} kg`);

  function handleSave() {
    const saved: WorkoutPlan = {
      id: plan?.id || `plan_${Date.now()}`,
      name,
      split,
      subtitle,
      estimatedDuration,
      targetVolume: estimatedVolume,
      targetVolumeKg: totalSets * 320,
      exercisesCount: exercises.length,
      exercises
    };
    onsave(saved);
    onclose();
  }
</script>

{#if open}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-60 flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl space-y-5 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold text-lg shrink-0">
            
          </div>
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">
              {plan ? 'Trainingsplan bearbeiten' : 'Neuen Trainingsplan erstellen'}
            </h2>
            <p class="text-xs text-[var(--text-muted)]">Strukturiere deinen Split, Übungsreihenfolge und Belastungsparameter</p>
          </div>
        </div>

        <button
          type="button"
          onclick={onclose}
          class="w-8 h-8 rounded-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center text-lg cursor-pointer transition-colors"
          title="Schließen"
          aria-label="Schließen"
        >
          &times;
        </button>
      </div>

      <!-- Plan Metadata Form -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div class="space-y-1">
          <label for="plan-name-input" class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Plan-Titel</label>
          <input
            id="plan-name-input"
            type="text"
            bind:value={name}
            class="w-full px-3.5 py-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
          />
        </div>

        <div class="space-y-1">
          <label for="plan-split-select" class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Split-Kategorie</label>
          <select
            id="plan-split-select"
            bind:value={split}
            class="w-full px-3.5 py-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--text-main)] outline-none focus:border-[var(--color-primary)] cursor-pointer"
          >
            <option value="Push / Pull / Legs">Push / Pull / Legs</option>
            <option value="Oberkörper / Unterkörper">Oberkörper / Unterkörper (2er Split)</option>
            <option value="Ganzkörper 3er">Ganzkörper 3er</option>
            <option value="Arnold Split (Chest/Back, Shoulders/Arms, Legs)">Arnold Split</option>
          </select>
        </div>
      </div>

      <!-- Calculated Metrics Overview -->
      <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl flex items-center justify-around text-xs">
        <div class="text-center">
          <span class="text-[0.6875rem] text-[var(--text-muted)] block">Übungen</span>
          <span class="font-extrabold text-[var(--text-main)]">{exercises.length}</span>
        </div>
        <div class="w-px h-6 bg-[var(--border-subtle)]"></div>
        <div class="text-center">
          <span class="text-[0.6875rem] text-[var(--text-muted)] block">Gesamtsätze</span>
          <span class="font-extrabold text-[var(--text-main)]">{totalSets} Sätze</span>
        </div>
        <div class="w-px h-6 bg-[var(--border-subtle)]"></div>
        <div class="text-center">
          <span class="text-[0.6875rem] text-[var(--text-muted)] block">Geschätzte Dauer</span>
          <span class="font-extrabold text-[var(--color-activity)]">{estimatedDuration}</span>
        </div>
      </div>

      <!-- Exercises List in Plan -->
      <div class="space-y-2.5 max-h-[36vh] overflow-y-auto pr-1">
        <span class="text-xs font-extrabold text-[var(--text-main)] block">Übungs-Reihenfolge & Belastungs-Parameter:</span>

        {#each exercises as ex, idx}
          <div class="p-3 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] flex items-center justify-between gap-3">
            
            <div class="flex items-center gap-2.5">
              <span class="w-6 h-6 rounded-lg bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] font-bold text-xs flex items-center justify-center text-[var(--text-muted)] tabular-nums">
                {idx + 1}
              </span>
              <div>
                <span class="text-xs font-bold text-[var(--text-main)] block">{ex.name}</span>
                <Badge variant="default" class="text-[0.5625rem]">{ex.muscle}</Badge>
              </div>
            </div>

            <!-- Parameters Inputs -->
            <div class="flex items-center gap-2 text-xs">
              <div class="flex items-center gap-1">
                <input
                  type="number"
                  min="1"
                  max="10"
                  bind:value={ex.targetSets}
                  class="w-11 px-1.5 py-1 rounded bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] font-bold text-center text-xs"
                />
                <span class="text-[0.6875rem] text-[var(--text-muted)] font-semibold">Sätze</span>
              </div>

              <input
                type="text"
                bind:value={ex.targetReps}
                class="w-20 px-1.5 py-1 rounded bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-center text-xs font-semibold"
              />

              <!-- Move Up / Down / Remove -->
              <div class="flex items-center gap-1 border-l border-[var(--border-subtle)] pl-2">
                <button
                  type="button"
                  onclick={() => moveUp(idx)}
                  class="w-6 h-6 rounded bg-[var(--bg-surface-50)] text-[0.625rem] font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] cursor-pointer"
                >
                  ▲
                </button>
                <button
                  type="button"
                  onclick={() => moveDown(idx)}
                  class="w-6 h-6 rounded bg-[var(--bg-surface-50)] text-[0.625rem] font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] cursor-pointer"
                >
                  ▼
                </button>
                <button
                  type="button"
                  onclick={() => removeExercise(idx)}
                  class="w-6 h-6 rounded bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white text-xs font-bold transition-all cursor-pointer"
                >
                  &times;
                </button>
              </div>
            </div>

          </div>
        {/each}
      </div>

      <!-- Add Exercise Dropdown / Button -->
      <div class="pt-2 flex items-center gap-2">
        <select
          bind:value={selectedExerciseToAdd}
          class="flex-1 px-3.5 py-2 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--text-main)] outline-none focus:border-[var(--color-primary)] cursor-pointer"
        >
          {#each availableExercises as ae}
            <option value={ae.name}>{ae.name} ({ae.muscle})</option>
          {/each}
        </select>
        <Btn variant="secondary" size="sm" onclick={addExercise}>
          + Übung hinzufügen
        </Btn>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between pt-3 border-t border-[var(--border-subtle)]">
        <Btn variant="secondary" size="sm" onclick={onclose}>
          Abbrechen
        </Btn>
        <button
          type="button"
          onclick={handleSave}
          class="px-5 py-2 rounded-xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md"
        >
          Plan speichern
        </button>
      </div>

    </div>
  </div>
{/if}
