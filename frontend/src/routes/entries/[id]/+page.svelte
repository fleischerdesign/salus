<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import MetricGroupDetailPage from '$components/pages/MetricGroupDetailPage.svelte';
  import MetricSingleDetailPage from '$components/pages/MetricSingleDetailPage.svelte';
  import { METRIC_GROUPS } from '$lib/data/metrics-data';

  const id = $derived(page.params.id || '');

  // Check if id matches a known metric group key
  const isGroup = $derived(METRIC_GROUPS.some((g) => g.key === id));

  // Find parent group if id is a metric code
  const parentGroup = $derived(METRIC_GROUPS.find((g) => g.subMetrics.some((m) => m.code === id)));
</script>

{#if isGroup}
  <MetricGroupDetailPage
    groupKey={id}
    onBack={() => goto('/entries')}
    onSelectMetric={(gk, mc) => goto(`/entries/${gk}/${mc}`)}
  />
{:else}
  <MetricSingleDetailPage
    groupKey={parentGroup?.key || 'blood_pressure'}
    metricCode={id}
    onBack={() => goto(parentGroup ? `/entries/${parentGroup.key}` : '/entries')}
    onBackGroup={() => goto(parentGroup ? `/entries/${parentGroup.key}` : '/entries')}
    onBackAll={() => goto('/entries')}
  />
{/if}
