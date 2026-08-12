<script lang="ts">
  import { useQuery } from '$lib/db/use-query.svelte';
  import { db } from '$lib/db/database';
  import type { MetricWithPreference } from '$lib/db/types';
  import { fetchMetricOverview } from '$lib/analytics/views/metric-overview';
  import MetricEntryDetail from '$components/entries/MetricEntryDetail.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import { page } from '$app/state';

  const parentGroupKey = $derived(page.params.id);
  const childMetricCode = $derived(page.params.metric_code);

  const metricDataQuery = useQuery(async () => {
    const code = childMetricCode;
    if (!code) return null;
    const def = await db.metric_definition.get(code);
    if (!def) return null;
    const prefs = await db.user_metric_preference.where('metric_code').equals(code).first();
    return {
      ...def,
      color: prefs?.color ?? '#4f46e5',
      icon: prefs?.icon ?? 'monitoring',
      widget_size: prefs?.widget_size ?? 'medium',
      widget_enabled: prefs?.widget_enabled ?? false,
      enabled: prefs?.enabled ?? true,
      position: prefs?.position ?? 0
    } satisfies MetricWithPreference;
  });
  const metric = $derived(metricDataQuery.value);
  const loading = $derived(metricDataQuery.loading);

  const overviewsQuery = useQuery(() => fetchMetricOverview());
  const overviews = $derived(overviewsQuery.value);
</script>

<svelte:head><title>Salus — {metric?.name ?? 'Entries'}</title></svelte:head>

{#if loading || !metric}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else}
  <MetricEntryDetail
    metricCode={metric.code}
    {metric}
    {overviews}
    backUrl="/entries/{parentGroupKey}"
    showSettings
  />
{/if}
