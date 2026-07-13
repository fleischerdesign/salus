<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import { fly } from 'svelte/transition';
  import { DURATIONS, motionParams } from '$lib/utils/motion';
  import { onMount } from 'svelte';

  interface Props {
    threshold?: number;
    class?: string;
  }

  let { threshold = 300, class: extraClass = '' }: Props = $props();

  let visible = $state(false);

  function handleScroll() {
    visible = window.scrollY > threshold;
  }

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  onMount(() => {
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  });
</script>

{#if visible}
  <button
    type="button"
    class="duration-micro fixed right-6 bottom-6 z-50 flex h-10 w-10 items-center justify-center rounded-full bg-primary-500 text-white shadow-lg transition-all hover:bg-primary-600 active:scale-95 {extraClass}"
    in:fly={{ y: 16, ...motionParams(DURATIONS.normal) }}
    out:fly={{ y: 16, ...motionParams(DURATIONS.normal) }}
    aria-label="Scroll to top"
    onclick={scrollToTop}
  >
    <Icon name="keyboard-arrow-up" />
  </button>
{/if}
