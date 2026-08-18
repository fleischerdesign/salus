<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { toggleHabit } from '$lib/mutations/wellness';

  const today = todayString();

  const habitsQuery = useQuery(
    async () => {
      const [allHabits, allLogs] = await Promise.all([
        db.habit.toArray(),
        db.habit_log.where('log_date').equals(today).toArray()
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
    () => today
  );

  const habits = $derived(habitsQuery.value ?? []);
  const doneCount = $derived(habits.filter((h) => h.completed).length);

  async function handleToggle(habitId: string) {
    await toggleHabit(habitId);
  }
</script>

<div
  class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-[18px] shadow-[var(--shadow-card)]"
>
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
      <Icon name="check" class="text-[var(--color-success)]" />
      <span>Tägliche Gewohnheiten (Habits)</span>
    </div>
    {#if habits.length > 0}
      <Badge variant="success">{doneCount} von {habits.length} erledigt</Badge>
    {/if}
  </div>

  {#if habits.length === 0}
    <div class="py-4 text-center text-xs text-[var(--text-muted)]">
      Noch keine Gewohnheiten hinterlegt.
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
      {#each habits as habit (habit.id)}
        <button
          type="button"
          onclick={() => handleToggle(habit.id)}
          class="flex cursor-pointer items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-left transition-all hover:bg-[var(--bg-surface-100)] {habit.completed
            ? 'border-emerald-500/40 bg-emerald-500/10'
            : ''}"
        >
          <div class="flex items-center gap-2.5">
            <div
              class="flex h-5 w-5 items-center justify-center rounded-full border-2 transition-all {habit.completed
                ? 'border-emerald-500 bg-emerald-500 text-white'
                : 'border-[var(--border-strong)]'}"
            >
              {#if habit.completed}
                <Icon name="check" size={12} />
              {/if}
            </div>
            <span
              class="text-xs font-semibold text-[var(--text-main)] {habit.completed
                ? 'text-[var(--text-muted)] line-through'
                : ''}"
            >
              {habit.title}
            </span>
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>
