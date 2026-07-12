<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Props {
    text: string;
    position?: 'top' | 'bottom';
    children: Snippet;
  }

  let { text, position = 'top', children }: Props = $props();

  let bubbleClass = $derived(
    'absolute left-1/2 z-tooltip -translate-x-1/2 rounded px-2 py-1 text-xs font-medium text-white opacity-0 shadow-md transition-opacity duration-150 group-hover:opacity-100 bg-surface-900 whitespace-nowrap ' +
    (position === 'top' ? 'bottom-full mb-1.5' : 'top-full mt-1.5')
  );

  let arrowClass = $derived(
    'absolute left-1/2 h-0 w-0 -translate-x-1/2 border-4 border-transparent ' +
    (position === 'top' ? 'top-full border-t-surface-900' : 'bottom-full border-b-surface-900')
  );
</script>

<span class="relative inline-flex group">
  {@render children?.()}
  <span class={bubbleClass}>
    {text}
    <span class={arrowClass}></span>
  </span>
</span>
