<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { FederatedAccessLog } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import Table from '$components/ui/Table.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';

  let logs = liveQuery(() =>
    db.federated_access_log
      .toArray()
      .then((arr) =>
        arr.sort((a, b) => new Date(b.accessed_at).getTime() - new Date(a.accessed_at).getTime())
      )
  );

  const columns = [
    { key: 'requester', label: 'Requester' },
    { key: 'data_type', label: 'Data Type' },
    { key: 'target_date', label: 'Date Requested' },
    { key: 'accessed_at', label: 'Accessed At' }
  ];
</script>

<svelte:head><title>Salus — Access Log</title></svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-semibold text-surface-900">Access Log</h1>
    <p class="mt-1 text-sm text-surface-500">
      Track who accessed your shared health data and when.
    </p>
  </div>

  <Card padding={false}>
    {#if $logs === undefined}
      <div class="flex justify-center py-12"><Spinner /></div>
    {:else if $logs && $logs.length === 0}
      <div class="py-12">
        <EmptyState
          icon="history"
          title="No Access Events"
          description="No one has accessed your shared data yet."
        />
      </div>
    {:else}
      <div class="overflow-x-auto">
        <Table
          {columns}
          rows={$logs.map((l) => ({
            requester: l.requester_handle,
            data_type: l.data_type,
            target_date: new Date(l.target_date).toLocaleDateString(),
            accessed_at: new Date(l.accessed_at).toLocaleString()
          }))}
        />
      </div>
    {/if}
  </Card>
</div>
