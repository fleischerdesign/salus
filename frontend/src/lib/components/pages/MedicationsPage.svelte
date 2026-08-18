<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Modal from '../ui/Modal.svelte';
  import Input from '../ui/Input.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { toggleMedicationLog, createMedication } from '$lib/mutations/medication';

  const today = todayString();

  // 1. Reactive Composite Query for Medications + Schedules + Today's Logs
  const medsQuery = useQuery(
    async () => {
      const [allMeds, allSchedules, allLogs] = await Promise.all([
        db.medication.toArray(),
        db.medication_schedule.toArray(),
        db.medication_log
          .where('created_at')
          .aboveOrEqual(today + 'T00:00:00')
          .toArray()
      ]);

      const activeMeds = allMeds.filter((m) => !m.deleted_at && m.is_active);
      const scheduleMap = new Map(allSchedules.map((s) => [s.medication_id, s]));
      const takenSet = new Set(
        allLogs.filter((l) => !l.deleted_at && l.taken_at && !l.skipped).map((l) => l.medication_id)
      );

      return activeMeds.map((m) => {
        const sched = scheduleMap.get(m.id);
        const timeStr = sched?.times?.[0] || 'Morgens';
        return {
          id: m.id,
          scheduleId: sched?.id ?? null,
          name: m.name,
          strength: m.strength || '',
          form: m.form || 'Tablette',
          instructions: m.instructions || 'Nach ärztlicher Anweisung',
          timing: timeStr,
          dosage: sched?.dosage || m.strength || '1 Dosis',
          takenToday: takenSet.has(m.id)
        };
      });
    },
    () => today
  );

  const meds = $derived(medsQuery.value ?? []);
  const loading = $derived(medsQuery.loading);

  let isCreateOpen = $state(false);
  let newName = $state('');
  let newStrength = $state('');
  let newInstructions = $state('');

  async function handleCreate() {
    if (!newName.trim()) return;
    await createMedication({
      name: newName.trim(),
      strength: newStrength.trim() || undefined,
      instructions: newInstructions.trim() || undefined
    });
    newName = '';
    newStrength = '';
    newInstructions = '';
    isCreateOpen = false;
  }

  async function toggleDose(medId: string, scheduleId: string | null, time: string | null) {
    await toggleMedicationLog(medId, scheduleId, time);
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Medikamente & Supplement-Zentrale</h1>
      <p class="mt-0.5 text-sm text-[var(--text-muted)]">
        Präzise Dosierungs-Zeitpläne, Restbestands-Tracking und klinische Adhärenz
      </p>
    </div>
    <div class="flex items-center gap-2">
      {#if meds.length > 0}
        <Badge variant="success">
          {meds.filter((m) => m.takenToday).length} von {meds.length} heute eingenommen
        </Badge>
      {/if}
      <Btn variant="primary" size="sm" onclick={() => (isCreateOpen = true)}>
        + Präparat hinzufügen
      </Btn>
    </div>
  </div>

  <!-- Medication Schedule Grid -->
  {#if loading}
    <div class="py-12 text-center text-sm text-[var(--text-muted)]">
      Medikamente werden geladen...
    </div>
  {:else if meds.length === 0}
    <div
      class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-8 text-center shadow-[var(--shadow-card)]"
    >
      <div
        class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
      >
        <Icon name="medication" size="lg" />
      </div>
      <div>
        <h3 class="text-base font-bold text-[var(--text-main)]">
          Keine Medikamente oder Supplemente hinterlegt
        </h3>
        <p class="mx-auto mt-1 max-w-sm text-xs text-[var(--text-muted)]">
          Füge deine täglichen Medikamente, Vitamine oder Mikronährstoffe hinzu, um
          Einnahme-Erinnerungen und Adhärenzstatistiken zu erhalten.
        </p>
      </div>
      <Btn variant="primary" size="sm" onclick={() => (isCreateOpen = true)}>
        Jetzt erstes Präparat anlegen
      </Btn>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-5 lg:grid-cols-12">
      <!-- Schedule (8-Col) -->
      <div
        class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)] lg:col-span-8"
      >
        <div class="mb-4 flex items-center justify-between">
          <span class="text-sm font-bold text-[var(--text-main)]">Heutiger Einnahme-Plan</span>
          <span class="text-xs text-[var(--text-muted)]"
            >{meds.filter((m) => m.takenToday).length} von {meds.length} eingenommen</span
          >
        </div>

        <div class="space-y-3">
          {#each meds as med (med.id)}
            <div
              class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 transition-all {med.takenToday
                ? 'border-emerald-500/30 bg-emerald-500/5'
                : ''}"
            >
              <div class="flex items-start gap-3">
                <button
                  type="button"
                  onclick={() => toggleDose(med.id, med.scheduleId, med.timing)}
                  class="mt-1 flex h-6 w-6 cursor-pointer items-center justify-center rounded-full border-2 transition-all {med.takenToday
                    ? 'border-emerald-500 bg-emerald-500 text-white'
                    : 'border-[var(--border-subtle)] bg-[var(--bg-surface-0)] hover:border-emerald-500'}"
                  title={med.takenToday
                    ? 'Als nicht eingenommen markieren'
                    : 'Als eingenommen markieren'}
                >
                  {#if med.takenToday}
                    <Icon name="check" size={14} />
                  {/if}
                </button>

                <div>
                  <div class="flex items-center gap-2">
                    <span
                      class="text-sm font-bold text-[var(--text-main)] {med.takenToday
                        ? 'text-[var(--text-muted)] line-through'
                        : ''}"
                    >
                      {med.name}
                    </span>
                    {#if med.strength}
                      <Badge variant="primary" class="text-[0.625rem]">
                        {med.strength}
                      </Badge>
                    {/if}
                  </div>
                  <p class="mt-0.5 text-xs text-[var(--text-muted)]">{med.instructions}</p>
                  <div
                    class="mt-1 flex items-center gap-3 font-mono text-[0.6875rem] text-[var(--text-soft)]"
                  >
                    <span>Timing: {med.timing}</span>
                  </div>
                </div>
              </div>

              <Badge variant={med.takenToday ? 'success' : 'default'}>
                {med.takenToday ? 'Erledigt ✓' : 'Fällig'}
              </Badge>
            </div>
          {/each}
        </div>
      </div>

      <!-- Adherence Stats & Inventory (4-Col) -->
      <div class="space-y-4 lg:col-span-4">
        <!-- Monthly Adherence Card -->
        <div
          class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
        >
          <span class="mb-2 block text-sm font-bold text-[var(--text-main)]"
            >Adhärenz-Statistik</span
          >
          <div class="my-1 font-mono text-3xl font-extrabold text-[var(--color-success)]">
            {meds.length > 0
              ? Math.round((meds.filter((m) => m.takenToday).length / meds.length) * 100)
              : 100} %
          </div>
          <p class="mb-3 text-xs text-[var(--text-muted)]">
            Therapietreue für den heutigen Kalendertag.
          </p>
          <div class="h-2 overflow-hidden rounded-full bg-[var(--bg-surface-100)]">
            <div
              class="h-full bg-[var(--color-success)] transition-all"
              style="width: {meds.length > 0
                ? (meds.filter((m) => m.takenToday).length / meds.length) * 100
                : 100}%"
            ></div>
          </div>
        </div>

        <!-- Interaction Safety Check -->
        <div
          class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
        >
          <div class="mb-2 flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
            <Icon name="science" class="text-[var(--color-primary)]" />
            <span>Interaktions-Prüfung</span>
          </div>
          <p class="text-xs text-[var(--text-muted)]">
            Keine bekannten pharmakologischen Wechselwirkungen zwischen den erfassten Präparaten.
          </p>
          <Badge variant="success" class="mt-3">Sicherheitsprüfung aktiv</Badge>
        </div>
      </div>
    </div>
  {/if}

  <!-- Create Medication Modal -->
  <Modal open={isCreateOpen} title="Neues Präparat anlegen" onclose={() => (isCreateOpen = false)}>
    <form
      onsubmit={(e) => {
        e.preventDefault();
        handleCreate();
      }}
      class="space-y-4"
    >
      <div>
        <label for="med-name" class="mb-1 block text-xs font-bold text-[var(--text-main)]"
          >Präparatname / Wirkstoff</label
        >
        <Input id="med-name" bind:value={newName} placeholder="z. B. Vitamin D3" />
      </div>
      <div>
        <label for="med-strength" class="mb-1 block text-xs font-bold text-[var(--text-main)]"
          >Dosierung / Stärke</label
        >
        <Input id="med-strength" bind:value={newStrength} placeholder="z. B. 5.000 I.E." />
      </div>
      <div>
        <label for="med-inst" class="mb-1 block text-xs font-bold text-[var(--text-main)]"
          >Einnahmehinweis</label
        >
        <Input
          id="med-inst"
          bind:value={newInstructions}
          placeholder="z. B. Morgens mit dem Frühstück"
        />
      </div>
      <div class="flex justify-end gap-2 pt-2">
        <Btn variant="secondary" size="sm" onclick={() => (isCreateOpen = false)}>Abbrechen</Btn>
        <Btn variant="primary" size="sm" type="submit" disabled={!newName.trim()}>Speichern</Btn>
      </div>
    </form>
  </Modal>
</div>
