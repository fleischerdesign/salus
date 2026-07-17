<script lang="ts">
  import { liveQuery } from 'dexie';
  import { page } from '$app/stores';
  import { db } from '$lib/db/database';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';

  let id = $derived($page.params.id);
  let loading = $state(true);

  $effect(() => {
    if (!id) return;
    const sub = liveQuery(() => db.habit.get(id)).subscribe(() => {
      loading = false;
    });
    return () => sub.unsubscribe();
  });
</script>

<svelte:head><title>Salus — Habit Detail</title></svelte:head>

<div class="space-y-6">
  {#if loading}
    <div class="h-64 animate-pulse rounded-xl bg-surface-100"></div>
  {:else}
    <PageHeader
      title="Habit Detail"
      subtitle="Coming soon"
      icon="check-circle"
      iconColor="#4f46e5"
    />
    <Card>
      <div class="p-8 text-center text-surface-500">
        Detailed habit view with heatmap and stats — coming soon.
      </div>
    </Card>
  {/if}
</div>
