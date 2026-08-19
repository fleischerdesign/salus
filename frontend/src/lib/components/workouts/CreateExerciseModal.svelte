<script lang="ts">
  import Modal from '../ui/Modal.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Textarea from '../ui/Textarea.svelte';
  import Chip from '../ui/Chip.svelte';
  import Icon from '../ui/Icon.svelte';
  import AnatomicalBodyVector from '../track/AnatomicalBodyVector.svelte';
  import { ANATOMICAL_PATH_TO_DETAILED_KEY, ANATOMICAL_MUSCLE_MAPPING } from '../track/anatomy-data';
  import { createExercise } from '$lib/mutations/exercise';
  import {
    DETAILED_MUSCLES,
    DETAILED_MUSCLE_MAP,
    MUSCLE_GROUPS,
    type MuscleGroup,
    type DetailedMuscleKey,
    type EquipmentType
  } from '../../types/workouts';

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
  let selectedPrimaryMuscles = $state<string[]>(['chest_clavicular']);
  let selectedSecondaryMuscles = $state<string[]>([]);
  let equipment = $state<EquipmentType>('Langhantel');
  let description = $state('');
  let instructions = $state('');
  let restSeconds = $state(90);
  let isSaving = $state(false);
  let errorMsg = $state('');

  let mannequinView = $state<'anterior' | 'posterior'>('anterior');
  let selectionTarget = $state<'primary' | 'secondary'>('primary');
  let activeGroupTab = $state<MuscleGroup>('Brust');

  const equipmentOptions: { value: EquipmentType; label: string }[] = [
    { value: 'Langhantel', label: 'Langhantel' },
    { value: 'Kurzhantel', label: 'Kurzhantel' },
    { value: 'Kabelzug', label: 'Kabelzug' },
    { value: 'Maschine', label: 'Maschine' },
    { value: 'Eigengewicht', label: 'Eigengewicht' }
  ];

  // Group detailed muscles by their parent MuscleGroup
  const musclesByGroup = $derived.by(() => {
    const map = new Map<MuscleGroup, typeof DETAILED_MUSCLES>();
    for (const g of MUSCLE_GROUPS) {
      map.set(
        g,
        DETAILED_MUSCLES.filter((m) => m.group === g)
      );
    }
    return map;
  });

  // Calculate path color map for live 2D body preview
  const pathColorMap = $derived.by(() => {
    const map: Record<string, string> = {};

    // Primary muscles -> Vivid Primary Color
    for (const key of selectedPrimaryMuscles) {
      const def = DETAILED_MUSCLE_MAP[key as DetailedMuscleKey];
      if (def) {
        for (const pid of def.svgPathIds) {
          map[pid] = 'var(--color-primary)';
        }
      }
    }

    // Secondary muscles -> Subtle Indigo/Secondary Color
    for (const key of selectedSecondaryMuscles) {
      const def = DETAILED_MUSCLE_MAP[key as DetailedMuscleKey];
      if (def) {
        for (const pid of def.svgPathIds) {
          if (!map[pid]) {
            map[pid] = '#818cf8';
          }
        }
      }
    }

    return map;
  });

  function togglePrimaryMuscle(key: string) {
    if (selectedPrimaryMuscles.includes(key)) {
      selectedPrimaryMuscles = selectedPrimaryMuscles.filter((k) => k !== key);
    } else {
      selectedPrimaryMuscles = [...selectedPrimaryMuscles, key];
      // Remove from secondary if present
      selectedSecondaryMuscles = selectedSecondaryMuscles.filter((k) => k !== key);
    }
  }

  function toggleSecondaryMuscle(key: string) {
    if (selectedSecondaryMuscles.includes(key)) {
      selectedSecondaryMuscles = selectedSecondaryMuscles.filter((k) => k !== key);
    } else {
      selectedSecondaryMuscles = [...selectedSecondaryMuscles, key];
      // Remove from primary if present
      selectedPrimaryMuscles = selectedPrimaryMuscles.filter((k) => k !== key);
    }
  }

  function handleBodyVectorClick(group: MuscleGroup, detailedId: string) {
    const detailedKey = ANATOMICAL_PATH_TO_DETAILED_KEY[detailedId];
    const keyToToggle = detailedKey || group;

    if (selectionTarget === 'primary') {
      togglePrimaryMuscle(keyToToggle);
    } else {
      toggleSecondaryMuscle(keyToToggle);
    }
  }

  function resetForm() {
    name = '';
    selectedPrimaryMuscles = ['chest_clavicular'];
    selectedSecondaryMuscles = [];
    equipment = 'Langhantel';
    description = '';
    instructions = '';
    restSeconds = 90;
    errorMsg = '';
    isSaving = false;
    mannequinView = 'anterior';
    selectionTarget = 'primary';
    activeGroupTab = 'Brust';
  }

  async function handleSave() {
    if (!name.trim()) {
      errorMsg = 'Bitte gib einen Namen für die Übung ein.';
      return;
    }
    if (selectedPrimaryMuscles.length === 0) {
      errorMsg = 'Bitte wähle mindestens einen primären Zielmuskel aus.';
      return;
    }

    try {
      isSaving = true;
      errorMsg = '';

      // Format canonical strings for storage
      const primaryStr = selectedPrimaryMuscles.join(', ');
      const secondaryStr = selectedSecondaryMuscles.length > 0 ? selectedSecondaryMuscles.join(', ') : null;

      await createExercise({
        name: name.trim(),
        equipment: equipment.toLowerCase(),
        primary_muscles: primaryStr,
        secondary_muscles: secondaryStr,
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
  subtitle="Erweitere deinen persönlichen Übungskatalog mit anatomischer Präzision"
  icon="fitness-center"
  size="lg"
  {onclose}
>
  {#if errorMsg}
    <div
      class="mb-3 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs font-bold text-rose-500"
    >
      {errorMsg}
    </div>
  {/if}

  <form
    onsubmit={(e) => {
      e.preventDefault();
      handleSave();
    }}
    class="space-y-4"
  >
    <!-- Basic Info -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div class="sm:col-span-2">
        <Input
          label="Name der Übung"
          required
          placeholder="z. B. Bulgarian Split Squats, Incline Cable Curls..."
          bind:value={name}
        />
      </div>
      <div>
        <Select
          label="Equipment / Ausrüstung"
          required
          bind:value={equipment}
          options={equipmentOptions}
        />
      </div>
    </div>

    <!-- Anatomical Muscle Selector & 2D Mannequin Preview -->
    <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5">
      <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-[var(--color-heading)]">
            Anatomische Zielmuskeln
          </h4>
          <p class="text-[11px] text-[var(--color-text-muted)]">
            Wähle Primärmuskeln (100% Satzvolumen) und Synergisten (50% Satzvolumen).
          </p>
        </div>

        <!-- Mode Toggle: Primär vs Sekundär -->
        <div class="flex items-center gap-1 rounded-xl bg-[var(--bg-surface-200)] p-1">
          <button
            type="button"
            onclick={() => (selectionTarget = 'primary')}
            class={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-bold transition-all ${
              selectionTarget === 'primary'
                ? 'bg-[var(--color-primary)] text-white shadow-sm'
                : 'text-[var(--color-text-muted)] hover:text-[var(--color-heading)]'
            }`}
          >
            <span class="h-2 w-2 rounded-full bg-white"></span>
            Primär ({selectedPrimaryMuscles.length})
          </button>
          <button
            type="button"
            onclick={() => (selectionTarget = 'secondary')}
            class={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-bold transition-all ${
              selectionTarget === 'secondary'
                ? 'bg-[#818cf8] text-white shadow-sm'
                : 'text-[var(--color-text-muted)] hover:text-[var(--color-heading)]'
            }`}
          >
            <span class="h-2 w-2 rounded-full bg-white"></span>
            Sekundär ({selectedSecondaryMuscles.length})
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <!-- Muscle Category Tabs & Chips (8 cols) -->
        <div class="space-y-3 lg:col-span-8">
          <!-- Muscle Group Horizontal Scroll Tabs -->
          <div class="flex gap-1.5 overflow-x-auto pb-1 scrollbar-none">
            {#each MUSCLE_GROUPS as group}
              {@const hasPrimary = selectedPrimaryMuscles.some(
                (k) => DETAILED_MUSCLE_MAP[k as DetailedMuscleKey]?.group === group
              )}
              {@const hasSecondary = selectedSecondaryMuscles.some(
                (k) => DETAILED_MUSCLE_MAP[k as DetailedMuscleKey]?.group === group
              )}
              <button
                type="button"
                onclick={() => (activeGroupTab = group)}
                class={`flex items-center gap-1 whitespace-nowrap rounded-xl px-2.5 py-1.5 text-xs font-bold transition-all ${
                  activeGroupTab === group
                    ? 'bg-[var(--color-heading)] text-[var(--bg-surface-0)]'
                    : 'bg-[var(--bg-surface-100)] text-[var(--color-text-muted)] hover:bg-[var(--bg-surface-200)]'
                }`}
              >
                <span>{group}</span>
                {#if hasPrimary}
                  <span class="h-1.5 w-1.5 rounded-full bg-[var(--color-primary)]"></span>
                {:else if hasSecondary}
                  <span class="h-1.5 w-1.5 rounded-full bg-[#818cf8]"></span>
                {/if}
              </button>
            {/each}
          </div>

          <!-- Active Group Muscle Chips -->
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {#each musclesByGroup.get(activeGroupTab) ?? [] as muscle (muscle.key)}
              {@const isPrimary = selectedPrimaryMuscles.includes(muscle.key)}
              {@const isSecondary = selectedSecondaryMuscles.includes(muscle.key)}
              <button
                type="button"
                onclick={() => {
                  if (selectionTarget === 'primary') {
                    togglePrimaryMuscle(muscle.key);
                  } else {
                    toggleSecondaryMuscle(muscle.key);
                  }
                }}
                class={`flex flex-col items-start rounded-xl border p-2.5 text-left transition-all ${
                  isPrimary
                    ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)] ring-1 ring-[var(--color-primary)]'
                    : isSecondary
                      ? 'border-[#818cf8] bg-[#818cf8]/10 ring-1 ring-[#818cf8]'
                      : 'border-[var(--border-subtle)] bg-[var(--bg-surface-0)] hover:border-[var(--color-heading)]'
                }`}
              >
                <div class="flex w-full items-center justify-between gap-1">
                  <span
                    class={`text-xs font-bold ${isPrimary ? 'text-[var(--color-primary)]' : isSecondary ? 'text-[#818cf8]' : 'text-[var(--color-heading)]'}`}
                  >
                    {muscle.name}
                  </span>
                  {#if isPrimary}
                    <span
                      class="rounded-md bg-[var(--color-primary)] px-1.5 py-0.5 text-[9px] font-black text-white"
                    >
                      1.0
                    </span>
                  {:else if isSecondary}
                    <span class="rounded-md bg-[#818cf8] px-1.5 py-0.5 text-[9px] font-black text-white">
                      0.5
                    </span>
                  {/if}
                </div>
                <span class="text-[10px] italic text-[var(--color-text-muted)] line-clamp-1">
                  {muscle.latin}
                </span>
              </button>
            {/each}
          </div>
        </div>

        <!-- 2D Mannequin Interactive Preview (4 cols) -->
        <div
          class="flex flex-col items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2 lg:col-span-4"
        >
          <div class="flex w-full items-center justify-between px-1">
            <span class="text-[10px] font-bold tracking-wider text-[var(--color-text-muted)] uppercase">
              2D Body Preview
            </span>
            <div class="flex gap-1">
              <button
                type="button"
                onclick={() => (mannequinView = 'anterior')}
                class={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                  mannequinView === 'anterior'
                    ? 'bg-[var(--color-heading)] text-white'
                    : 'text-[var(--color-text-muted)] hover:bg-[var(--bg-surface-200)]'
                }`}
              >
                Front
              </button>
              <button
                type="button"
                onclick={() => (mannequinView = 'posterior')}
                class={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                  mannequinView === 'posterior'
                    ? 'bg-[var(--color-heading)] text-white'
                    : 'text-[var(--color-text-muted)] hover:bg-[var(--bg-surface-200)]'
                }`}
              >
                Rück
              </button>
            </div>
          </div>

          <div class="my-1 flex h-[180px] w-full items-center justify-center">
            <AnatomicalBodyVector
              view={mannequinView}
              {pathColorMap}
              onselect={handleBodyVectorClick}
            />
          </div>

          <span class="text-[10px] text-[var(--color-text-muted)] text-center">
            Klicke auf einen Muskel im Modell, um ihn als {selectionTarget === 'primary' ? 'Primär' : 'Sekundär'} zuzuweisen.
          </span>
        </div>
      </div>
    </div>

    <!-- Rest Seconds & Instructions -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div>
        <Input
          label="Satzpause (Sek.)"
          type="number"
          step={15}
          min={30}
          max={300}
          bind:value={restSeconds}
        />
      </div>
      <div class="sm:col-span-2">
        <Textarea
          label="Ausführungshinweise / Form-Tipps (Optional)"
          rows={2}
          placeholder="z. B. Standbein leicht nach vorne versetzen, Rumpf aufrecht halten..."
          bind:value={instructions}
        />
      </div>
    </div>

    <!-- Modal Actions -->
    <div class="flex items-center justify-end gap-2 border-t border-[var(--border-subtle)] pt-3">
      <Btn variant="secondary" size="md" onclick={onclose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" type="submit" loading={isSaving}>Übung speichern</Btn>
    </div>
  </form>
</Modal>
