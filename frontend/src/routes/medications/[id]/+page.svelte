<script lang="ts">
  import { liveQuery } from 'dexie';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import type {
    Medication,
    MedicationLog,
    MedicationSchedule,
    MedicationInventory
  } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import MedicationForm from '$components/medications/MedicationForm.svelte';
  import ScheduleEditor from '$components/medications/ScheduleEditor.svelte';
  import InventoryTracker from '$components/medications/InventoryTracker.svelte';
  import {
    updateMedication,
    deleteMedication,
    toggleMedicationLog,
    createSchedule as createScheduleMut,
    deleteSchedule,
    updateInventory,
    skipDose
  } from '$lib/mutations/medication';

  let id = $derived(page.params.id);

  let loading = $state(true);
  let medication = $state<Medication | null>(null);
  let schedules = $state<MedicationSchedule[]>([]);
  let logs = $state<MedicationLog[]>([]);
  let inventory = $state<MedicationInventory | null>(null);
  let editOpen = $state(false);
  let deleteOpen = $state(false);
  let saving = $state(false);

  $effect(() => {
    if (!id) return;
    const sub1 = liveQuery(() =>
      db.medication.get(id).then((m) => (m && !m.deleted_at ? m : null))
    ).subscribe((v) => {
      medication = v;
    });
    const sub2 = liveQuery(() =>
      db.medication_schedule
        .where({ medication_id: id })
        .filter((s) => !s.deleted_at)
        .toArray()
    ).subscribe((v) => {
      schedules = v;
    });
    const sub3 = liveQuery(() =>
      db.medication_log
        .where({ medication_id: id })
        .filter((l) => !l.deleted_at)
        .toArray()
    ).subscribe((v) => {
      logs = v;
    });
    const sub4 = liveQuery(() =>
      db.medication_inventory
        .where({ medication_id: id })
        .filter((i) => !i.deleted_at)
        .first()
    ).subscribe((v) => {
      inventory = v ?? null;
      loading = false;
    });
    return () => {
      sub1.unsubscribe();
      sub2.unsubscribe();
      sub3.unsubscribe();
      sub4.unsubscribe();
    };
  });

  const today = $derived(new Date().toISOString().split('T')[0]);
  const todayWeekday = $derived(new Date().getDay() || 7);
  const totalTaken = $derived(logs.filter((l) => !l.skipped).length);
  const totalSkipped = $derived(logs.filter((l) => l.skipped).length);
  const adherenceRate = $derived(
    logs.length > 0 ? Math.round((totalTaken / logs.length) * 100) : 0
  );

  const recentLogs = $derived(logs.slice(0, 14));

  async function handleSave(data: Record<string, string>) {
    if (!id) return;
    saving = true;
    try {
      await updateMedication(id, data);
      editOpen = false;
    } finally {
      saving = false;
    }
  }

  async function handleDelete() {
    if (!id) return;
    await deleteMedication(id);
    goto('/medications');
  }

  async function handleToggle(scheduleId: string | null, time: string | null) {
    if (!id) return;
    await toggleMedicationLog(id, scheduleId, time);
  }

  async function handleCreateSchedule(data: {
    dosage: string;
    times: string[];
    days_of_week: number[] | null;
    start_date: string;
    end_date: string;
  }) {
    if (!id) return;
    await createScheduleMut(id, data);
  }

  async function handleDeleteSchedule(scheduleId: string) {
    await deleteSchedule(scheduleId);
  }

  async function handleUpdateInventory(data: {
    initial_count: number;
    remaining_count: number;
    refill_at_count: number;
  }) {
    if (!id) return;
    await updateInventory(id, data);
  }

  async function handleSkip(scheduleId: string, time: string) {
    if (!id) return;
    await skipDose(id, scheduleId, time);
  }

  const todayScheduleItems = $derived.by(() => {
    const items: {
      schedule: MedicationSchedule;
      time: string;
      taken: boolean;
      skipped: boolean;
    }[] = [];
    for (const sched of schedules) {
      if (sched.days_of_week && !sched.days_of_week.includes(todayWeekday)) continue;
      if (sched.start_date && today < sched.start_date) continue;
      if (sched.end_date && today > sched.end_date) continue;

      for (const t of sched.times) {
        const match = logs.find(
          (l) => l.schedule_id === sched.id && !l.deleted_at && l.taken_at?.startsWith(today)
        );
        items.push({
          schedule: sched,
          time: t,
          taken: match != null && !match.skipped,
          skipped: match != null && match.skipped
        });
      }
    }
    items.sort((a, b) => a.time.localeCompare(b.time));
    return items;
  });
