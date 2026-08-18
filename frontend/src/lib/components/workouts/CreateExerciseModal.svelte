<script lang="ts">
  import Modal from '../ui/Modal.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Textarea from '../ui/Textarea.svelte';
  import { createExercise } from '$lib/mutations/exercise';
  import type { MuscleGroup, EquipmentType } from '../../types/workouts';

  let {
    open = false,
    oncreated,
    onclose
  } = $props<{
    open: boolean;
    oncreated?: () => void;
    onclose: () => void;
  }>();

  let name = $state('');
  let primaryMuscle = $state<MuscleGroup>('Brust');
  let secondaryMuscles = $state('');
  let equipment = $state<EquipmentType>('Langhantel');
  let description = $state('');
  let instructions = $state('');
  let restSeconds = $state(90);
  let isSaving = $state(false);
  let errorMsg = $state('');

  const muscleOptions: { value: MuscleGroup; label: string }[] = [
    { value: 'Brust', label: 'Brust' },
    { value: 'Rücken', label: 'Rücken' },
    { value: 'Quadrizeps', label: 'Quadrizeps' },
    { value: 'Hamstrings', label: 'Hamstrings' },
    { value: 'Schultern', label: 'Schultern' },
    { value: 'Bizeps', label: 'Bizeps' },
    { value: 'Trizeps', label: 'Trizeps' },
    { value: 'Waden', label: 'Waden' },
    { value: 'Bauch', label: 'Bauch' },
    { value: 'Gesäß', label: 'Gesäß' }
  ];

  const equipmentOptions: { value: EquipmentType; label: string }[] = [
    { value: 'Langhantel', label: 'Langhantel' },
    { value: 'Kurzhantel', label: 'Kurzhantel' },
    { value: 'Kabelzug', label: 'Kabelzug' },
    { value: 'Maschine', label: 'Maschine' },
    { value: 'Eigengewicht', label: 'Eigengewicht' }
  ];

  function resetForm() {
    name = '';
    primaryMuscle = 'Brust';
    secondaryMuscles = '';
    equipment = 'Langhantel';
    description = '';
    instructions = '';
    restSeconds = 90;
    errorMsg = '';
    isSaving = false;
  }

  async function handleSave() {
    if (!name.trim()) {
      errorMsg = 'Bitte gib einen Namen für die Übung ein.';
      return;
    }

    try {
      isSaving = true;
      errorMsg = '';

      await createExercise({
        name: name.trim(),
        equipment: equipment.toLowerCase(),
        primary_muscles: primaryMuscle,
        secondary_muscles: secondaryMuscles.trim() || null,
        description: description.trim() || null,
        instructions: instructions.trim() || null,
        suggested_rest_seconds: restSeconds || 90
      });

      resetForm();
      oncreated?.();
      onclose();
    } catch (e) {
      const err = e as Error;
      errorMsg = err?.message || 'Fehler beim Erstellen der Übung.';
    } finally {
      isSaving = false;
    }
  }
</script>

<Modal
  {open}
  title="Neue Übung anlegen"
  subtitle="Erweitere deinen persönlichen Übungskatalog"
  icon="fitness-center"
  {onclose}
>
  <!-- Error Message -->
  {#if errorMsg}
    <div
      class="mb-3 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs font-bold text-rose-500"
    >
      {errorMsg}
    </div>
  {/if}

  <!-- Form Inputs -->
  <form
    onsubmit={(e) => {
      e.preventDefault();
      handleSave();
    }}
    class="space-y-3.5"
  >
    <!-- Name -->
    <Input
      label="Name der Übung"
      required
      placeholder="z. B. Bulgarian Split Squats, Incline Cable Curls..."
      bind:value={name}
    />

    <!-- Muscle & Equipment Grid -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Select
        label="Primäre Muskelgruppe"
        required
        bind:value={primaryMuscle}
        options={muscleOptions}
      />

      <Select
        label="Equipment / Ausrüstung"
        required
        bind:value={equipment}
        options={equipmentOptions}
      />
    </div>

    <!-- Secondary Muscles & Rest Time -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Input
        label="Sekundäre Muskeln (Optional)"
        placeholder="z. B. Gesäß, Bauch..."
        bind:value={secondaryMuscles}
      />

      <Input
        label="Empfohlene Satzpause (Sekunden)"
        type="number"
        step={15}
        min={30}
        max={300}
        bind:value={restSeconds}
      />
    </div>

    <!-- Description / Instructions -->
    <Textarea
      label="Ausführungshinweise / Form-Tipps (Optional)"
      rows={2}
      placeholder="z. B. Standbein leicht nach vorne versetzen, Rumpf aufrecht halten..."
      bind:value={instructions}
    />

    <!-- Modal Actions -->
    <div class="flex items-center justify-end gap-2 border-t border-[var(--border-subtle)] pt-3">
      <Btn variant="secondary" size="md" onclick={onclose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" type="submit" loading={isSaving}>Übung speichern</Btn>
    </div>
  </form>
</Modal>
