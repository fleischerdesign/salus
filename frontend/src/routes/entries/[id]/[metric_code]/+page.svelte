<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import MetricSingleDetailPage from '$components/pages/MetricSingleDetailPage.svelte';

  const groupKey = $derived(page.params.id || 'blood_pressure');
  const metricCode = $derived(page.params.metric_code || 'systolic_bp');
</script>

<MetricSingleDetailPage {groupKey} {metricCode} onBack={() => goto(`/entries/${groupKey}`)} />
