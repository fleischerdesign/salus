<script lang="ts">
  import Icon from './Icon.svelte';
  import { onMount, onDestroy } from 'svelte';

  interface Props {
    name?: string;
    placeholder?: string;
    value?: string;
    debounceMs?: number;
    onsearch?: (query: string) => void;
    class?: string;
  }

  let {
    name = 'q',
    placeholder = 'Search…',
    value = $bindable(''),
    debounceMs = 300,
    onsearch,
    class: extraClass = ''
  }: Props = $props();

  let timer: ReturnType<typeof setTimeout> | null = null;

  function handleInput(e: Event) {
    const input = e.target as HTMLInputElement;
    value = input.value;
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => onsearch?.(value), debounceMs);
  }

  function clear() {
    value = '';
    onsearch?.('');
  }

  onDestroy(() => {
    if (timer) clearTimeout(timer);
  });
</script>

<div class="relative {extraClass}">
  <span class="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-surface-400">
    <Icon name="search" size="sm" />
  </span>
  <input
    {name}
    type="search"
    {placeholder}
    value
    oninput={handleInput}
    class="h-10 w-full rounded-md border border-surface-300 bg-surface-50 pr-9 pl-9 text-sm text-surface-900 transition-colors duration-150 placeholder:text-surface-400 hover:border-surface-400 focus:border-primary-500 focus:bg-surface-0 focus:ring-2 focus:ring-primary-200 focus:outline-none"
  />
  {#if value}
    <button
      type="button"
      class="absolute top-1/2 right-2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full text-surface-400 transition-colors duration-150 hover:bg-surface-200 hover:text-surface-600"
      aria-label="Clear search"
      onclick={clear}
    >
      <Icon name="close" size="sm" />
    </button>
  {/if}
</div>
