<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { Medication, MedicationLog, MedicationSchedule } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import MedicationGrid from '$components/medications/MedicationGrid.svelte';
  import MedicationForm from '$components/medications/MedicationForm.svelte';
  import { createMedication, toggleMedicationLog } from '$lib/mutations/medication';

  let loading = $state(true);
  let medications = $state<Medication[]>([]);
  let schedules = $state<MedicationSchedule[]>([]);
  let logs = $state<MedicationLog[]>([]);
  let formOpen = $state(false);

  $effect(() => {
    const sub1 = liveQuery(() =>
      db.medication
        .where('deleted_at')
        .equals('')
        .or('deleted_at')
        .equals(null as any)
        .toArray()
    ).subscribe((v) => {
      medications = v;
    });
    const sub2 = liveQuery(() => db.medication_schedule.toArray()).subscribe((v) => {
      schedules = v;
    });
    const sub3 = liveQuery(() => db.medication_log.toArray()).subscribe((v) => {
      logs = v;
      loading = false;
    });
    return () => {
      sub1.unsubscribe();
      sub2.unsubscribe();
      sub3.unsubscribe();
    };
  });

  const today = $derived(new Date().toISOString().split('T')[0]);
  const todayWeekday = $derived(new Date().getDay() || 7);

  const nextDoses = $derived.by(() => {
    const result: Record<string, string | null> = {};
    for (const med of medications) {
      const medSchedules = schedules.filter((s) => s.medication_id === med.id && !s.deleted_at);
      if (medSchedules.length === 0) {
        result[med.id] = null;
        continue;
      }

      const now = new Date();
      const nowMinutes = now.getHours() * 60 + now.getMinutes();

      let nextTime: string | null = null;
      let nextMinutes = Infinity;

      for (const sched of medSchedules) {
        if (sched.days_of_week && !sched.days_of_week.includes(todayWeekday)) continue;
        if (sched.start_date && today < sched.start_date) continue;
        if (sched.end_date && today > sched.end_date) continue;

        for (const t of sched.times) {
          const [h, m] = t.split(':').map(Number);
          const tMinutes = h * 60 + m;

          const alreadyTaken = logs.some(
            (l) =>
              l.medication_id === med.id &&
              l.schedule_id === sched.id &&
              !l.deleted_at &&
              !l.skipped &&
              l.taken_at?.startsWith(today)
          );
          if (alreadyTaken) continue;

          if (tMinutes > nowMinutes && tMinutes < nextMinutes) {
            nextMinutes = tMinutes;
            nextTime = t;
          }
        }
      }

      if (nextTime) {
        result[med.id] = `Today ${nextTime}`;
      } else {
        const tomorrowSchedules = schedules.filter(
          (s) => s.medication_id === med.id && !s.deleted_at && s.times.length > 0
        );
        if (tomorrowSchedules.length > 0) {
          result[med.id] = 'Tomorrow';
        } else {
          result[med.id] = null;
        }
      }
    }
    return result;
  });

  const adherenceRates = $derived.by(() => {
    const result: Record<string, number> = {};
    for (const med of medications) {
      const medLogs = logs.filter((l) => l.medication_id === med.id && !l.deleted_at);
      if (medLogs.length === 0) {
        result[med.id] = 0;
      } else {
        result[med.id] = medLogs.filter((l) => !l.skipped).length / medLogs.length;
      }
    }
    return result;
  });

  const todayItems = $derived.by(() => {
    const items: {
      medId: string;
      medName: string;
      colorHex: string;
      icon: string;
      dosage: string;
      time: string;
      scheduleId: string;
      taken: boolean;
    }[] = [];

    for (const med of medications) {
      const medSchedules = schedules.filter((s) => s.medication_id === med.id && !s.deleted_at);
      for (const sched of medSchedules) {
        if (sched.days_of_week && !sched.days_of_week.includes(todayWeekday)) continue;
        if (sched.start_date && today < sched.start_date) continue;
        if (sched.end_date && today > sched.end_date) continue;

        for (const t of sched.times) {
          const taken = logs.some(
            (l) =>
              l.medication_id === med.id &&
              l.schedule_id === sched.id &&
              !l.deleted_at &&
              !l.skipped &&
              l.taken_at?.startsWith(today)
          );

          items.push({
            medId: med.id,
            medName: med.name,
            colorHex: med.color_hex,
            icon: med.icon,
            dosage: sched.dosage,
            time: t,
            scheduleId: sched.id || '',
            taken
          });
        }
      }
    }
    items.sort((a, b) => a.time.localeCompare(b.time));
    return items;
  });

  async function handleSave(data: any) {
    await createMedication(data);
    formOpen = false;
  }

  async function handleToggle(medicationId: string) {
    const medSchedules = schedules.filter((s) => s.medication_id === medicationId && !s.deleted_at);
    if (medSchedules.length > 0) {
      const now = new Date();
      const nowMinutes = now.getHours() * 60 + now.getMinutes();
      let bestScheduleId: string | null = null;
      let bestTime: string | null = null;
      let bestDiff = Infinity;

      for (const sched of medSchedules) {
        for (const t of sched.times) {
          const [h, m] = t.split(':').map(Number);
          const diff = Math.abs(nowMinutes - (h * 60 + m));
          if (diff < bestDiff) {
            bestDiff = diff;
            bestTime = t;
            bestScheduleId = sched.id || null;
          }
        }
      }

      await toggleMedicationLog(medicationId, bestScheduleId, bestTime);
    } else {
      await toggleMedicationLog(medicationId, null, null);
    }
  }

  async function handleTodayToggle(medId: string, scheduleId: string, time: string) {
    await toggleMedicationLog(medId, scheduleId, time);
  }
