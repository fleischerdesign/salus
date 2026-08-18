<script lang="ts">
  import HabitCard from './HabitCard.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import type { Habit } from '$lib/db/types';

  interface Props {
    habits: Habit[];
    stats: Record<string, { currentStreak: number; todayCompleted: boolean }>;
    onToggle: (habitId: string) => Promise<void>;
    onCreate: () => void;
  }

  let { habits, stats, onToggle, onCreate }: Props = $props();
</script>

{#if habits.length === 0}
  <div class="flex flex-col items-center justify-center gap-3 py-16 text-center">
    <div class="bg-surface-100 text-surface-400 rounded-full p-4">
      <Icon name="check-circle" size="2xl" class="text-surface-400" />
    </div>
    <h3 class="text-surface-900 text-lg font-semibold">No habits yet</h3>
    <p class="text-surface-500 max-w-xs text-sm">
      Create your first habit to start building streaks.
    </p>
    <button
      type="button"
      class="bg-primary-500 text-on-primary hover:bg-primary-600 rounded-lg px-4 py-2 text-sm font-semibold"
      onclick={onCreate}
    >
      Create Habit
    </button>
  </div>
{:else}
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
    {#each habits as habit (habit.id)}
      {@const s = stats[habit.id] ?? { currentStreak: 0, todayCompleted: false }}
      <HabitCard
        {habit}
        streak={s.currentStreak}
        todayCompleted={s.todayCompleted}
        completionRate={0}
        onToggle={() => onToggle(habit.id)}
      />
    {/each}
  </div>
{/if}
