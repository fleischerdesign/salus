<script lang="ts">
  import { db } from '$lib/db/database';
  import { todayString, dateString } from '$lib/utils/datetime';
  import type { Habit } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import HabitGrid from '$components/habits/HabitGrid.svelte';
  import HabitForm from '$components/habits/HabitForm.svelte';
  import { toggleHabit, createHabit as createHabitMut } from '$lib/mutations/wellness';
  import Icon from '$components/ui/Icon.svelte';
  import Card from '$components/ui/Card.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';

  const habitsQuery = useQuery(() => db.habit.toArray());
  const habits = $derived(habitsQuery.value);
  const logsQuery = useQuery(() => db.habit_log.toArray());
  const logs = $derived(logsQuery.value);
  const loading = $derived(logsQuery.loading);

  let formOpen = $state(false);
  let editTarget = $state<Habit | null>(null);

  let stats = $derived(
    Object.fromEntries(
      (habits ?? []).map((h) => {
        const hLogs = (logs ?? []).filter((l) => l.habit_id === h.id && l.completed);
        const dates = [...new Set(hLogs.map((l) => l.log_date))].sort().reverse();
        const today = todayString();
        let currentStreak = 0;
        let expected = today;
        for (const d of dates) {
          if (d === expected) {
            currentStreak++;
            expected = prevDay(expected);
          } else if (d < expected) break;
        }
        return [h.id, { currentStreak, todayCompleted: dates[0] === today }];
      })
    )
  );

  function prevDay(d: string): string {
    const dt = new Date(d);
    dt.setDate(dt.getDate() - 1);
    return dateString(dt);
  }

  async function handleToggle(habitId: string) {
    const { ok, error } = await toggleHabit(habitId);
    if (!ok) console.error('Failed to toggle habit:', error);
  }

  async function handleSave(data: Parameters<typeof createHabitMut>[0]) {
    await createHabitMut(data);
    formOpen = false;
    editTarget = null;
  }

  const activeHabits = $derived((habits ?? []).filter((h) => !h.is_archived));
  const archivedHabits = $derived((habits ?? []).filter((h) => h.is_archived));
</script>

<svelte:head><title>Salus — Habits</title></svelte:head>

<div class="space-y-6">
  <PageHeader title="Habits" subtitle="Track daily habits and build streaks" icon="check-circle">
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white hover:bg-primary-600"
          onclick={() => {
            editTarget = null;
            formOpen = true;
          }}
        >
          <Icon name="add" class="text-base" /><span>New Habit</span>
        </button>
      </div>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {#each Array(3) as _}
        <div class="h-24 animate-pulse rounded-xl bg-surface-100"></div>
      {/each}
    </div>
  {:else}
    <HabitGrid
      habits={activeHabits}
      {stats}
      onToggle={handleToggle}
      onCreate={() => {
        editTarget = null;
        formOpen = true;
      }}
    />

    {#if archivedHabits.length > 0}
      <details class="mt-4">
        <summary class="cursor-pointer text-sm font-medium text-surface-500 hover:text-surface-700"
          >Archived ({archivedHabits.length})</summary
        >
        <div class="mt-2 grid grid-cols-1 gap-3 opacity-60 sm:grid-cols-2 lg:grid-cols-3">
          {#each archivedHabits as habit}
            <a href="/habits/{habit.id}" class="no-underline">
              <Card padding={false}>
                <div class="flex items-center gap-3 p-3">
                  <Icon name={habit.icon} class="text-surface-400" />
                  <span class="text-sm text-surface-500">{habit.name}</span>
                </div>
              </Card>
            </a>
          {/each}
        </div>
      </details>
    {/if}
  {/if}

  <HabitForm
    open={formOpen}
    habit={editTarget
      ? {
          name: editTarget.name,
          description: editTarget.description ?? '',
          color: editTarget.color,
          icon: editTarget.icon,
          frequency: editTarget.frequency,
          target_count: editTarget.target_count,
          days_bitmask: editTarget.days_bitmask,
          stack_hint: editTarget.stack_hint ?? ''
        }
      : null}
    onSave={handleSave}
    onClose={() => {
      formOpen = false;
      editTarget = null;
    }}
  />
</div>
