<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
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
    class="fixed bottom-6 right-6 z-50 flex h-10 w-10 items-center justify-center rounded-full bg-primary-500 text-white shadow-lg transition-all duration-150 hover:bg-primary-600 active:scale-95 {extraClass}"
    aria-label="Scroll to top"
    onclick={scrollToTop}
  >
    <Icon name="keyboard-arrow-up" />
  </button>
{/if}
