<script lang="ts">
  import { type Snippet, untrack } from 'svelte';
  import { getContext } from 'svelte';
  import Icon from './Icon.svelte';

  interface Props {
    title: string;
    open?: boolean;
    children: Snippet;
  }

  let { title, open = false, children }: Props = $props();

  const accordion = getContext<{
    toggle: (id: string) => void;
    isOpen: (id: string) => boolean;
  }>('accordion');

  const id = `acc-${Math.random().toString(36).slice(2, 9)}`;
  let isOpen = $derived(accordion.isOpen(id));

  if (untrack(() => open)) accordion.toggle(id);
</script>

<div>
  <button
    type="button"
    class="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-semibold text-surface-900 transition-colors duration-150 hover:bg-surface-50"
    aria-expanded={isOpen}
    onclick={() => accordion.toggle(id)}
  >
    {title}
    <Icon name="expand-more" size="sm" class="transition-transform duration-150 {isOpen ? 'rotate-180' : ''}" />
  </button>
  {#if isOpen}
    <div class="px-4 py-3 text-sm text-surface-600">
      {@render children()}
    </div>
  {/if}
</div>
