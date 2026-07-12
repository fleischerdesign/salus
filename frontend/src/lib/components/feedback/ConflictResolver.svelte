<script lang="ts">
  import { db } from '$lib/db/database';
  import { mutate } from '$lib/db/mutate';
  import ConflictDialog from '$components/ui/ConflictDialog.svelte';
  import { conflictStore } from '$stores/conflict.svelte';

  let resolving = $state(false);

  async function handleResolve(fields: Record<string, unknown> | null) {
    const conflict = conflictStore.current;
    if (!conflict || resolving) return;

    if (fields === null || Object.keys(fields).length === 0) {
      await db.table(conflict.table).put(conflict.serverRecord);
      conflictStore.resolve(conflict.id);
      return;
    }

    resolving = true;

    const merged = { ...conflict.serverRecord, ...fields };
    await mutate({
      table: conflict.table,
      type: 'update',
      data: fields,
      optimistic: merged,
      realId: conflict.realId
    });

    conflictStore.resolve(conflict.id);
    resolving = false;
  }
</script>

{#if conflictStore.hasPending && conflictStore.current}
  <ConflictDialog
    table={conflictStore.current.table}
    clientRecord={conflictStore.current.clientRecord}
    serverRecord={conflictStore.current.serverRecord}
    onresolve={handleResolve}
    open={true}
  />
{/if}
