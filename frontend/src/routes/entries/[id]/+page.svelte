<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import MetricGroupDetailPage from '$components/pages/MetricGroupDetailPage.svelte';

  const groupKey = $derived(page.params.id || 'blood_pressure');
</script>

<MetricGroupDetailPage
  {groupKey}
  onBack={() => goto('/entries')}
  onSelectMetric={(gk, mc) => goto(`/entries/${gk}/${mc}`)}
/>
