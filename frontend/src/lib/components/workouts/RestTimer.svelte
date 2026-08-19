<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import { fly, fade } from 'svelte/transition';
  import { DURATIONS, motionParams } from '$lib/utils/motion';
  import { onDestroy, untrack } from 'svelte';

  interface Props {
    initialSeconds?: number;
    addIncrement?: number;
    oncomplete?: () => void;
    onstart?: (startFn: (seconds?: number) => void) => void;
    class?: string;
  }

  let {
    initialSeconds = 90,
    addIncrement = 30,
    oncomplete,
    onstart,
    class: extraClass = ''
  }: Props = $props();

  let active = $state(false);
  let remaining = $state(untrack(() => initialSeconds));
  let intervalId: ReturnType<typeof setInterval> | null = null;

  function start(seconds?: number) {
    if (seconds !== undefined) remaining = seconds;
    active = true;
    if (intervalId) clearInterval(intervalId);
    intervalId = setInterval(tick, 1000);
  }

  function tick() {
    remaining--;
    if (remaining <= 0) {
      remaining = 0;
      active = false;
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
      oncomplete?.();
    }
  }

  function addTime() {
    remaining += addIncrement;
  }

  function dismiss() {
    active = false;
    remaining = initialSeconds;
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  }

  let display = $derived(
    remaining >= 60 ? `${Math.floor(remaining / 60)}m ${remaining % 60}s` : `${remaining}s`
  );

  $effect(() => {
    onstart?.(start);
  });

  onDestroy(() => {
    if (intervalId) clearInterval(intervalId);
  });
</script>

{#if active}
  <div
    class="fixed bottom-6 left-1/2 z-50 flex -translate-x-1/2 items-center gap-2 rounded-full border border-surface-200 bg-surface-0 px-4 py-2 text-sm font-semibold text-surface-900 shadow-lg {extraClass}"
    in:fly={{ y: 16, ...motionParams(DURATIONS.normal) }}
    out:fade={motionParams(DURATIONS.fast)}
    role="timer"
    aria-live="polite"
  >
    <Icon name="timer" size="sm" class="text-primary-500" />
    <span class="tabular-nums">{display}</span>
    <button
      type="button"
      class="ml-1 rounded-full bg-surface-100 px-2 py-0.5 text-xs font-medium text-surface-600 hover:bg-surface-200"
      onclick={addTime}>+{addIncrement}s</button
    >
    <button
      type="button"
      class="ml-1 flex h-6 w-6 items-center justify-center rounded-full text-surface-400 hover:bg-surface-100 hover:text-surface-600"
      aria-label="Dismiss timer"
      onclick={dismiss}
    >
      <Icon name="close" size="sm" />
    </button>
  </div>
{/if}
