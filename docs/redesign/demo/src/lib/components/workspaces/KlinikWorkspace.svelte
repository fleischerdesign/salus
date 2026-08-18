<script lang="ts">
  import MetricsOverviewPage from '../pages/MetricsOverviewPage.svelte';
  import MetricGroupDetailPage from '../pages/MetricGroupDetailPage.svelte';
  import MetricSingleDetailPage from '../pages/MetricSingleDetailPage.svelte';
  import LabsPage from '../pages/LabsPage.svelte';
  import MedicationsPage from '../pages/MedicationsPage.svelte';
  import GoalsPage from '../pages/GoalsPage.svelte';

  export type KlinikTab = 'metrics' | 'labs' | 'medications' | 'goals';

  let {
    activeTab = 'metrics',
    selectedGroupKey = 'blood_pressure',
    selectedMetricCode = 'systolic_bp',
    metricViewMode = 'overview', // 'overview' | 'group' | 'single'
    onopenpdf
  } = $props<{
    activeTab?: KlinikTab;
    selectedGroupKey?: string;
    selectedMetricCode?: string;
    metricViewMode?: 'overview' | 'group' | 'single';
    onopenpdf?: () => void;
  }>();

  let currentMetricMode = $state<'overview' | 'group' | 'single'>('overview');
  let currentGroup = $state('blood_pressure');
  let currentMetric = $state('systolic_bp');

  $effect(() => {
    currentMetricMode = metricViewMode;
    if (selectedGroupKey) currentGroup = selectedGroupKey;
    if (selectedMetricCode) currentMetric = selectedMetricCode;
  });
</script>

<div class="space-y-6">
  <!-- Workspace Content Area (Driven by Topbar Ribbon) -->
  {#if activeTab === 'metrics'}
    {#if currentMetricMode === 'overview'}
      <MetricsOverviewPage
        onSelectGroup={(gk) => { currentGroup = gk; currentMetricMode = 'group'; }}
        onSelectMetric={(gk, mc) => { currentGroup = gk; currentMetric = mc; currentMetricMode = 'single'; }}
      />
    {:else if currentMetricMode === 'group'}
      <MetricGroupDetailPage
        groupKey={currentGroup}
        onBack={() => currentMetricMode = 'overview'}
        onSelectMetric={(gk, mc) => { currentGroup = gk; currentMetric = mc; currentMetricMode = 'single'; }}
      />
    {:else if currentMetricMode === 'single'}
      <MetricSingleDetailPage
        groupKey={currentGroup}
        metricCode={currentMetric}
        onBackGroup={() => currentMetricMode = 'group'}
        onBackAll={() => currentMetricMode = 'overview'}
      />
    {/if}
  {:else if activeTab === 'labs'}
    <LabsPage {onopenpdf} />
  {:else if activeTab === 'medications'}
    <MedicationsPage />
  {:else if activeTab === 'goals'}
    <GoalsPage />
  {/if}
</div>
