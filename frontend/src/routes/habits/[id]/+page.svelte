<script lang="ts">
  import { liveQuery } from 'dexie';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import type { Habit, HabitLog } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import ProgressBar from '$components/ui/ProgressBar.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import CheckCircle from '$components/ui/CheckCircle.svelte';
  import HabitForm from '$components/habits/HabitForm.svelte';
  import { updateHabit, deleteHabit, toggleHabit } from '$lib/mutations/wellness';

  let id = $derived(page.params.id);
  let loading = $state(true);
  let habit = $state<Habit | null>(null);
  let logs = $state<HabitLog[]>([]);
  let editOpen = $state(false);
  let deleteOpen = $state(false);

  const dayNames = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];

  function computeFreqLabel(h: Habit): string {
    switch (h.frequency) {
      case 'daily': return 'Daily';
      case 'weekly_n': return `${h.target_count}×/week`;
      case 'custom_days': {
        if (h.days_bitmask == null) return '';
        const active = dayNames.filter((_, i) => (h.days_bitmask! >> i) & 1);
        return active.join(', ');
      }
      default: return '';
    }
  }

  const freqLabel = $derived(habit ? computeFreqLabel(habit) : '');

  const todayStr = new Date().toISOString().split('T')[0];
  const todayCompleted = $derived(
    logs.some((l) => l.log_date === todayStr && l.completed)
  );

  const completedLogs = $derived(logs.filter((l) => l.completed));
  const completedDates = $derived([...new Set(completedLogs.map((l) => l.log_date))].sort().reverse());

  const currentStreak = $derived.by(() => {
    let streak = 0;
    let expected = todayStr;
    for (const d of completedDates) {
      if (d === expected) {
        streak++;
        const dt = new Date(d);
        dt.setDate(dt.getDate() - 1);
        expected = dt.toISOString().split('T')[0];
      } else if (d < expected) break;
    }
    return streak;
  });

  const totalCompletions = $derived(completedLogs.length);

  const weekDays = 7;
  const weekCount = 12;

  const calendarCells = $derived.by(() => {
    const today = new Date();
    const dayOfWeek = (today.getDay() + 6) % 7;
    const endDate = new Date(today);
    endDate.setDate(endDate.getDate() - dayOfWeek + 6);
    const startDate = new Date(endDate);
    startDate.setDate(startDate.getDate() - weekCount * weekDays + 1);

    const dateSet = new Set(completedDates);
    const cells: { date: string; completed: boolean; today: boolean }[] = [];

    const d = new Date(startDate);
    while (d <= endDate) {
      const ds = d.toISOString().split('T')[0];
      cells.push({ date: ds, completed: dateSet.has(ds), today: ds === todayStr });
      d.setDate(d.getDate() + 1);
    }
    return cells;
  });

  const weeklyCompletionRate = $derived.by(() => {
    if (!habit || habit.frequency !== 'daily') return null;
    const totalDays = Math.min(weekDays * 4, calendarCells.length);
    if (totalDays === 0) return null;
    const completedInRange = calendarCells.filter((c) => c.completed).length;
    return Math.round((completedInRange / totalDays) * 100);
  });

  $effect(() => {
    if (!id) return;
    const sub1 = liveQuery(() =>
      db.habit.get(id).then((h) => (h && !h.deleted_at ? h : null))
    ).subscribe((v) => {
      habit = v;
    });
    const sub2 = liveQuery(() =>
      db.habit_log.where({ habit_id: id }).filter((l) => !l.deleted_at).toArray()
    ).subscribe((v) => {
      logs = v;
      loading = false;
    });
    return () => {
      sub1.unsubscribe();
      sub2.unsubscribe();
    };
  });

  async function handleToggle() {
    if (!id) return;
    await toggleHabit(id);
  }

  async function handleSave(data: {
    name: string;
    description: string;
    color: string;
    icon: string;
    frequency: string;
    target_count: number;
    days_bitmask?: number | null;
    stack_hint: string;
  }) {
    if (!id) return;
    await updateHabit(id, data);
    editOpen = false;
  }

  async function handleDelete() {
    if (!id) return;
    await deleteHabit(id);
    goto('/habits');
  }
</script>

<svelte:head><title>Salus — {habit?.name ?? 'Habit'}</title></svelte:head>

