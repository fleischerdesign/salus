<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import { fly } from 'svelte/transition';
  import { scrollY } from 'svelte/reactivity/window';
  import { DURATIONS, motionParams } from '$lib/utils/motion';

  interface Props {
    threshold?: number;
    class?: string;
  }

  let { threshold = 300, class: extraClass = '' }: Props = $props();

  let visible = $derived((scrollY.current ?? 0) > threshold);

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
</script>

{#if visible}
  <button
    type="button"
    class="duration-micro fixed right-6 bottom-6 z-50 flex h-10 w-10 items-center justify-center rounded-full bg-primary-500 text-on-primary shadow-lg transition-all hover:bg-primary-600 active:scale-95 {extraClass}"
    in:fly={{ y: 16, ...motionParams(DURATIONS.normal) }}
    out:fly={{ y: 16, ...motionParams(DURATIONS.normal) }}
    aria-label="Scroll to top"
    onclick={scrollToTop}
  >
    <Icon name="keyboard-arrow-up" />
  </button>
{/if}
