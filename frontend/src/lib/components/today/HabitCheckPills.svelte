<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { toggleHabit } from '$lib/mutations/wellness';

  interface Props {
    date?: string;
  }

  let { date = todayString() }: Props = $props();

  const habitsQuery = useQuery(
    async () => {
      const [allHabits, allLogs] = await Promise.all([
        db.habit.toArray(),
        db.habit_log.where('log_date').equals(date).toArray()
      ]);

      const activeHabits = allHabits.filter((h) => !h.deleted_at && !h.is_archived);
      const completedSet = new Set(
        allLogs.filter((l) => !l.deleted_at && l.completed).map((l) => l.habit_id)
      );

      return activeHabits.map((h) => ({
        id: h.id,
        title: h.name,
        completed: completedSet.has(h.id)
      }));
    },
    () => date
  );

  const habits = $derived(habitsQuery.value ?? []);
  const doneCount = $derived(habits.filter((h) => h.completed).length);

  async function handleToggle(habitId: string) {
    await toggleHabit(habitId, date);
  }
</script>

<div
  class="rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
>
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-2 text-sm font-extrabold text-[var(--text-main)]">
      <div
        class="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500"
      >
        <Icon name="check" size="sm" />
      </div>
      <span>Tägliche Gewohnheiten (Habits)</span>
    </div>
    {#if habits.length > 0}
      <Badge variant="success" class="text-xs font-bold"
        >{doneCount} von {habits.length} erledigt</Badge
      >
    {/if}
  </div>

  {#if habits.length === 0}
    <div class="py-6 text-center text-xs text-[var(--text-muted)] italic">
      Noch keine Gewohnheiten hinterlegt.
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
      {#each habits as habit (habit.id)}
        <button
          type="button"
          onclick={() => handleToggle(habit.id)}
          class="flex cursor-pointer items-center justify-between gap-3 rounded-2xl border p-3.5 text-left transition-all {habit.completed
            ? 'border-emerald-500/30 bg-emerald-500/10 shadow-xs'
            : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] hover:border-[var(--border-strong)]'}"
        >
          <span
            class="text-xs font-bold {habit.completed
              ? 'text-emerald-700 dark:text-emerald-300'
              : 'text-[var(--text-main)]'}"
          >
            {habit.title}
          </span>
          <div
            class="flex h-6 w-6 shrink-0 items-center justify-center rounded-xl border transition-all {habit.completed
              ? 'border-emerald-500 bg-emerald-500 text-white'
              : 'border-[var(--border-strong)] bg-[var(--bg-surface-0)]'}"
          >
            {#if habit.completed}
              <Icon name="check" size="sm" />
            {/if}
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>
