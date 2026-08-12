<script lang="ts">
  import { useQuery } from '$lib/db/use-query.svelte';

  let { querier }: { querier: () => Promise<unknown[]> } = $props();

  const query = useQuery(() => querier());
  const items = $derived(query.value);
  const loading = $derived(query.loading);
</script>

<div>
  {#if loading}
    <span class="loading">LOADING</span>
  {:else}
    <span class="loaded">loaded:{(items ?? []).length}</span>
  {/if}
</div>
