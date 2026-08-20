<script lang="ts">
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Modal from '../ui/Modal.svelte';
  import type { Exercise } from '$lib/db/types';

  export interface WorkoutItem {
    exercise_id: string;
    target_sets: number;
    target_reps: number;
    target_rpe: number;
  }

  export interface WorkoutDraft {
    name: string;
    description: string | null;
    exercises: WorkoutItem[];
  }

  let {
    open = false,
    exercises = [],
    onsave,
    onclose
  } = $props<{
    open: boolean;
    exercises: Exercise[];
    onsave: (draft: WorkoutDraft) => void;
    onclose: () => void;
  }>();

  let name = $state('');
  let description = $state('');
  let items = $state<WorkoutItem[]>([]);
  let selectedExerciseId = $state('');

  const exerciseOptions = $derived(
    exercises.map((e: Exercise) => ({
      value: e.id,
      label: `${e.name} (${e.primary_muscles?.split(',')[0] ?? ''})`
    }))
  );

  function exerciseName(id: string): string {
    return exercises.find((e: Exercise) => e.id === id)?.name ?? 'Übung';
  }

  function exerciseMuscle(id: string): string {
    return exercises.find((e: Exercise) => e.id === id)?.primary_muscles?.split(',')[0] ?? '';
  }

  $effect(() => {
    if (open) {
      name = '';
      description = '';
      items = [];
      selectedExerciseId = exercises[0]?.id ?? '';
    }
  });

  function addExercise() {
    if (!selectedExerciseId) return;
    items = [
      ...items,
      { exercise_id: selectedExerciseId, target_sets: 3, target_reps: 8, target_rpe: 8 }
    ];
  }

  function removeExercise(idx: number) {
    items = items.filter((_, i) => i !== idx);
  }

  function updateItem(idx: number, patch: Partial<WorkoutItem>) {
    items = items.map((item, i) => (i === idx ? { ...item, ...patch } : item));
  }

  function moveUp(idx: number) {
    if (idx <= 0) return;
    const arr = [...items];
    const item = arr[idx];
    arr.splice(idx, 1);
    arr.splice(idx - 1, 0, item);
    items = arr;
  }

  function moveDown(idx: number) {
    if (idx >= items.length - 1) return;
    const arr = [...items];
    const item = arr[idx];
    arr.splice(idx, 1);
    arr.splice(idx + 1, 0, item);
    items = arr;
  }

  function handleSave() {
    onsave({
      name: name.trim(),
      description: description.trim() || null,
      exercises: items
    });
    onclose();
  }

  let canSave = $derived(name.trim().length > 0 && items.length > 0);
</script>

<Modal
  {open}
  title="Neues Workout erstellen"
  subtitle="Wähle Übungen aus dem Katalog und lege Sätze, Wiederholungen und RPE fest"
  icon="fitness-center"
  size="lg"
  {onclose}
>
  <div class="space-y-5">
    <div class="grid grid-cols-1 gap-3">
      <Input label="Name" bind:value={name} placeholder="z. B. Push Day" />
      <Input label="Beschreibung" bind:value={description} placeholder="Optional" />
    </div>

    <div class="max-h-[36vh] space-y-2.5 overflow-y-auto pr-1">
      <span class="block text-xs font-extrabold text-text-main">
        Übungen ({items.length}):
      </span>

      {#if items.length === 0}
        <p class="rounded-xl border border-dashed border-border-subtle p-3 text-xs text-text-muted">
          Noch keine Übungen — füge unten welche aus dem Katalog hinzu.
        </p>
      {/if}

      {#each items as item, idx (idx)}
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
              <span class="block text-xs font-bold text-text-main">
                {exerciseName(item.exercise_id)}
              </span>
              <Badge variant="default" class="text-[0.5625rem]">
                {exerciseMuscle(item.exercise_id)}
              </Badge>
            </div>
          </div>

          <div class="flex items-center gap-2 text-xs">
            <div class="w-20">
              <Input
                type="number"
                min={1}
                max={10}
                unit="Sätze"
                value={item.target_sets}
                oninput={(e) =>
                  updateItem(idx, {
                    target_sets: Number((e.currentTarget as HTMLInputElement).value) || 3
                  })}
              />
            </div>
            <div class="w-20">
              <Input
                type="number"
                min={1}
                max={50}
                unit="Wdh."
                value={item.target_reps}
                oninput={(e) =>
                  updateItem(idx, {
                    target_reps: Number((e.currentTarget as HTMLInputElement).value) || 8
                  })}
              />
            </div>
            <div class="w-16">
              <Input
                type="number"
                min={6}
                max={10}
                step={0.5}
                unit="RPE"
                value={item.target_rpe}
                oninput={(e) =>
                  updateItem(idx, {
                    target_rpe: Number((e.currentTarget as HTMLInputElement).value) || 8
                  })}
              />
            </div>

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

    <div class="flex items-end gap-2 pt-2">
      <div class="flex-1">
        <Select
          label="Übung hinzufügen"
          options={exerciseOptions}
          bind:value={selectedExerciseId}
        />
      </div>
      <Btn variant="secondary" size="md" onclick={addExercise} class="h-10 shrink-0">
        + Hinzufügen
      </Btn>
    </div>

    <div class="flex items-center justify-end gap-2 border-t border-border-subtle pt-3">
      <Btn variant="secondary" size="md" onclick={onclose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" onclick={handleSave} disabled={!canSave}
        >Workout speichern</Btn
      >
    </div>
  </div>
</Modal>
