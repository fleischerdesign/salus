<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import type { Habit } from '$lib/db/types';

  interface Props {
    habit: Habit;
    streak: number;
    todayCompleted: boolean;
    completionRate: number;
    onToggle: () => void;
  }

  let { habit, streak, todayCompleted, completionRate, onToggle }: Props = $props();

  let toggling = $state(false);

  async function handleToggle() {
    toggling = true;
    try {
      await onToggle();
    } finally {
      toggling = false;
    }
  }
</script>

<button
  type="button"
  class="group relative flex w-full items-center gap-4 rounded-xl border border-surface-200 bg-surface-0 p-4 text-left transition-all hover:border-surface-300 hover:shadow-sm"
  onclick={handleToggle}
  disabled={toggling}
>
  <div
    class="duration-micro flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-white transition-transform"
    style="background-color: {habit.color}"
    class:scale-90={toggling}
  >
    <Icon name={habit.icon} size="md" />
  </div>

  <div class="min-w-0 flex-1">
    <div class="font-semibold text-surface-900">{habit.name}</div>
    {#if habit.description}
      <div class="truncate text-xs text-surface-500">{habit.description}</div>
    {/if}
  </div>

  <div class="flex flex-shrink-0 items-center gap-3">
    {#if streak > 0}
      <div class="flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1">
        <span class="text-sm">{streak}</span>
        <span class="text-[10px]">🔥</span>
      </div>
    {/if}

    <div
      class="duration-micro flex h-7 w-7 items-center justify-center rounded-full border-2 transition-all"
      class:border-primary-500={todayCompleted}
      class:bg-primary-500={todayCompleted}
      class:border-surface-300={!todayCompleted}
      class:group-hover:border-primary-400={!todayCompleted}
    >
      {#if todayCompleted}
        <Icon name="check" size="sm" class="text-white" />
      {/if}
    </div>
  </div>
</button>
