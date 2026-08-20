<script lang="ts">
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import SegmentedControl from '../ui/SegmentedControl.svelte';
  import Modal from '../ui/Modal.svelte';
  import Icon from '../ui/Icon.svelte';

  export interface ProgramSlotDraft {
    workout_id: string;
    timing: 'rotation' | 'weekly' | 'dated';
    day_of_week: number | null;
    scheduled_date: string | null;
  }

  export interface ProgramDraft {
    name: string;
    description: string | null;
    progression_scheme: string;
    slots: ProgramSlotDraft[];
  }

  let {
    open = false,
    workouts = [],
    onsave,
    onclose
  } = $props<{
    open: boolean;
    workouts: { id: string; name: string }[];
    onsave: (draft: ProgramDraft) => void;
    onclose: () => void;
  }>();

  let name = $state('');
  let description = $state('');
  let progressionScheme = $state('linear');
  let slots = $state<ProgramSlotDraft[]>([]);

  const schemeOptions = [
    { value: 'linear', label: 'Linear (Overload)' },
    { value: 'autoregulated', label: 'Autoreguliert' },
    { value: 'none', label: 'Standard' }
  ];

  const timingOptions = [
    { value: 'rotation', label: 'Rotation' },
    { value: 'weekly', label: 'Wochentag' },
    { value: 'dated', label: 'Datum' }
  ];

  const weekdayOptions = [
    { value: 0, label: 'Montag' },
    { value: 1, label: 'Dienstag' },
    { value: 2, label: 'Mittwoch' },
    { value: 3, label: 'Donnerstag' },
    { value: 4, label: 'Freitag' },
    { value: 5, label: 'Samstag' },
    { value: 6, label: 'Sonntag' }
  ];

  const workoutOptions = $derived(
    workouts.map((w: { id: string; name: string }) => ({ value: w.id, label: w.name }))
  );

  $effect(() => {
    if (open) {
      name = '';
      description = '';
      progressionScheme = 'linear';
      slots = [];
    }
  });

  function addSlot() {
    slots = [
      ...slots,
      {
        workout_id: workouts[0]?.id ?? '',
        timing: 'rotation',
        day_of_week: null,
        scheduled_date: null
      }
    ];
  }

  function removeSlot(index: number) {
    slots = slots.filter((_, i) => i !== index);
  }

  function updateSlot(index: number, patch: Partial<ProgramSlotDraft>) {
    slots = slots.map((slot, i) => (i === index ? { ...slot, ...patch } : slot));
  }

  function handleSave() {
    onsave({
      name: name.trim(),
      description: description.trim() || null,
      progression_scheme: progressionScheme,
      slots: slots
        .filter((s) => s.workout_id)
        .map((s) => ({
          workout_id: s.workout_id,
          timing: s.timing,
          day_of_week: s.timing === 'weekly' ? s.day_of_week : null,
          scheduled_date: s.timing === 'dated' ? s.scheduled_date : null
        }))
        .map((s, index) => ({ ...s, sequence: index }))
    });
    onclose();
  }

  let canSave = $derived(name.trim().length > 0 && slots.some((s) => s.workout_id));
</script>

<Modal
  {open}
  title="Neues Programm erstellen"
  subtitle="Kombiniere Workouts zu einem Programm und lege die Progression fest"
  icon="calendar-view-week"
  size="lg"
  {onclose}
>
  <div class="space-y-5">
    <div class="grid grid-cols-1 gap-3">
      <Input label="Programm-Name" bind:value={name} placeholder="z. B. Push / Pull / Legs" />
      <Input
        label="Beschreibung"
        bind:value={description}
        placeholder="Optional — Ziel, Dauer, Fokus"
      />
    </div>

    <div>
      <span class="mb-1.5 block text-xs font-bold text-text-main">Progression</span>
      <SegmentedControl options={schemeOptions} bind:value={progressionScheme} />
    </div>

    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold text-text-main">Workouts</span>
        <button
          type="button"
          onclick={addSlot}
          class="flex cursor-pointer items-center gap-1 rounded-lg px-2 py-1 text-xs font-bold text-primary transition-colors hover:bg-primary-soft"
        >
          <Icon name="add" size="sm" />
          <span>Tag hinzufügen</span>
        </button>
      </div>

      {#if slots.length === 0}
        <p class="rounded-xl border border-dashed border-border-subtle p-3 text-xs text-text-muted">
          Noch keine Workouts — füge mindestens ein Workout hinzu.
        </p>
      {/if}

      {#each slots as slot, index (index)}
        <div
          class="grid grid-cols-1 gap-2 rounded-2xl border border-border-subtle bg-surface-50 p-3 sm:grid-cols-[1fr_auto_auto]"
        >
          <Select
            label={`Tag ${index + 1}`}
            options={workoutOptions}
            bind:value={slot.workout_id}
            onchange={(val) => updateSlot(index, { workout_id: String(val) })}
          />
          <Select
            label="Zeit"
            options={timingOptions}
            bind:value={slot.timing}
            onchange={(val) => updateSlot(index, { timing: val as ProgramSlotDraft['timing'] })}
          />
          {#if slot.timing === 'weekly'}
            <Select
              label="Wochentag"
              options={weekdayOptions}
              value={slot.day_of_week ?? 0}
              onchange={(val) => updateSlot(index, { day_of_week: Number(val) })}
            />
          {:else if slot.timing === 'dated'}
            <Input
              label="Datum"
              type="date"
              value={slot.scheduled_date ?? ''}
              oninput={(e) =>
                updateSlot(index, {
                  scheduled_date: (e.currentTarget as HTMLInputElement).value || null
                })}
            />
          {:else}
            <div class="flex items-end">
              <button
                type="button"
                onclick={() => removeSlot(index)}
                class="hover:text-danger flex cursor-pointer items-center gap-1 rounded-lg px-2 py-1.5 text-xs font-bold text-text-muted transition-colors"
              >
                <Icon name="delete" size="sm" />
                <span>Entfernen</span>
              </button>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </div>

  {#snippet actions()}
    <Btn variant="ghost" onclick={onclose}>Abbrechen</Btn>
    <Btn variant="primary" onclick={handleSave} disabled={!canSave}>Programm speichern</Btn>
  {/snippet}
</Modal>
