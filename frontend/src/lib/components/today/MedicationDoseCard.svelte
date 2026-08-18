<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { toggleMedicationLog } from '$lib/mutations/medication';

  const today = todayString();

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
          dosage: sched?.dosage || m.strength || '1 Dosis',
          time: timeStr,
          instructions: m.instructions || 'Nach Anweisung',
          taken: takenSet.has(m.id)
        };
      });
    },
    () => today
  );

  const meds = $derived(medsQuery.value ?? []);
  const takenCount = $derived(meds.filter((m) => m.taken).length);

  async function handleToggle(medId: string, scheduleId: string | null, time: string | null) {
    await toggleMedicationLog(medId, scheduleId, time);
  }
</script>

<div
  class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-[18px] shadow-[var(--shadow-card)]"
>
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
      <Icon name="medication" class="text-[var(--color-primary)]" />
      <span>Tägliche Supplement- & Medikamenten-Dosen</span>
    </div>
    {#if meds.length > 0}
      <Badge variant={takenCount === meds.length ? 'success' : 'default'}>
        {takenCount} von {meds.length} eingenommen
      </Badge>
    {/if}
  </div>

  {#if meds.length === 0}
    <div class="py-4 text-center text-xs text-[var(--text-muted)]">
      Keine aktiven Medikamente hinterlegt.
    </div>
  {:else}
    <div class="space-y-2">
      {#each meds as med (med.id)}
        <div
          class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 transition-all {med.taken
            ? 'border-emerald-500/30 bg-emerald-500/10'
            : ''}"
        >
          <div class="flex items-center gap-3">
            <button
              type="button"
              onclick={() => handleToggle(med.id, med.scheduleId, med.time)}
              class="flex h-5 w-5 cursor-pointer items-center justify-center rounded-full border-2 transition-all {med.taken
                ? 'border-emerald-500 bg-emerald-500 text-white'
                : 'border-[var(--border-strong)]'}"
            >
              {#if med.taken}
                <Icon name="check" size={12} />
              {/if}
            </button>

            <div>
              <div class="flex items-center gap-2">
                <span
                  class="text-xs font-bold text-[var(--text-main)] {med.taken
                    ? 'text-[var(--text-muted)] line-through'
                    : ''}"
                >
                  {med.name}
                </span>
                <span class="font-mono text-[0.6875rem] text-[var(--text-soft)]">{med.dosage}</span>
              </div>
              <span class="text-[0.6875rem] text-[var(--text-muted)]">{med.instructions}</span>
            </div>
          </div>

          <Badge variant="default" class="font-mono text-[0.625rem]">{med.time}</Badge>
        </div>
      {/each}
    </div>
  {/if}
</div>
