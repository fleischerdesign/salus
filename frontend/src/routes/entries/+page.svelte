<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { MetricWithPreference } from '$lib/db/types';
  import { mergeMetricPrefs } from '$lib/db/types';
  import { fetchMetricOverview, overviewForMetric } from '$lib/analytics/views/metric-overview';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';
  import Card from '$components/ui/Card.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Icon from '$components/ui/Icon.svelte';

  type Metric = MetricWithPreference;

  let allDefs = liveQuery(() => db.metric_definition.toArray());
  let allPrefs = liveQuery(() => db.user_metric_preference.toArray());
  let groups = liveQuery(() => db.metric_group.toArray());

  let metrics = $derived(
    $allDefs && $allPrefs ? mergeMetricPrefs($allDefs, $allPrefs) : null
  );
  let overviews = liveQuery(() => fetchMetricOverview());

  let groupedMetrics = $derived(
    metrics && $groups
      ? metrics.filter((m) => m.group_key != null)
      : []
  );
  let standaloneMetrics = $derived(
    metrics ? metrics.filter((m) => m.group_key == null && m.enabled) : []
  );

  function metricsInGroup(groupKey: string): Metric[] {
    return metrics ? metrics.filter((m) => m.group_key === groupKey) : [];
  }

  function groupLatestDate(groupKey: string): string | null {
    const groupMetrics = metricsInGroup(groupKey);
    let latest: string | null = null;
    for (const m of groupMetrics) {
      const ov = overviewForMetric($overviews ?? [], m.code);
      if (ov?.latest_date && (!latest || ov.latest_date > latest)) {
        latest = ov.latest_date;
      }
    }
    return latest;
  }

  function groupTotalEntries(groupKey: string): number {
    let total = 0;
    for (const m of metricsInGroup(groupKey)) {
      const ov = overviewForMetric($overviews ?? [], m.code);
      if (ov) total += ov.entry_count;
    }
    return total;
  }
</script>

<svelte:head><title>Salus — Logbook</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Logbook"
    subtitle="Select a metric to view and manage its entries."
    icon="library-books"
    iconColor="#4f46e5"
  />

  {#if metrics === undefined || $overviews === undefined || $groups === undefined}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if (metrics?.length ?? 0) === 0}
    <EmptyState
      title="No metrics yet"
      description="Metric definitions will appear after syncing with the server."
      icon="receipt-long"
    />
  {:else}
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <!-- Group cards -->
      {#each $groups as group, i (group.key)}
        {@const gMetrics = metricsInGroup(group.key)}
        {#if gMetrics.length > 0}
          <a
            href="/entries/{group.key}"
            class="no-underline"
            in:fade={{ ...staggerFade(i) }}
          >
            <Card padding={false} hoverable>
              {#snippet header()}
                <div class="flex items-center gap-3">
                  <div
                    class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
                    style="background-color: {gMetrics[0].color}20; color: {gMetrics[0].color}"
                  >
                    <Icon name={group.icon || 'monitoring'} />
                  </div>
                  <div class="min-w-0 flex-1">
                    <p class="truncate text-sm font-medium text-surface-900">{group.name}</p>
                    <p class="text-xs text-surface-500">
                      {gMetrics.map((m) => m.name).join(', ')}
                    </p>
                  </div>
                  <div class="flex h-6 items-center rounded-full bg-surface-100 px-2 text-xs text-surface-500">
                    {gMetrics.length}
                  </div>
                </div>
              {/snippet}
              <div class="p-6">
                {#if groupLatestDate(group.key)}
                  <div class="flex items-baseline gap-1">
                    <span class="text-lg font-bold text-surface-900">
                      {gMetrics.length} metrics
                    </span>
                  </div>
                  <p class="mt-0.5 text-xs text-surface-400">
                    Latest: {groupLatestDate(group.key)} · {groupTotalEntries(group.key)} entries
                  </p>
                {:else}
                  <p class="text-xs text-surface-400">No entries yet</p>
                {/if}
              </div>
            </Card>
          </a>
        {/if}
      {/each}

      <!-- Standalone metric cards -->
      {#each standaloneMetrics as m, i (m.code)}
        {@const ov = overviewForMetric($overviews, m.code)}
        <a href="/entries/{m.code}" class="no-underline" in:fade={{ ...staggerFade(groupedMetrics.length + i) }}>
          <Card padding={false} hoverable>
            {#snippet header()}
              <div class="flex items-center gap-3">
                <div
                  class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
                  style="background-color: {m.color}20; color: {m.color}"
                >
                  <Icon name={m.icon || 'monitoring'} />
                </div>
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-medium text-surface-900">{m.name}</p>
                  <p class="text-xs text-surface-500">{m.unit || '—'}</p>
                </div>
              </div>
            {/snippet}
            <div class="p-6">
              {#if ov}
                <div class="flex items-baseline gap-1">
                  <span class="text-lg font-bold text-surface-900">
                    {ov.latest_value ?? '—'}
                  </span>
                  {#if ov.latest_value && m.unit}
                    <span class="text-xs text-surface-400">{m.unit}</span>
                  {/if}
                </div>
                <p class="mt-0.5 text-xs text-surface-400">
                  {ov.latest_date ?? 'No entries'} · {ov.entry_count}
                  {ov.entry_count === 1 ? 'entry' : 'entries'}
                </p>
              {:else}
                <p class="text-xs text-surface-400">No entries yet</p>
              {/if}
            </div>
          </Card>
        </a>
      {/each}
    </div>
  {/if}
</div>
