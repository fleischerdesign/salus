<script lang="ts">
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Modal from '../ui/Modal.svelte';
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
    {
      name: 'Bankdrücken (Langhantel)',
      muscle: 'Brust',
      targetSets: 4,
      targetReps: '6–8 Wdh',
      targetRir: 2
    },
    {
      name: 'Schrägbankdrücken (Kurzhantel)',
      muscle: 'Brust',
      targetSets: 3,
      targetReps: '8–10 Wdh',
      targetRir: 1
    },
    {
      name: 'Dips mit Zusatzgewicht',
      muscle: 'Trizeps',
      targetSets: 3,
      targetReps: '8–10 Wdh',
      targetRir: 1
    }
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
        {
          name: 'Bankdrücken (Langhantel)',
          muscle: 'Brust',
          targetSets: 4,
          targetReps: '6–8 Wdh',
          targetRir: 2
        },
        {
          name: 'Schrägbankdrücken (Kurzhantel)',
          muscle: 'Brust',
          targetSets: 3,
          targetReps: '8–10 Wdh',
          targetRir: 1
        }
      ];
    }
  });

  const splitOptions = [
    { value: 'Push / Pull / Legs', label: 'Push / Pull / Legs' },
    { value: 'Oberkörper / Unterkörper', label: 'Oberkörper / Unterkörper (2er Split)' },
    { value: 'Ganzkörper 3er', label: 'Ganzkörper 3er' },
    { value: 'Arnold Split (Chest/Back, Shoulders/Arms, Legs)', label: 'Arnold Split' }
  ];

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

  let exerciseOptions = $derived(
    availableExercises.map((ae) => ({
      value: ae.name,
      label: `${ae.name} (${ae.muscle})`
    }))
  );

  function addExercise() {
    const item = availableExercises.find((e) => e.name === selectedExerciseToAdd);
    if (item) {
      exercises = [
        ...exercises,
        {
          name: item.name,
          muscle: item.muscle,
          targetSets: 3,
          targetReps: '10–12 Wdh',
          targetRir: 2
        }
      ];
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

<Modal
  {open}
  title={plan ? 'Trainingsplan bearbeiten' : 'Neuen Trainingsplan erstellen'}
  subtitle="Strukturiere deinen Split, Übungsreihenfolge und Belastungsparameter"
  icon="fitness-center"
  size="lg"
  {onclose}
>
  <div class="space-y-5">
    <!-- Plan Metadata Form -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Input label="Plan-Titel" bind:value={name} placeholder="z. B. Push / Pull / Legs" />

      <Select label="Split-Kategorie" bind:value={split} options={splitOptions} />
    </div>

    <!-- Calculated Metrics Overview -->
    <div
      class="flex items-center justify-around rounded-2xl border border-border-subtle bg-surface-50 p-3 text-xs"
    >
      <div class="text-center">
        <span class="block text-[0.6875rem] text-text-muted">Übungen</span>
        <span class="font-extrabold text-text-main">{exercises.length}</span>
      </div>
      <div class="h-6 w-px bg-border-subtle"></div>
      <div class="text-center">
        <span class="block text-[0.6875rem] text-text-muted">Gesamtsätze</span>
        <span class="font-extrabold text-text-main">{totalSets} Sätze</span>
      </div>
      <div class="h-6 w-px bg-border-subtle"></div>
      <div class="text-center">
        <span class="block text-[0.6875rem] text-text-muted">Geschätzte Dauer</span>
        <span class="font-extrabold text-activity">{estimatedDuration}</span>
      </div>
    </div>

    <!-- Exercises List in Plan -->
    <div class="max-h-[36vh] space-y-2.5 overflow-y-auto pr-1">
      <span class="block text-xs font-extrabold text-text-main"
        >Übungs-Reihenfolge & Belastungs-Parameter:</span
      >

      {#each exercises as ex, idx}
        <div
          class="flex items-center justify-between gap-3 rounded-2xl border border-border-subtle bg-surface-0 p-3"
        >
          <div class="flex items-center gap-2.5">
            <span
              class="flex h-6 w-6 items-center justify-center rounded-lg border border-border-subtle bg-surface-50 text-xs font-bold text-text-muted tabular-nums"
            >
              {idx + 1}
            </span>
            <div>
              <span class="block text-xs font-bold text-text-main">{ex.name}</span>
              <Badge variant="default" class="text-[0.5625rem]">{ex.muscle}</Badge>
            </div>
          </div>

          <!-- Parameters Inputs -->
          <div class="flex items-center gap-2 text-xs">
            <div class="w-20">
              <Input type="number" min={1} max={10} unit="Sätze" bind:value={ex.targetSets} />
            </div>

            <div class="w-24">
              <Input placeholder="8-12 Wdh." bind:value={ex.targetReps} />
            </div>

            <!-- Move Up / Down / Remove -->
            <div class="flex items-center gap-1 border-l border-border-subtle pl-2">
              <button
                type="button"
                onclick={() => moveUp(idx)}
                class="h-6 w-6 cursor-pointer rounded-lg bg-surface-50 text-[0.625rem] font-bold text-text-muted hover:text-text-main"
                title="Nach oben verschieben"
              >
                ▲
              </button>
              <button
                type="button"
                onclick={() => moveDown(idx)}
                class="h-6 w-6 cursor-pointer rounded-lg bg-surface-50 text-[0.625rem] font-bold text-text-muted hover:text-text-main"
                title="Nach unten verschieben"
              >
                ▼
              </button>
              <button
                type="button"
                onclick={() => removeExercise(idx)}
                class="h-6 w-6 cursor-pointer rounded-lg bg-rose-500/10 text-xs font-bold text-rose-500 transition-all hover:bg-rose-500 hover:text-white"
                title="Übung entfernen"
              >
                &times;
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Add Exercise Dropdown / Button -->
    <div class="flex items-end gap-2 pt-2">
      <div class="flex-1">
        <Select
          label="Übung zur Liste hinzufügen"
          bind:value={selectedExerciseToAdd}
          options={exerciseOptions}
        />
      </div>
      <Btn variant="secondary" size="md" onclick={addExercise} class="h-10 shrink-0">
        + Hinzufügen
      </Btn>
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-end gap-2 border-t border-border-subtle pt-3">
      <Btn variant="secondary" size="md" onclick={onclose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" onclick={handleSave}>Plan speichern</Btn>
    </div>
  </div>
</Modal>
