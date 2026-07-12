<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import Card from '$components/ui/Card.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import Spinner from '$components/ui/Spinner.svelte';

  let stats = liveQuery(() => db.admin_stats.get('global'));
</script>

{#if !$stats}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else}
  <div class="space-y-6">
    <Card>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">System Statistics</span>
      {/snippet}
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div class="rounded-lg border border-surface-200 bg-surface-50 p-5">
          <Stat value={$stats.total_users ?? 0} label="Total Users" />
        </div>
        <div class="rounded-lg border border-surface-200 bg-surface-50 p-5">
          <Stat value={$stats.total_measurements ?? 0} label="Total Measurements" />
        </div>
        <div class="rounded-lg border border-surface-200 bg-surface-50 p-5">
          <Stat value={$stats.total_metric_types ?? 0} label="Metric Types" />
        </div>
        <div class="rounded-lg border border-surface-200 bg-surface-50 p-5">
          <Stat value={$stats.total_goals ?? 0} label="Total Goals" />
        </div>
        {#if $stats.db_size}
          <div class="rounded-lg border border-surface-200 bg-surface-50 p-5">
            <Stat value={$stats.db_size} label="Database Size" />
          </div>
        {/if}
      </div>
    </Card>
  </div>
{/if}
