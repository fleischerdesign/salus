<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Card from '$components/ui/Card.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import CheckCircle from '$components/ui/CheckCircle.svelte';
  import { goto } from '$app/navigation';
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
  let feedback = $state<'idle' | 'done' | 'undone'>('idle');

  const dayNames = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];

  const freqLabel = $derived.by(() => {
    switch (habit.frequency) {
      case 'daily':
        return 'Daily';
      case 'weekly_n':
        return `${habit.target_count}×/week`;
      case 'custom_days': {
        if (habit.days_bitmask == null) return '';
        const active = dayNames.filter((_, i) => (habit.days_bitmask! >> i) & 1);
        return active.join(', ');
      }
      default:
        return '';
    }
  });

  async function handleToggle(checked: boolean) {
    toggling = true;
    const wasCompleted = todayCompleted;
    try {
      await onToggle();
      feedback = wasCompleted ? 'undone' : 'done';
      setTimeout(() => (feedback = 'idle'), 800);
    } finally {
      toggling = false;
    }
  }
  function navigateToDetail() {
    goto('/habits/' + habit.id);
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="group block cursor-pointer"
  onclick={navigateToDetail}
  onkeydown={(e) => {
    if (e.key === 'Enter') navigateToDetail();
  }}
  role="link"
  tabindex="0"
>
  <Card hoverable padding={false}>
    <div class="p-4 pb-2">
      <div class="flex items-start gap-3">
        <div
          class="duration-micro flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-white transition-all"
          style="background-color: {habit.color}"
          class:scale-90={toggling}
          class:bg-success-500={feedback === 'done'}
          class:bg-error-500={feedback === 'undone'}
        >
          <Icon name={habit.icon} size="md" />
        </div>

        <div class="min-w-0 flex-1 pt-0.5">
          <div class="font-semibold text-surface-900">{habit.name}</div>
          {#if habit.description}
            <div class="truncate text-xs text-surface-500">{habit.description}</div>
          {/if}
        </div>

        {#if freqLabel}
          <Badge variant="default" class="mt-0.5 flex-shrink-0 text-[10px]">{freqLabel}</Badge>
        {/if}
      </div>
    </div>

    <div class="border-t border-surface-100"></div>

    <div class="flex items-center justify-between px-4 py-2.5">
      <div class="flex items-center gap-1.5 text-xs text-surface-500">
        {#if streak > 0}
          <span class="text-amber-500">🔥</span>
          <span class="font-medium text-surface-600">{streak}-day streak</span>
        {:else}
          <span class="text-surface-400">No streak yet</span>
        {/if}
      </div>

      <CheckCircle checked={todayCompleted} disabled={toggling} onchange={handleToggle} />
    </div>
  </Card>
</div>
