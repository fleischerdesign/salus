<script lang="ts">
  import { type Snippet } from 'svelte';
  import { todayString } from '$lib/utils/datetime';
  import Icon from './Icon.svelte';
  import Btn from './Btn.svelte';

  interface Props {
    dateDisplay: string;
    onPrev: () => void;
    onNext: () => void;
    onDateChange?: (date: string) => void;
    isToday: boolean;
    children?: Snippet;
    class?: string;
  }

  let {
    dateDisplay,
    onPrev,
    onNext,
    onDateChange,
    isToday,
    children,
    class: extraClass = ''
  }: Props = $props();

  let dateInput = $state<HTMLInputElement | null>(null);

  function handleDateInput(e: Event) {
    const input = e.target as HTMLInputElement;
    onDateChange?.(input.value);
  }
</script>

<div
  class="flex items-center gap-2 rounded-lg bg-surface-100 px-3 py-2 {extraClass}"
  role="navigation"
  aria-label="Date navigation"
>
  <button
    class="duration-micro hover:bg-primary-50 hover:text-primary-600 flex h-9 w-9 items-center justify-center rounded-full text-surface-600 transition-colors"
    onclick={onPrev}
    aria-label="Previous day"
    type="button"
  >
    <Icon name="chevron-left" />
  </button>

  <span
    class="duration-micro tracking-label hover:text-primary-600 cursor-pointer text-xs font-semibold text-surface-900 transition-colors"
    role="button"
    tabindex="0"
    onclick={() => {
      dateInput?.showPicker();
    }}
    onkeydown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        dateInput?.showPicker();
      }
    }}
  >
    {dateDisplay}
  </span>
  <input bind:this={dateInput} type="date" class="sr-only" onchange={handleDateInput} />

  <button
    class="duration-micro hover:bg-primary-50 hover:text-primary-600 flex h-9 w-9 items-center justify-center rounded-full text-surface-600 transition-colors"
    onclick={onNext}
    aria-label="Next day"
    type="button"
  >
    <Icon name="chevron-right" />
  </button>

  {#if !isToday}
    <Btn variant="secondary" size="sm" onclick={() => onDateChange?.(todayString())}>Today</Btn>
  {/if}

  {@render children?.()}
</div>
