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

<div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-card">
  <div class="mb-1 flex items-start justify-between gap-3">
    <div class="flex min-w-0 items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
        style="background-color: color-mix(in srgb, var(--color-success) 12%, transparent); color: var(--color-success);"
      >
        <Icon name="check" size="md" />
      </div>
      <div class="min-w-0">
        <h3 class="truncate text-sm font-extrabold tracking-tight text-text-main">
          Tägliche Gewohnheiten (Habits)
        </h3>
        <p class="truncate text-xs text-text-muted">Routinen &amp; Check-ins</p>
      </div>
    </div>
    {#if habits.length > 0}
      <Badge variant="success" class="text-[0.625rem] font-bold">
        {doneCount} von {habits.length} erledigt
      </Badge>
    {/if}
  </div>

  {#if habits.length === 0}
    <div class="py-6 text-center text-xs text-text-muted italic">
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
            : 'border-border-subtle bg-surface-50 hover:border-border-strong'}"
        >
          <span
            class="text-xs font-bold {habit.completed
              ? 'text-emerald-700 dark:text-emerald-300'
              : 'text-text-main'}"
          >
            {habit.title}
          </span>
          <div
            class="flex h-6 w-6 shrink-0 items-center justify-center rounded-xl border transition-all {habit.completed
              ? 'border-emerald-500 bg-emerald-500 text-white'
              : 'border-border-strong bg-surface-0'}"
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
