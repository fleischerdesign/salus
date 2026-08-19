<script lang="ts">
  import Modal from '../ui/Modal.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Textarea from '../ui/Textarea.svelte';
  import SegmentedControl from '../ui/SegmentedControl.svelte';
  import AnatomicalBodyVector from '../track/AnatomicalBodyVector.svelte';
  import { ANATOMICAL_PATH_TO_DETAILED_KEY } from '../track/anatomy-data';
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
  let instructions = $state('');
  let restSeconds = $state(90);
  let isSaving = $state(false);
  let errorMsg = $state('');

  // Target Mode: 'primary' vs 'secondary'
  let targetMode = $state<string>('primary');
  let activeGroup = $state<MuscleGroup>('Brust');
  let mannequinView = $state<string>('anterior');

  const equipmentOptions: { value: EquipmentType; label: string }[] = [
    { value: 'Langhantel', label: 'Langhantel' },
    { value: 'Kurzhantel', label: 'Kurzhantel' },
    { value: 'Kabelzug', label: 'Kabelzug' },
    { value: 'Maschine', label: 'Maschine' },
    { value: 'Eigengewicht', label: 'Eigengewicht' }
  ];

  // Group detailed muscles by parent group
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

  // Dynamic path color map for live 2D body preview
  const pathColorMap = $derived.by(() => {
    const map: Record<string, string> = {};

    for (const key of selectedPrimaryMuscles) {
      const def = DETAILED_MUSCLE_MAP[key as DetailedMuscleKey];
      if (def) {
        for (const pid of def.svgPathIds) {
          map[pid] = 'var(--color-primary)';
        }
      }
    }

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

  function toggleMuscle(key: string) {
    if (targetMode === 'primary') {
      if (selectedPrimaryMuscles.includes(key)) {
        selectedPrimaryMuscles = selectedPrimaryMuscles.filter((k) => k !== key);
      } else {
        selectedPrimaryMuscles = [...selectedPrimaryMuscles, key];
        selectedSecondaryMuscles = selectedSecondaryMuscles.filter((k) => k !== key);
      }
    } else {
      if (selectedSecondaryMuscles.includes(key)) {
        selectedSecondaryMuscles = selectedSecondaryMuscles.filter((k) => k !== key);
      } else {
        selectedSecondaryMuscles = [...selectedSecondaryMuscles, key];
        selectedPrimaryMuscles = selectedPrimaryMuscles.filter((k) => k !== key);
      }
    }
  }

  function removePrimary(key: string) {
    selectedPrimaryMuscles = selectedPrimaryMuscles.filter((k) => k !== key);
  }

  function removeSecondary(key: string) {
    selectedSecondaryMuscles = selectedSecondaryMuscles.filter((k) => k !== key);
  }

  function handleBodyVectorClick(group: MuscleGroup, detailedId: string) {
    const detailedKey = ANATOMICAL_PATH_TO_DETAILED_KEY[detailedId] || group;
    toggleMuscle(detailedKey);
  }

  function getMuscleDisplayName(key: string): string {
    const def = DETAILED_MUSCLE_MAP[key as DetailedMuscleKey];
    return def ? def.name : key;
  }

  function resetForm() {
    name = '';
    selectedPrimaryMuscles = ['chest_clavicular'];
    selectedSecondaryMuscles = [];
    equipment = 'Langhantel';
    instructions = '';
    restSeconds = 90;
    errorMsg = '';
    isSaving = false;
    targetMode = 'primary';
    activeGroup = 'Brust';
    mannequinView = 'anterior';
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

      const primaryStr = selectedPrimaryMuscles.join(', ');
      const secondaryStr =
        selectedSecondaryMuscles.length > 0 ? selectedSecondaryMuscles.join(', ') : null;

      await createExercise({
        name: name.trim(),
        equipment: equipment.toLowerCase(),
        primary_muscles: primaryStr,
        secondary_muscles: secondaryStr,
        description: null,
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
  icon="fitness_center"
  size="lg"
  {onclose}
>
  {#if errorMsg}
    <div
      class="mb-3 rounded-xl border border-rose-500/30 bg-rose-500/10 p-2.5 text-xs font-bold text-rose-500"
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
    <!-- Top Metadata Grid -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-12">
      <div class="sm:col-span-6">
        <Input
          label="Name der Übung"
          required
          placeholder="z. B. Bulgarian Split Squats..."
          bind:value={name}
        />
      </div>
      <div class="sm:col-span-3">
        <Select
          label="Equipment"
          required
          bind:value={equipment}
          options={equipmentOptions}
        />
      </div>
      <div class="sm:col-span-3">
        <Input
          label="Pause (Sek.)"
          type="number"
          step={15}
          min={30}
          max={300}
          bind:value={restSeconds}
        />
      </div>
    </div>

    <!-- ═════════════════════════════════════════════════════════════ -->
    <!-- MAIN INTERACTIVE SECTION: 7/5 SPLIT (Picker + 2D Body)        -->
    <!-- ═════════════════════════════════════════════════════════════ -->
    <div class="grid grid-cols-1 gap-3.5 md:grid-cols-12 items-stretch">
      <!-- Left Column: Muscle Selector & Active Tags (7 cols) -->
      <div
        class="flex flex-col justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5 md:col-span-7 space-y-3"
      >
        <div class="space-y-2.5">
          <!-- Mode Switch: Primär vs Sekundär -->
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-[var(--text-main)]">
              Zielmuskeln
            </span>
            <SegmentedControl
              size="sm"
              bind:value={targetMode}
              options={[
                { value: 'primary', label: `Primär (${selectedPrimaryMuscles.length})` },
                { value: 'secondary', label: `Sekundär (${selectedSecondaryMuscles.length})` }
              ]}
            />
          </div>

          <!-- Active Selected Tags Summary for Active Mode -->
          <div class="flex flex-wrap gap-1.5 min-h-[30px] items-center">
            <span class="text-[11px] font-bold {targetMode === 'primary' ? 'text-[var(--color-primary)]' : 'text-indigo-400'}">
              {targetMode === 'primary' ? 'Primär:' : 'Sekundär:'}
            </span>
            {#if targetMode === 'primary'}
              {#each selectedPrimaryMuscles as key (key)}
                <span
                  class="inline-flex items-center gap-1 rounded-lg border border-[var(--color-primary)]/40 bg-[var(--color-primary-soft)] px-2 py-0.5 text-[11px] font-bold text-[var(--color-primary)] shadow-2xs"
                >
                  <span>{getMuscleDisplayName(key)}</span>
                  <button
                    type="button"
                    onclick={() => removePrimary(key)}
                    class="cursor-pointer hover:opacity-70 text-[var(--color-primary)]"
                    aria-label="Entfernen"
                  >
                    &times;
                  </button>
                </span>
              {/each}
              {#if selectedPrimaryMuscles.length === 0}
                <span class="text-xs italic text-[var(--text-muted)]">
                  Keine Primärmuskeln gewählt (wähle unten)
                </span>
              {/if}
            {:else}
              {#each selectedSecondaryMuscles as key (key)}
                <span
                  class="inline-flex items-center gap-1 rounded-lg border border-indigo-400/40 bg-indigo-500/10 px-2 py-0.5 text-[11px] font-bold text-indigo-400 shadow-2xs"
                >
                  <span>{getMuscleDisplayName(key)}</span>
                  <button
                    type="button"
                    onclick={() => removeSecondary(key)}
                    class="cursor-pointer hover:opacity-70 text-indigo-400"
                    aria-label="Entfernen"
                  >
                    &times;
                  </button>
                </span>
              {/each}
              {#if selectedSecondaryMuscles.length === 0}
                <span class="text-xs italic text-[var(--text-muted)]">
                  Keine Synergisten gewählt (optional)
                </span>
              {/if}
            {/if}
          </div>

          <!-- Muscle Group Horizontal Scroll Tabs -->
          <div class="no-scrollbar flex gap-1 overflow-x-auto border-t border-[var(--border-subtle)] pt-2.5">
            {#each MUSCLE_GROUPS as group}
              {@const hasP = selectedPrimaryMuscles.some(
                (k) => DETAILED_MUSCLE_MAP[k as DetailedMuscleKey]?.group === group
              )}
              {@const hasS = selectedSecondaryMuscles.some(
                (k) => DETAILED_MUSCLE_MAP[k as DetailedMuscleKey]?.group === group
              )}
              <button
                type="button"
                onclick={() => (activeGroup = group)}
                class="cursor-pointer flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-bold whitespace-nowrap transition-all {activeGroup ===
                group
                  ? targetMode === 'primary'
                    ? 'bg-[var(--color-primary)] text-white shadow-2xs'
                    : 'bg-indigo-500 text-white shadow-2xs'
                  : 'border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
              >
                <span>{group}</span>
                {#if hasP}
                  <span class="h-1.5 w-1.5 rounded-full {activeGroup === group ? 'bg-white' : 'bg-[var(--color-primary)]'}"></span>
                {:else if hasS}
                  <span class="h-1.5 w-1.5 rounded-full {activeGroup === group ? 'bg-white' : 'bg-indigo-400'}"></span>
                {/if}
              </button>
            {/each}
          </div>

          <!-- Muscle Chips of Selected Group -->
          <div class="flex flex-wrap gap-1.5 pt-0.5">
            {#each musclesByGroup.get(activeGroup) ?? [] as muscle (muscle.key)}
              {@const isPrimary = selectedPrimaryMuscles.includes(muscle.key)}
              {@const isSecondary = selectedSecondaryMuscles.includes(muscle.key)}
              <button
                type="button"
                onclick={() => toggleMuscle(muscle.key)}
                class="cursor-pointer rounded-lg border px-2.5 py-1 text-xs font-semibold transition-all {isPrimary
                  ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)] text-[var(--color-primary)] font-bold ring-1 ring-[var(--color-primary)]'
                  : isSecondary
                    ? 'border-indigo-400 bg-indigo-500/10 text-indigo-400 font-bold ring-1 ring-indigo-400'
                    : 'border-[var(--border-subtle)] bg-[var(--bg-surface-0)] text-[var(--text-main)] hover:border-[var(--border-strong)]'}"
              >
                <span>{muscle.name}</span>
                {#if isPrimary}
                  <span class="ml-1 text-[10px] font-bold text-[var(--color-primary)]">(P)</span>
                {:else if isSecondary}
                  <span class="ml-1 text-[10px] font-bold text-indigo-400">(S)</span>
                {/if}
              </button>
            {/each}
          </div>
        </div>
      </div>

      <!-- Right Column: Integrated 2D Anatomical Vector (5 cols) -->
      <div
        class="flex flex-col items-center justify-between rounded-2xl border border-[var(--border-subtle)] bg-gradient-to-b from-[var(--bg-surface-50)] to-[var(--bg-surface-100)] p-3 md:col-span-5"
      >
        <div class="flex w-full items-center justify-between">
          <span class="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)]">
            2D-Modell
          </span>
          <SegmentedControl
            size="sm"
            bind:value={mannequinView}
            options={[
              { value: 'anterior', label: 'Front' },
              { value: 'posterior', label: 'Rück' }
            ]}
          />
        </div>

        <div class="my-1 flex h-[210px] w-full items-center justify-center">
          <AnatomicalBodyVector
            view={mannequinView as 'anterior' | 'posterior'}
            {pathColorMap}
            onselect={handleBodyVectorClick}
          />
        </div>

        <div class="flex items-center gap-3 text-[10px] text-[var(--text-muted)]">
          <div class="flex items-center gap-1">
            <span class="h-2 w-2 rounded-full bg-[var(--color-primary)]"></span>
            <span>Primär</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="h-2 w-2 rounded-full bg-indigo-400"></span>
            <span>Sekundär</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Optional Ausführungshinweise (Collapsible) -->
    <details class="group rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2.5">
      <summary class="flex cursor-pointer items-center justify-between text-xs font-semibold text-[var(--text-muted)] select-none hover:text-[var(--text-main)]">
        <span>▸ Ausführungshinweise & Form-Tipps (Optional)</span>
      </summary>
      <div class="mt-2.5 pt-2 border-t border-[var(--border-subtle)]">
        <Textarea
          rows={2}
          placeholder="z. B. Standbein leicht nach vorne versetzen, Rumpf aufrecht halten..."
          bind:value={instructions}
        />
      </div>
    </details>

    <!-- Modal Actions -->
    <div class="flex items-center justify-end gap-2 border-t border-[var(--border-subtle)] pt-3">
      <Btn variant="secondary" size="md" onclick={onclose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" type="submit" loading={isSaving}>Übung anlegen</Btn>
    </div>
  </form>
</Modal>