<div class="space-y-6">
  {#if loading}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if !habit}
    <EmptyState icon="check-circle" title="Habit not found" description="This habit may have been deleted." />
  {:else}
    <PageHeader
      title={habit.name}
      subtitle={freqLabel}
      backUrl="/habits"
      icon={habit.icon}
      iconColor="#fff"
      iconBgColor={habit.color}
    >
      {#snippet stats()}
        <div class="grid gap-6 px-6 py-6 sm:grid-cols-3">
          <Stat value={currentStreak} unit="days" label="Current Streak" />
          <Stat value={totalCompletions} unit="times" label="Total" />
          {#if weeklyCompletionRate != null}
            <div class="flex flex-col items-start gap-3">
              <ProgressBar
                value={weeklyCompletionRate}
                max={100}
                variant="info"
                height="md"
                label={`${weeklyCompletionRate}% completion`}
                class="w-full"
              />
            </div>
          {/if}
        </div>
      {/snippet}
      {#snippet actions()}
        <div class="flex h-full items-stretch gap-2">
          <Btn variant="secondary" size="sm" onclick={() => (editOpen = true)}>
            <Icon name="edit" size="sm" />Edit
          </Btn>
          <Btn
            variant="secondary"
            size="sm"
            class="!text-error-600 hover:!bg-error-50"
            onclick={() => (deleteOpen = true)}
          >
            <Icon name="delete" size="sm" />Delete
          </Btn>
        </div>
      {/snippet}
    </PageHeader>

    <div class="grid gap-6 lg:grid-cols-12">
      <Card padding={false} class="lg:col-span-8">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="checklist" size="sm" class="text-surface-500" />
            <span class="text-sm font-semibold text-surface-700">Completion History</span>
          </div>
        {/snippet}
        <div class="p-4">
          {#if calendarCells.length === 0}
            <div class="flex justify-center py-8 text-xs text-surface-400">No data yet.</div>
          {:else}
            <div class="inline-grid grid-flow-col gap-1" style="grid-template-rows: repeat(7, 1fr);">
              {#each calendarCells as cell}
                <div
                  class="h-3 w-3 rounded-sm {cell.completed
                    ? 'bg-primary-500'
                    : 'bg-surface-100'} {cell.today ? 'ring-1 ring-inset ring-primary-300' : ''}"
                  title={cell.date}
                ></div>
              {/each}
            </div>
            <div class="mt-3 flex items-center justify-between text-[10px] text-surface-400">
              <span>{calendarCells[0]?.date ?? ''}</span>
              <span>today</span>
              <span>{calendarCells[calendarCells.length - 1]?.date ?? ''}</span>
            </div>
          {/if}
        </div>
      </Card>

      <div class="space-y-4 lg:col-span-4">
        <Card>
          <div class="flex items-center gap-2">
            <CheckCircle checked={todayCompleted} onchange={handleToggle} />
            <span class="text-sm font-medium text-surface-700">
              {todayCompleted ? 'Done today' : 'Mark today as done'}
            </span>
          </div>
        </Card>

        {#if habit.description}
          <Card>
            <p class="text-sm text-surface-600">{habit.description}</p>
          </Card>
        {/if}

        <Card>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-surface-500">Frequency</span>
              <Badge variant="default">{freqLabel}</Badge>
            </div>
            {#if habit.stack_hint}
              <div class="flex items-center justify-between text-sm">
                <span class="text-surface-500">Stack hint</span>
                <span class="text-surface-700">{habit.stack_hint}</span>
              </div>
            {/if}
            <div class="flex items-center justify-between text-sm">
              <span class="text-surface-500">Color</span>
              <div class="h-4 w-4 rounded" style="background-color: {habit.color}"></div>
            </div>
          </div>
        </Card>
      </div>

      <Card padding={false} class="lg:col-span-full">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="history" size="sm" class="text-surface-500" />
            <span class="text-sm font-semibold text-surface-700">Recent Logs</span>
          </div>
        {/snippet}
        <div class="divide-y divide-surface-100">
          {#if logs.length === 0}
            <div class="px-6 py-8 text-center text-sm text-surface-400">No logs yet.</div>
          {:else}
            {#each logs.filter((l) => l.completed).slice(0, 20) as log}
              <div class="flex items-center justify-between px-6 py-2.5">
                <span class="text-sm text-surface-700">{log.log_date}</span>
                <span class="text-xs text-surface-400">
                  {new Date(log.completed_at ?? log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            {/each}
          {/if}
        </div>
      </Card>
    </div>
  {/if}
</div>

<HabitForm
  open={editOpen}
  habit={habit
    ? {
        name: habit.name,
        description: habit.description ?? '',
        color: habit.color,
        icon: habit.icon,
        frequency: habit.frequency,
        target_count: habit.target_count,
        days_bitmask: habit.days_bitmask,
        stack_hint: habit.stack_hint ?? ''
      }
    : null}
  onSave={handleSave}
  onClose={() => (editOpen = false)}
/>

<ConfirmDialog
  bind:open={deleteOpen}
  title="Delete Habit"
  variant="danger"
  message="Are you sure you want to delete this habit and all its logs?"
  confirmLabel="Delete"
  onconfirm={handleDelete}
/>
