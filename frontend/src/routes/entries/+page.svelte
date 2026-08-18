<script lang="ts">
  import { goto } from '$app/navigation';
  import MetricsOverviewPage from '$components/pages/MetricsOverviewPage.svelte';
</script>

<MetricsOverviewPage
  onSelectGroup={(gk) => goto(`/entries/${gk}`)}
  onSelectMetric={(gk, mc) => goto(`/entries/${gk}/${mc}`)}
/>
