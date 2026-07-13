<script lang="ts">
  import { fade } from 'svelte/transition';
  import { page } from '$app/state';
  import { DURATIONS, EASINGS, motionParams } from '$lib/utils/motion';
  import type { Snippet } from 'svelte';

  let { children }: { children: Snippet } = $props();
</script>

{#key page.url.pathname}
  <div in:fade={motionParams(DURATIONS.normal, EASINGS.standard)}>
    {@render children()}
  </div>
{/key}
