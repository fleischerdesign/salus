<script lang="ts">
  import Icon from './Icon.svelte';

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

  $effect(() => {
    const timer = setTimeout(() => onsearch?.(value), debounceMs);
    return () => clearTimeout(timer);
  });

  function clear() {
    value = '';
  }
</script>

<div class="relative flex items-center {extraClass}">
  <span
    class="text-surface-400 pointer-events-none absolute inset-y-0 left-0 flex w-9 items-center justify-center"
  >
    <Icon name="search" size="sm" />
  </span>
  <input
    {name}
    type="search"
    {placeholder}
    bind:value
    class="duration-micro border-surface-300 bg-surface-50 text-surface-900 placeholder:text-surface-400 hover:border-surface-400 focus:border-primary-500 focus:bg-surface-0 focus:ring-primary-200 h-10 w-full rounded-md border pr-9 pl-9 text-sm font-normal transition-colors focus:ring-2 focus:outline-none"
  />
  {#if value}
    <button
      type="button"
      class="duration-micro text-surface-400 hover:text-surface-600 absolute inset-y-0 right-0 flex w-9 items-center justify-center transition-colors"
      aria-label="Clear search"
      onclick={clear}
    >
      <Icon name="close" size="sm" />
    </button>
  {/if}
</div>
