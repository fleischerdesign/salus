<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import { createGoal, updateGoal, deleteGoal } from '$lib/mutations/goal';

  interface Props {
    open: boolean;
    metricCode: string;
    metricName: string;
    unit: string;
    goal?: {
      id?: string;
      target_value?: number;
      direction?: string;
      frequency?: string;
      deadline?: string | null;
    } | null;
    onclose: () => void;
    onsave?: () => void;
  }

  let { open, metricCode, metricName, unit, goal = null, onclose, onsave }: Props = $props();

  let targetValue = $state('');
  let direction = $state<'decrease' | 'increase'>('decrease');
  let frequency = $state('daily');
  let deadline = $state('');
  let isSaving = $state(false);

  $effect(() => {
    if (open) {
      if (goal && goal.target_value !== undefined) {
        targetValue = String(goal.target_value);
        direction = (goal.direction as 'decrease' | 'increase') || 'decrease';
        frequency = goal.frequency || 'daily';
        deadline = goal.deadline || '';
      } else {
        targetValue = '';
        direction = 'decrease';
        frequency = 'daily';
        deadline = '';
      }
    }
  });

  const directionOptions = [
    { value: 'decrease', label: 'Wert senken (z. B. Gewicht, KFA, Blutdruck)' },
    { value: 'increase', label: 'Wert steigern (z. B. Schritte, Schlaf, Muskelmasse)' }
  ];

  const frequencyOptions = [
    { value: 'daily', label: 'Täglicher Sollwert' },
    { value: 'weekly', label: 'Wöchentlicher Sollwert' },
    { value: 'milestone', label: 'Fester Zielwert mit Stichtag' }
  ];

  async function handleSave() {
    const val = parseFloat(targetValue);
    if (isNaN(val)) return;

    isSaving = true;
    try {
      if (goal?.id) {
        await updateGoal(goal.id, {
          target_value: val,
          direction,
          frequency,
          deadline: deadline || null
        });
      } else {
        await createGoal(metricCode, val, direction, frequency, deadline || undefined);
      }
      onsave?.();
      onclose();
    } catch (e) {
      console.error('Fehler beim Speichern des Ziels:', e);
    } finally {
      isSaving = false;
    }
  }

  async function handleDelete() {
    if (!goal?.id) return;
    if (!confirm('Möchtest du dieses persönliche Ziel wirklich löschen?')) return;

    isSaving = true;
    try {
      await deleteGoal(goal.id);
      onsave?.();
      onclose();
    } catch (e) {
      console.error('Fehler beim Löschen des Ziels:', e);
    } finally {
      isSaving = false;
    }
  }
</script>

<Modal
  {open}
  title={goal?.id ? `Ziel für ${metricName} bearbeiten` : `Ziel für ${metricName} festlegen`}
  subtitle={`Definiere deinen persönlichen Sollwert in ${unit || 'Einheiten'}`}
  icon="flag"
  {onclose}
>
  <form
    onsubmit={(e) => {
      e.preventDefault();
      handleSave();
    }}
    class="space-y-4"
  >
    <div>
      <Input
        label={`Persönlicher Zielwert (${unit})`}
        type="number"
        step="any"
        placeholder="z. B. 75.0"
        bind:value={targetValue}
        required
      />
    </div>

    <div>
      <Select label="Zielrichtung" options={directionOptions} bind:value={direction} />
    </div>

    <div>
      <Select label="Intervall / Typ" options={frequencyOptions} bind:value={frequency} />
    </div>

    {#if frequency === 'milestone'}
      <div>
        <Input label="Stichtag / Frist (Optional)" type="date" bind:value={deadline} />
      </div>
    {/if}

    <div class="flex items-center justify-between border-t border-border-subtle pt-4">
      <div>
        {#if goal?.id}
          <button
            type="button"
            class="cursor-pointer text-xs font-semibold text-vital hover:underline"
            onclick={handleDelete}
            disabled={isSaving}
          >
            Ziel löschen
          </button>
        {/if}
      </div>

      <div class="flex items-center gap-2">
        <Btn variant="secondary" size="md" onclick={onclose} disabled={isSaving}>Abbrechen</Btn>
        <Btn variant="primary" size="md" type="submit" disabled={isSaving || !targetValue}>
          {isSaving ? 'Speichern...' : 'Ziel speichern'}
        </Btn>
      </div>
    </div>
  </form>
</Modal>
