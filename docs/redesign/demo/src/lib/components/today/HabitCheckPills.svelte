<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  interface Habit {
    id: string;
    title: string;
    streak: number;
    completed: boolean;
  }

  let habits = $state<Habit[]>([
    { id: '1', title: '3L Wasser trinken', streak: 42, completed: true },
    { id: '2', title: '10.000 Schritte gehen', streak: 18, completed: true },
    { id: '3', title: '10 Min Morgenlicht vor 09:00', streak: 12, completed: true },
    { id: '4', title: 'Kein Koffein nach 14:30 Uhr', streak: 6, completed: false }
  ]);

  function toggleHabit(index: number) {
    habits[index].completed = !habits[index].completed;
    if (navigator.vibrate) navigator.vibrate(25);
  }
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-[18px] shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="check" class="text-[var(--color-success)]" />
      <span>Tägliche Gewohnheiten (Habits)</span>
    </div>
    <Badge variant="success">3 von 4 erledigt (75%)</Badge>
  </div>

  <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
    {#each habits as habit, i}
      <button
        type="button"
        onclick={() => toggleHabit(i)}
        class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex items-center justify-between cursor-pointer transition-all hover:bg-[var(--bg-surface-100)] {habit.completed ? 'border-[var(--color-success)]/40 bg-[var(--color-success-soft)]/20' : ''}"
      >
        <div class="flex items-center gap-2.5">
          <div
            class="w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all {habit.completed ? 'bg-[var(--color-success)] border-[var(--color-success)] text-white' : 'border-[var(--border-strong)]'}"
          >
            {#if habit.completed}
              <Icon name="check" size={12} />
            {/if}
          </div>
          <span class="text-xs font-semibold text-[var(--text-main)] {habit.completed ? 'line-through text-[var(--text-muted)]' : ''}">
            {habit.title}
          </span>
        </div>
        <span class="text-[0.6875rem] font-mono font-bold text-[var(--color-circadian)]">
          {habit.streak}T
        </span>
      </button>
    {/each}
  </div>
</div>
