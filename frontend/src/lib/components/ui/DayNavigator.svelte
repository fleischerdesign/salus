<script lang="ts">
  import { type Snippet } from 'svelte';
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
    class="duration-micro flex h-9 w-9 items-center justify-center rounded-full text-surface-600 transition-colors hover:bg-primary-50 hover:text-primary-600"
    onclick={onPrev}
    aria-label="Previous day"
    type="button"
  >
    <Icon name="chevron-left" />
  </button>

  <span
    class="duration-micro cursor-pointer text-[13px] font-semibold tracking-[0.05em] text-surface-900 transition-colors hover:text-primary-600"
    role="button"
    tabindex="0"
    onclick={() => {
      const input = document.getElementById('daynav-hidden-date') as HTMLInputElement;
      input?.showPicker();
    }}
    onkeydown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const input = document.getElementById('daynav-hidden-date') as HTMLInputElement;
        input?.showPicker();
      }
    }}
  >
    {dateDisplay}
  </span>
  <input id="daynav-hidden-date" type="date" class="sr-only" onchange={handleDateInput} />

  <button
    class="duration-micro flex h-9 w-9 items-center justify-center rounded-full text-surface-600 transition-colors hover:bg-primary-50 hover:text-primary-600"
    onclick={onNext}
    aria-label="Next day"
    type="button"
  >
    <Icon name="chevron-right" />
  </button>

  {#if !isToday}
    <Btn
      variant="secondary"
      size="sm"
      onclick={() => onDateChange?.(new Date().toISOString().split('T')[0])}>Today</Btn
    >
  {/if}

  {@render children?.()}
</div>
