<script lang="ts">
  import type { MoodEntry } from '$lib/db/types';
  import { todayString } from '$lib/utils/datetime';
  import Icon from '$components/ui/Icon.svelte';
  import { theme } from '$stores/theme.svelte';
  import { moodColorClass } from '$lib/theme/scales';

  interface Props {
    entries: MoodEntry[];
    onSelectDate: (date: string) => void;
  }

  let { entries, onSelectDate }: Props = $props();

  let currentDate = $state(new Date());

  const moodMap = $derived(new Map(entries.map((e) => [e.entry_date, e.mood_score])));

  const year = $derived(currentDate.getFullYear());
  const month = $derived(currentDate.getMonth());

  const firstDay = $derived(new Date(year, month, 1));
  const startOffset = $derived((firstDay.getDay() + 6) % 7);

  const daysInMonth = $derived(new Date(year, month + 1, 0).getDate());

  const monthLabel = $derived(
    currentDate.toLocaleString('en-US', { month: 'long', year: 'numeric' })
  );

  function prevMonth() {
    currentDate = new Date(year, month - 1, 1);
  }

  function nextMonth() {
    currentDate = new Date(year, month + 1, 1);
  }

  function dateStr(d: number) {
    const m = String(month + 1).padStart(2, '0');
    const day = String(d).padStart(2, '0');
    return `${year}-${m}-${day}`;
  }

  function moodColor(score: number): string {
    return moodColorClass(score, theme.colorblind);
  }

  const todayStr = $derived(todayString());
</script>

<div class="space-y-3">
  <div class="flex items-center justify-between">
    <button
      type="button"
      class="rounded-lg p-1.5 text-surface-500 hover:bg-surface-100 hover:text-surface-700"
      onclick={prevMonth}
    >
      <Icon name="chevron-left" size="lg" class="text-surface-500" />
    </button>
    <span class="text-sm font-semibold text-surface-800">{monthLabel}</span>
    <button
      type="button"
      class="rounded-lg p-1.5 text-surface-500 hover:bg-surface-100 hover:text-surface-700"
      onclick={nextMonth}
    >
      <Icon name="chevron-right" size="lg" class="text-surface-500" />
    </button>
  </div>

  <div class="grid grid-cols-7 gap-1 text-center">
    {#each ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'] as day}
      <span class="text-[10px] font-medium text-surface-400">{day}</span>
    {/each}

    {#each Array(startOffset) as _}
      <div></div>
    {/each}

    {#each Array(daysInMonth) as _, i}
      {@const day = i + 1}
      {@const ds = dateStr(day)}
      {@const scoreVal = moodMap.get(ds)}
      <button
        type="button"
        class="duration-micro flex h-9 items-center justify-center rounded-lg text-xs font-medium transition-all hover:ring-2 hover:ring-primary-300 {scoreVal
          ? moodColor(scoreVal) + ' text-white'
          : 'bg-surface-100 text-surface-600'} {ds === todayStr ? 'ring-2 ring-primary-500' : ''}"
        style={scoreVal ? `opacity: ${0.3 + scoreVal * 0.07}` : ''}
        onclick={() => onSelectDate(ds)}
      >
        {day}
      </button>
    {/each}
  </div>
</div>
