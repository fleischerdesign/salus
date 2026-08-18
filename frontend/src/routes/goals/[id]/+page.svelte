<script lang="ts">
  import { db } from '$lib/db/database';
  import { fetchGoalView } from '$lib/analytics/views/goal-views';
  import { formatValue, progressVariant, statusColor } from '$lib/analytics/goal-ui';
  import { page } from '$app/state';
  import Card from '$components/ui/Card.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import ProgressBar from '$components/ui/ProgressBar.svelte';
  import LineChart from '$components/dashboard/LineChart.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import { regressionSeries } from '$lib/analytics/stats';
  import { useQuery } from '$lib/db/use-query.svelte';

  const goalId = $derived(page.params.id as string);

  const goalViewQuery = useQuery(
    () => fetchGoalView(goalId),
    () => goalId
  );
  const goalView = $derived(goalViewQuery.value);

  const nutrientLabels: Record<string, string> = {
    calories: 'Calories',
    protein: 'Protein',
    carbs: 'Carbs',
    fat: 'Fat'
  };
  const nutritionUnit = $derived(
    goalView?.nutrition_field
      ? (nutrientLabels[goalView.nutrition_field] ?? goalView.nutrition_field)
      : ''
  );

  // Load measurements for this goal's metric type to render trend chart
  const measurementsQuery = useQuery(
    async () => {
      const g = await db.goal.get(goalId);
      if (!g) return [];
      return db.measurement
        .where('metric_code')
        .equals(g.metric_code)
        .toArray()
        .then((arr) =>
          arr
            .filter((m) => !m.deleted_at && m.value_numeric != null)
            .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
        );
    },
    () => goalId
  );
  const measurements = $derived(measurementsQuery.value);

  let chartData = $derived.by(() => {
    if (!measurements || (measurements ?? []).length === 0 || !goalView) return null;

    const labels = (measurements ?? []).map((m) => m.start_time.slice(5, 10));
    const values = (measurements ?? []).map((m) => m.value_numeric!);

    // Calculate OLS regression and prediction intervals
    let regressionLine: Array<{ x: number; y: number }> | null = null;
    let regressionCI: Array<{ x: number; lower: number; upper: number }> | null = null;
    if (values.length >= 3) {
      const series = regressionSeries(values, 0.8);
      if (series) {
        regressionLine = series.points;
        regressionCI = series.ci;
      }
    }

    // Draw horizontal target line
    const targetLine = Array(labels.length).fill(goalView.target_value);

    const series = [
      {
        label: goalView.metric_name,
        data: values,
        color: goalView.metric_color,
        yAxis: 'left' as const
      },
      {
        label: 'Goal Target',
        data: targetLine,
        color: 'var(--color-error-500)',
        yAxis: 'left' as const
      }
    ];

    return { labels, series, regressionLine, regressionCI };
  });

  function calculateRequiredRate(): string | null {
    if (!goalView || !goalView.deadline || goalView.progress.current_value === null) return null;
    const diff = goalView.target_value - goalView.progress.current_value;
    const remainingDays = Math.ceil(
      (new Date(goalView.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
    );

    if (remainingDays <= 0) return null;

    const rate = diff / remainingDays;
    const absRateStr = Math.abs(rate).toFixed(1).replace(/\.0$/, '');

    if (goalView.direction === 'increase') {
      return rate > 0
        ? `You need to increase by an average of ${absRateStr} ${goalView.metric_unit} per day to hit your target.`
        : 'You have already met the target value! Maintain consistency.';
    } else {
      return rate < 0
        ? `You need to decrease by an average of ${absRateStr} ${goalView.metric_unit} per day to hit your target.`
        : 'You have already met the target value! Maintain consistency.';
    }
  }
</script>

<svelte:head>
  <title>Salus — Goal Details</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <PageHeader
    title={goalView ? `${goalView.metric_name} Goal` : 'Loading Goal…'}
    subtitle={goalView
      ? nutritionUnit
        ? `${goalView.frequency} Goal · ${nutritionUnit}`
        : `${goalView.frequency} Goal`
      : ''}
    backUrl="/goals"
    icon={goalView?.metric_icon || 'track-changes'}
    iconColor={goalView?.metric_color}
  >
    {#snippet stats()}
      {#if goalView}
        <div class="grid gap-6 px-6 py-6 md:grid-cols-3">
          <div class="space-y-1">
            <span class="text-surface-400 text-xs font-medium tracking-wider uppercase"
              >Current / Target</span
            >
            <div class="flex items-baseline gap-1.5">
              <span class="text-surface-900 text-2xl font-bold">
                {formatValue(goalView.progress.current_value)}
              </span>
              <span class="text-surface-400 text-sm">
                / {formatValue(goalView.target_value)}
                {goalView.metric_unit}
              </span>
            </div>
          </div>

          <div class="space-y-1">
            <span class="text-surface-400 text-xs font-medium tracking-wider uppercase">Status</span
            >
            <div>
              <span class="text-sm font-bold uppercase {statusColor(goalView.progress.status)}">
                {goalView.progress.status}
              </span>
            </div>
          </div>

          {#if goalView.deadline}
            <div class="space-y-1">
              <span class="text-surface-400 text-xs font-medium tracking-wider uppercase"
                >Deadline</span
              >
              <div class="text-surface-700 text-sm font-semibold">
                {new Date(goalView.deadline).toLocaleDateString(undefined, {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </div>
            </div>
          {/if}
        </div>

        <div class="border-surface-100 border-t px-6 py-4">
          <div class="mb-2 flex items-center justify-between">
            <span class="text-surface-500 text-xs font-semibold">Goal Completion Progress</span>
            <span class="text-surface-700 text-xs font-bold">{goalView.progress.percent}%</span>
          </div>
          <ProgressBar
            value={goalView.progress.percent}
            max={100}
            variant={progressVariant(goalView.progress.status)}
            height="md"
          />
        </div>
      {/if}
    {/snippet}
  </PageHeader>

  {#if !goalView || !measurements}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else}
    <div class="grid gap-6 lg:grid-cols-12">
      <!-- Chart Card -->
      <Card padding={false} class="lg:col-span-8">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="show_chart" size="sm" class="text-surface-400" />
            <span class="text-surface-900 text-sm font-semibold">Historical Trend vs. Target</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if chartData}
            <LineChart
              labels={chartData.labels}
              series={chartData.series}
              leftUnit={goalView.metric_unit}
              regressionLine={chartData.regressionLine}
              regressionCI={chartData.regressionCI}
            />
          {:else}
            <div class="flex h-[200px] items-center justify-center">
              <p class="text-surface-400 text-sm">No data points logged for this metric yet.</p>
            </div>
          {/if}
        </div>
      </Card>

      <!-- Forecast Card -->
      <div class="space-y-6 lg:col-span-4">
        {#if goalView.forecast}
          <Card padding={false}>
            {#snippet header()}
              <div class="flex items-center gap-2">
                <Icon name="query_stats" size="sm" class="text-surface-400" />
                <span class="text-surface-900 text-sm font-semibold">Statistical Forecast</span>
              </div>
            {/snippet}
            <div class="space-y-4 p-6">
              <div class="flex items-center justify-between">
                <span class="text-surface-500 text-sm">Deadline Status</span>
                <span
                  class="rounded px-2 py-0.5 text-xs font-bold"
                  class:bg-success-50={goalView.forecast.on_track}
                  class:text-success-600={goalView.forecast.on_track}
                  class:bg-error-50={!goalView.forecast.on_track}
                  class:text-error-600={!goalView.forecast.on_track}
                >
                  {goalView.forecast.on_track ? 'ON TRACK' : 'OFF TRACK'}
                </span>
              </div>

              <div class="border-surface-100 flex items-baseline justify-between border-t pt-3">
                <span class="text-surface-500 text-sm">Est. Target Value</span>
                <span class="text-surface-900 text-lg font-bold">
                  {formatValue(goalView.forecast.predicted)}
                  {goalView.metric_unit}
                </span>
              </div>

              <div class="text-surface-400 flex justify-between text-xs">
                <span>80% Confidence Range</span>
                <span class="font-medium">
                  [{formatValue(goalView.forecast.ci_lower)} – {formatValue(
                    goalView.forecast.ci_upper
                  )}]
                </span>
              </div>

              <div class="border-surface-100 border-t pt-3">
                <span class="text-surface-400 mb-1 block text-xs font-semibold">Recommendation</span
                >
                <p class="text-surface-600 text-xs leading-relaxed">
                  {calculateRequiredRate()}
                </p>
              </div>
            </div>
          </Card>
        {/if}

        <Card padding={false}>
          {#snippet header()}
            <div class="flex items-center gap-2">
              <Icon name="info" size="sm" class="text-surface-400" />
              <span class="text-surface-900 text-sm font-semibold">Goal Parameters</span>
            </div>
          {/snippet}
          <div class="text-surface-600 space-y-3 p-6 text-sm">
            <div class="flex justify-between">
              <span>Goal Type</span>
              <span class="text-surface-800 font-medium capitalize">{goalView.frequency}</span>
            </div>
            <div class="flex justify-between">
              <span>Direction</span>
              <span class="text-surface-800 font-medium capitalize">{goalView.direction}</span>
            </div>
            <div class="flex justify-between">
              <span>Metric</span>
              <span class="text-surface-800 font-medium">{goalView.metric_name}</span>
            </div>
          </div>
        </Card>
      </div>

      <!-- Recent Log Entries -->
      <Card padding={false} class="lg:col-span-full">
        {#snippet header()}
          <div class="flex items-center justify-between pr-2">
            <div class="flex items-center gap-2">
              <Icon name="list_alt" size="sm" class="text-surface-400" />
              <span class="text-surface-900 text-sm font-semibold">Recent Contributions</span>
            </div>
            <a
              href="/entries/{goalView.metric_code}"
              class="text-primary-600 hover:text-primary-700 text-xs font-semibold"
            >
              Manage Entries
            </a>
          </div>
        {/snippet}
        <div class="divide-surface-100 divide-y">
          {#if (measurements ?? []).length === 0}
            <div class="text-surface-400 p-6 text-center text-sm">
              No measurements logged for this metric yet.
            </div>
          {:else}
            {#each (measurements ?? []).slice(-5).reverse() as m}
              <div class="hover:bg-surface-50 flex items-center justify-between px-6 py-3.5">
                <div class="flex items-baseline gap-1">
                  <span class="text-surface-900 text-sm font-bold">
                    {formatValue(m.value_numeric)}
                  </span>
                  <span class="text-surface-400 text-xs">{goalView.metric_unit}</span>
                </div>
                <div class="text-surface-400 text-xs">
                  {new Date(m.start_time).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            {/each}
          {/if}
        </div>
      </Card>
    </div>
  {/if}
</div>
