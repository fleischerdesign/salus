<script lang="ts">
  import { type Snippet } from 'svelte';
  import { setContext } from 'svelte';

  interface Props {
    children: Snippet;
    class?: string;
  }

  let { children, class: extraClass = '' }: Props = $props();

  let openItems = $state<Set<string>>(new Set());

  setContext('accordion', {
    toggle(id: string) {
      if (openItems.has(id)) openItems.delete(id);
      else openItems.add(id);
      openItems = new Set(openItems);
    },
    get isOpen() {
      return (id: string) => openItems.has(id);
    }
  });
</script>

<div class="divide-y divide-surface-200 rounded-lg border border-surface-200 bg-surface-0 {extraClass}">
  {@render children()}
</div>