</script>

<PageHeader
  title="Medications"
  subtitle="Track your medications, doses, and inventory"
  icon="pill"
  iconColor="#4f46e5"
>
  {#snippet actions()}
    <div class="flex h-full items-stretch">
      <button
        type="button"
        class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white hover:bg-primary-600"
        onclick={() => (formOpen = true)}
      >
        <Icon name="add" class="text-base" /><span>New Medication</span>
      </button>
    </div>
  {/snippet}
</PageHeader>

{#if loading}
  <div class="flex justify-center py-20">
    <Spinner />
  </div>
{:else}
  {#if todayItems.length > 0}
    <div class="mb-8">
      <h2 class="mb-3 text-sm font-semibold tracking-wider text-surface-400 uppercase">
        Today's Schedule
      </h2>
      <Card>
        <div class="divide-y divide-surface-100">
          {#each todayItems as item (item.scheduleId + item.time)}
            <div class="flex items-center gap-3 px-4 py-3">
              <div
                class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg text-white"
                style="background-color: {item.colorHex}"
              >
                <Icon name={item.icon} size="sm" />
              </div>

              <div class="min-w-0 flex-1">
                <div class="text-sm font-medium text-surface-800">{item.medName}</div>
                <div class="text-xs text-surface-400">{item.dosage} · {item.time}</div>
              </div>

              <button
                onclick={() => handleTodayToggle(item.medId, item.scheduleId, item.time)}
                disabled={item.taken}
                class="rounded-full px-3 py-1 text-xs font-medium transition-colors"
                class:bg-success-50={item.taken}
                class:text-success-600={item.taken}
                class:bg-surface-100={!item.taken}
                class:text-surface-500={!item.taken}
                class:hover:bg-surface-200={!item.taken}
              >
                {item.taken ? '✓ Taken' : 'Take'}
              </button>
            </div>
          {/each}
        </div>
      </Card>
    </div>
  {/if}

  <h2 class="mb-3 text-sm font-semibold tracking-wider text-surface-400 uppercase">
    My Medications
  </h2>
  <MedicationGrid
    {medications}
    {nextDoses}
    {adherenceRates}
    onToggle={handleToggle}
    onCreate={() => (formOpen = true)}
  />
{/if}

<MedicationForm
  open={formOpen}
  medication={null}
  onSave={handleSave}
  onClose={() => (formOpen = false)}
/>
