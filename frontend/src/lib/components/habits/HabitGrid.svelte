<script lang="ts">
  import HabitCard from './HabitCard.svelte';
  import type { Habit } from '$lib/db/types';

  interface Props {
    habits: Habit[];
    stats: Record<
      string,
      { currentStreak: number; longestStreak: number; todayCompleted: boolean }
    >;
    onToggle: (habitId: string) => Promise<void>;
    onCreate: () => void;
  }

  let { habits, stats, onToggle, onCreate }: Props = $props();
</script>

{#if habits.length === 0}
  <div class="flex flex-col items-center justify-center gap-3 py-16 text-center">
    <div class="rounded-full bg-surface-100 p-4 text-surface-400">
      <span class="material-symbols-outlined text-3xl">check-circle</span>
    </div>
    <h3 class="text-lg font-semibold text-surface-900">No habits yet</h3>
    <p class="max-w-xs text-sm text-surface-500">
      Create your first habit to start building streaks.
    </p>
    <button
      type="button"
      class="rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600"
      onclick={onCreate}
    >
      Create Habit
    </button>
  </div>
{:else}
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
    {#each habits as habit (habit.id)}
      {@const s = stats[habit.id] ?? { currentStreak: 0, longestStreak: 0, todayCompleted: false }}
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
