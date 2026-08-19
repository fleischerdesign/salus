<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { toggleMedicationLog } from '$lib/mutations/medication';

  interface Props {
    date?: string;
  }

  let { date = todayString() }: Props = $props();

  const medsQuery = useQuery(
    async () => {
      const dayStart = date + 'T00:00:00';
      const dayEnd = date + 'T23:59:59.999';

      const [allMeds, allSchedules, allLogs] = await Promise.all([
        db.medication.toArray(),
        db.medication_schedule.toArray(),
        db.medication_log.where('taken_at').between(dayStart, dayEnd).toArray()
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
          dosage: sched?.dosage || m.strength || '1 Dosis',
          time: timeStr,
          instructions: m.instructions || 'Nach Anweisung',
          taken: takenSet.has(m.id)
        };
      });
    },
    () => date
  );

  const meds = $derived(medsQuery.value ?? []);
  const takenCount = $derived(meds.filter((m) => m.taken).length);

  async function handleToggle(medId: string, scheduleId: string | null, time: string | null) {
    await toggleMedicationLog(medId, scheduleId, time);
  }
</script>

<div
  class="rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
>
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-2 text-sm font-extrabold text-[var(--text-main)]">
      <div
        class="flex h-8 w-8 items-center justify-center rounded-xl bg-[var(--color-primary-soft)]/20 text-[var(--color-primary)]"
      >
        <Icon name="medication" size="sm" />
      </div>
      <span>Tägliche Supplement- &amp; Medikamenten-Dosen</span>
    </div>
    {#if meds.length > 0}
      <Badge variant="primary" class="text-xs font-bold"
        >{takenCount} von {meds.length} eingenommen</Badge
      >
    {/if}
  </div>

  {#if meds.length === 0}
    <div class="py-6 text-center text-xs text-[var(--text-muted)] italic">
      Noch keine Medikamente oder Supplemente hinterlegt.
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
      {#each meds as med (med.id)}
        <button
          type="button"
          onclick={() => handleToggle(med.id, med.scheduleId, med.time)}
          class="flex cursor-pointer items-center justify-between gap-3 rounded-2xl border p-3.5 text-left transition-all {med.taken
            ? 'border-emerald-500/30 bg-emerald-500/10 shadow-xs'
            : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] hover:border-[var(--border-strong)]'}"
        >
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <span
                class="truncate text-xs font-bold {med.taken
                  ? 'text-emerald-700 dark:text-emerald-300'
                  : 'text-[var(--text-main)]'}"
              >
                {med.name}
              </span>
              <span
                class="rounded-md bg-[var(--bg-surface-100)] px-1.5 py-0.5 text-[0.625rem] font-bold text-[var(--text-muted)]"
              >
                {med.dosage}
              </span>
            </div>
            <span class="text-[0.6875rem] text-[var(--text-muted)]"
              >{med.time} &bull; {med.instructions}</span
            >
          </div>

          <div
            class="flex h-6 w-6 shrink-0 items-center justify-center rounded-xl border transition-all {med.taken
              ? 'border-emerald-500 bg-emerald-500 text-white'
              : 'border-[var(--border-strong)] bg-[var(--bg-surface-0)]'}"
          >
            {#if med.taken}
              <Icon name="check" size="sm" />
            {/if}
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>
