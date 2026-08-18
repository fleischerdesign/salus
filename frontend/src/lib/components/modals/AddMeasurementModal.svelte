<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import { createMeasurement } from '$lib/mutations/measurement';

  interface Props {
    open: boolean;
    metricCode: string;
    metricName: string;
    unit: string;
    onclose: () => void;
    onsaved?: () => void;
  }

  let { open, metricCode, metricName, unit, onclose, onsaved }: Props = $props();

  let value = $state('');
  let measuredAt = $state('');
  let note = $state('');
  let isSaving = $state(false);

  $effect(() => {
    if (open) {
      value = '';
      note = '';
      // Default to current local date/time in YYYY-MM-DDTHH:mm format
      const now = new Date();
      const offset = now.getTimezoneOffset() * 60000;
      measuredAt = new Date(now.getTime() - offset).toISOString().slice(0, 16);
    }
  });

  async function handleSave() {
    const num = parseFloat(value);
    if (isNaN(num)) return;

    isSaving = true;
    try {
      await createMeasurement(metricCode, {
        value: num,
        measured_at: measuredAt ? new Date(measuredAt).toISOString() : new Date().toISOString(),
        note: note.trim() || null,
        source: 'manual'
      });
      onsaved?.();
      onclose();
    } catch (e) {
      console.error('Fehler beim Speichern des Messwerts:', e);
    } finally {
      isSaving = false;
    }
  }
</script>

<Modal
  {open}
  title="Messwert erfassen"
  subtitle={`${metricName} (${unit || 'Einheit'})`}
  icon="add"
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
        label={`Messwert (${unit})`}
        type="number"
        step="any"
        placeholder="z. B. 120"
        bind:value
        required
      />
    </div>

    <div>
      <Input label="Zeitpunkt der Messung" type="datetime-local" bind:value={measuredAt} required />
    </div>

    <div>
      <Textarea
        label="Notiz / Kontext (Optional)"
        placeholder="z. B. Nüchtern nach dem Aufstehen, nach dem Training..."
        bind:value={note}
        rows={2}
      />
    </div>

    <div class="flex items-center justify-end gap-2 border-t border-[var(--border-subtle)] pt-4">
      <Btn variant="secondary" size="md" onclick={onclose} disabled={isSaving}>Abbrechen</Btn>
      <Btn variant="primary" size="md" type="submit" disabled={isSaving || !value}>
        {isSaving ? 'Wird gespeichert...' : 'Messwert speichern'}
      </Btn>
    </div>
  </form>
</Modal>