</script>

{#if loading}
  <div class="flex justify-center py-20">
    <Spinner />
  </div>
{:else if !medication}
  <EmptyState
    icon="pill"
    title="Medication not found"
    description="This medication may have been deleted."
  />
{:else}
  <PageHeader
    title={medication.name}
    subtitle={medication.strength ? `${medication.strength} · ${medication.form}` : medication.form}
    icon={medication.icon}
    iconColor={medication.color_hex}
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch gap-2">
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 bg-surface-100 px-6 text-sm font-semibold whitespace-nowrap text-surface-700 hover:bg-surface-200"
          onclick={() => (editOpen = true)}
        >
          <Icon name="edit" class="text-base" /><span>Edit</span>
        </button>
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 bg-error-500 px-6 text-sm font-semibold whitespace-nowrap text-white hover:bg-error-600"
          onclick={() => (deleteOpen = true)}
        >
          <Icon name="delete" class="text-base" /><span>Delete</span>
        </button>
      </div>
    {/snippet}
  </PageHeader>

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
    <div class="flex flex-col gap-6 lg:col-span-2">
      <!-- Info Card -->
      <Card>
        <h3 class="mb-4 text-sm font-semibold text-surface-700">Details</h3>
        <div class="grid grid-cols-2 gap-4 text-sm">
          {#if medication.active_ingredient}
            <div>
              <span class="text-surface-400">Active Ingredient</span>
              <div class="font-medium text-surface-700">{medication.active_ingredient}</div>
            </div>
          {/if}
          {#if medication.strength}
            <div>
              <span class="text-surface-400">Strength</span>
              <div class="font-medium text-surface-700">{medication.strength}</div>
            </div>
          {/if}
          <div>
            <span class="text-surface-400">Form</span>
            <div class="font-medium text-surface-700">
              {medication.form.charAt(0).toUpperCase() + medication.form.slice(1)}
            </div>
          </div>
          {#if medication.instructions}
            <div class="col-span-2">
              <span class="text-surface-400">Instructions</span>
              <div class="font-medium text-surface-700">{medication.instructions}</div>
            </div>
          {/if}
        </div>
      </Card>

      <!-- Today's Schedule -->
      {#if todayScheduleItems.length > 0}
        <Card>
          <h3 class="mb-4 text-sm font-semibold text-surface-700">Today's Doses</h3>
          <div class="divide-y divide-surface-100">
            {#each todayScheduleItems as item (item.schedule.id + item.time)}
              <div class="flex items-center gap-3 py-3 first:pt-0 last:pb-0">
                <span class="w-12 font-mono text-sm font-medium text-surface-600">{item.time}</span>
                <span class="flex-1 text-sm text-surface-500">{item.schedule.dosage}</span>
                {#if item.taken}
                  <Badge variant="success">Taken</Badge>
                {:else if item.skipped}
                  <Badge variant="error">Skipped</Badge>
                {:else}
                  <div class="flex gap-1">
                    <Btn
                      variant="primary"
                      size="sm"
                      onclick={() => handleToggle(item.schedule.id || null, item.time)}
                    >
                      Take
                    </Btn>
                    <Btn
                      variant="ghost"
                      size="sm"
                      onclick={() => handleSkip(item.schedule.id || '', item.time)}
                    >
                      Skip
                    </Btn>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </Card>
      {:else if medication.is_active}
        <Card>
          <div class="py-4 text-center text-surface-400">
            <Icon name="event_busy" size="lg" />
            <p class="mt-2">No doses scheduled for today</p>
          </div>
        </Card>
      {/if}

      <!-- Schedule Management -->
      <Card>
        <h3 class="mb-4 text-sm font-semibold text-surface-700">Schedules</h3>
        {#if schedules.length > 0}
          <div class="flex flex-col gap-3">
            {#each schedules as sched (sched.id)}
              <div
                class="flex items-start justify-between rounded-lg border border-surface-200 p-3"
              >
                <div>
                  <div class="text-sm font-medium text-surface-700">{sched.dosage}</div>
                  <div class="mt-1 text-xs text-surface-400">
                    {sched.times.join(', ')}
                    {#if sched.days_of_week}
                      · {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                        .filter((_, i) => sched.days_of_week!.includes(i + 1))
                        .join(', ')}
                    {:else}
                      · Every day
                    {/if}
                  </div>
                </div>
                <button
                  onclick={() => handleDeleteSchedule(sched.id || '')}
                  class="text-surface-400 hover:text-error-500"
                >
                  <Icon name="delete" size="sm" />
                </button>
              </div>
            {/each}
          </div>
        {:else}
          <p class="py-4 text-center text-sm text-surface-400">
            No schedules yet. Add one below or use as-needed.
          </p>
        {/if}

        <div class="mt-4">
          <ScheduleEditor
            times={[]}
            dosage={''}
            startDate={''}
            endDate={''}
            daysOfWeek={null}
            onSave={handleCreateSchedule}
          />
        </div>
      </Card>

      <!-- Recent Logs -->
      <Card>
        <h3 class="mb-4 text-sm font-semibold text-surface-700">Recent Logs</h3>
        {#if recentLogs.length > 0}
          <div class="divide-y divide-surface-100">
            {#each recentLogs as log (log.id)}
              <div class="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
                <Badge variant={log.skipped ? 'error' : 'success'}>
                  {log.skipped ? 'Skipped' : 'Taken'}
                </Badge>
                <span class="flex-1 text-sm text-surface-500">
                  {log.dosage_taken || '-'}
                </span>
                <span class="text-xs text-surface-400">
                  {log.taken_at ? new Date(log.taken_at).toLocaleString() : ''}
                </span>
              </div>
            {/each}
          </div>
        {:else}
          <p class="py-4 text-center text-sm text-surface-400">No logs recorded yet.</p>
        {/if}
      </Card>
    </div>

    <!-- Sidebar -->
    <div class="flex flex-col gap-6">
      <div class="grid grid-cols-2 gap-4">
        <Stat label="Adherence" value="{adherenceRate}%" />
        <Stat label="Taken" value={totalTaken} />
        <Stat label="Skipped" value={totalSkipped} />
        <Stat label="Total Logs" value={logs.length} />
      </div>

      <InventoryTracker {inventory} onUpdate={handleUpdateInventory} />

      {#if medication.is_active}
        <Btn variant="primary" onclick={() => handleToggle(null, null)}>
          <Icon name={medication.icon} size="sm" /> Log As-Needed Dose
        </Btn>
      {/if}
    </div>
  </div>

  <MedicationForm
    open={editOpen}
    medication={{
      name: medication.name,
      active_ingredient: medication.active_ingredient ?? '',
      strength: medication.strength ?? '',
      form: medication.form,
      instructions: medication.instructions ?? '',
      color_hex: medication.color_hex,
      icon: medication.icon
    }}
    onSave={handleSave}
    onClose={() => (editOpen = false)}
    {saving}
  />

  <ConfirmDialog
    bind:open={deleteOpen}
    title="Delete Medication"
    variant="danger"
    message="Are you sure you want to delete this medication and all its schedules, logs, and inventory?"
    confirmLabel="Delete"
    onconfirm={handleDelete}
  />
{/if}
