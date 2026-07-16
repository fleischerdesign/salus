<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { fetchGoalView } from '$lib/analytics/views/goal-views';
  import { page } from '$app/state';
  import Card from '$components/ui/Card.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ProgressBar from '$components/ui/ProgressBar.svelte';
  import LineChart from '$components/dashboard/LineChart.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import { linearRegression, predictionInterval } from '$lib/analytics/stats';

  const goalId = $derived(page.params.id as string);

  let goalView = liveQuery(() => fetchGoalView(goalId));

  // Load measurements for this goal's metric type to render trend chart
  let measurements = liveQuery(async () => {
    const g = await db.goal.get(goalId);
    if (!g) return [];
    return db.measurement
      .where('metric_type_id')
      .equals(g.metric_type_id)
      .toArray()
      .then((arr) =>
        arr
          .filter((m) => !m.deleted_at && m.value_numeric != null)
          .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
      );
  });

  let chartData = $derived.by(() => {
    if (!$measurements || $measurements.length === 0 || !$goalView) return null;

    const labels = $measurements.map((m) => m.start_time.slice(5, 10));
    const values = $measurements.map((m) => m.value_numeric!);

    // Calculate OLS regression and prediction intervals
    let regressionLine: Array<{ x: number; y: number }> | null = null;
    let regressionCI: Array<{ x: number; lower: number; upper: number }> | null = null;
    if (values.length >= 3) {
      const xs = values.map((_, i) => i);
      const reg = linearRegression(xs, values);
      if (reg) {
        regressionLine = xs.map((x) => ({
          x,
          y: reg.intercept + reg.slope * x
        }));
        regressionCI = xs.map((x) => {
          const pi = predictionInterval(reg, x, 0.8);
          return {
            x,
            lower: pi?.lower ?? reg.intercept + reg.slope * x,
            upper: pi?.upper ?? reg.intercept + reg.slope * x
          };
        });
      }
    }

    // Draw horizontal target line
    const targetLine = Array(labels.length).fill($goalView.target_value);

    const series = [
      {
        label: $goalView.metric_name,
        data: values,
        color: $goalView.metric_color,
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

  function progressVariant(status: string): 'success' | 'error' | 'info' {
    if (status === 'fulfilled') return 'success';
    if (status === 'missed') return 'error';
    return 'info';
  }

  function statusColor(status: string): string {
    if (status === 'fulfilled') return 'text-success-600';
    if (status === 'missed') return 'text-error-500';
    return 'text-primary-600';
  }

  function formatValue(v: number | null | undefined): string {
    if (v === null || v === undefined) return '—';
    return v >= 1000
      ? v.toLocaleString(undefined, { maximumFractionDigits: 1 })
      : v.toFixed(1).replace(/\.0$/, '');
  }

  function calculateRequiredRate(): string | null {
    if (!$goalView || !$goalView.deadline || $goalView.progress.current_value === null) return null;
    const diff = $goalView.target_value - $goalView.progress.current_value;
    const remainingDays = Math.ceil(
      (new Date($goalView.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
    );

    if (remainingDays <= 0) return null;

    const rate = diff / remainingDays;
    const absRateStr = Math.abs(rate).toFixed(1).replace(/\.0$/, '');

    if ($goalView.direction === 'increase') {
      return rate > 0
        ? `You need to increase by an average of ${absRateStr} ${$goalView.metric_unit} per day to hit your target.`
        : 'You have already met the target value! Maintain consistency.';
    } else {
      return rate < 0
        ? `You need to decrease by an average of ${absRateStr} ${$goalView.metric_unit} per day to hit your target.`
        : 'You have already met the target value! Maintain consistency.';
    }
  }
</script>

<svelte:head>
  <title>Salus — Goal Details</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <Card padding={false}>
    {#snippet header()}
      <div class="flex items-center gap-3">
        <a
          href="/goals"
          class="duration-micro flex h-9 w-9 items-center justify-center rounded-lg text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700"
          aria-label="Back to Goals"
        >
          <Icon name="arrow-back" size="sm" />
        </a>
        {#if $goalView}
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
            style="background-color: {$goalView.metric_color}20; color: {$goalView.metric_color}"
          >
            <Icon name={$goalView.metric_icon || 'track-changes'} />
          </div>
        {:else}
          <div class="h-10 w-10 shrink-0 animate-pulse rounded-lg bg-surface-200"></div>
        {/if}
        <div class="min-w-0 flex-1">
          <h1 class="truncate text-lg font-semibold text-surface-900">
            {$goalView ? `${$goalView.metric_name} Goal` : 'Loading Goal…'}
          </h1>
          {#if $goalView}
            <p class="text-xs text-surface-500 capitalize">{$goalView.frequency} Goal</p>
          {/if}
        </div>
      </div>
    {/snippet}

    {#if $goalView}
      <div class="grid gap-6 px-6 py-6 md:grid-cols-3">
        <div class="space-y-1">
          <span class="text-xs font-medium tracking-wider text-surface-400 uppercase"
            >Current / Target</span
          >
          <div class="flex items-baseline gap-1.5">
            <span class="text-2xl font-bold text-surface-900">
              {formatValue($goalView.progress.current_value)}
            </span>
            <span class="text-sm text-surface-400">
              / {formatValue($goalView.target_value)}
              {$goalView.metric_unit}
            </span>
          </div>
        </div>

        <div class="space-y-1">
          <span class="text-xs font-medium tracking-wider text-surface-400 uppercase">Status</span>
          <div>
            <span class="text-sm font-bold uppercase {statusColor($goalView.progress.status)}">
              {$goalView.progress.status}
            </span>
          </div>
        </div>

        {#if $goalView.deadline}
          <div class="space-y-1">
            <span class="text-xs font-medium tracking-wider text-surface-400 uppercase"
              >Deadline</span
            >
            <div class="text-sm font-semibold text-surface-700">
              {new Date($goalView.deadline).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
          </div>
        {/if}
      </div>

      <div class="border-t border-surface-100 px-6 py-4">
        <div class="mb-2 flex items-center justify-between">
          <span class="text-xs font-semibold text-surface-500">Goal Completion Progress</span>
          <span class="text-xs font-bold text-surface-700">{$goalView.progress.percent}%</span>
        </div>
        <ProgressBar
          value={$goalView.progress.percent}
          max={100}
          variant={progressVariant($goalView.progress.status)}
          height="md"
        />
      </div>
    {/if}
  </Card>

  {#if !$goalView || !$measurements}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else}
    <div class="grid gap-6 lg:grid-cols-12">
      <!-- Chart Card -->
      <Card padding={false} class="lg:col-span-8">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="show_chart" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Historical Trend vs. Target</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if chartData}
            <LineChart
              labels={chartData.labels}
              series={chartData.series}
              leftUnit={$goalView.metric_unit}
              regressionLine={chartData.regressionLine}
              regressionCI={chartData.regressionCI}
            />
          {:else}
            <div class="flex h-[200px] items-center justify-center">
              <p class="text-sm text-surface-400">No data points logged for this metric yet.</p>
            </div>
          {/if}
        </div>
      </Card>

      <!-- Forecast Card -->
      <div class="space-y-6 lg:col-span-4">
        {#if $goalView.forecast}
          <Card padding={false}>
            {#snippet header()}
              <div class="flex items-center gap-2">
                <Icon name="query_stats" size="sm" class="text-surface-400" />
                <span class="text-sm font-semibold text-surface-900">Statistical Forecast</span>
              </div>
            {/snippet}
            <div class="space-y-4 p-6">
              <div class="flex items-center justify-between">
                <span class="text-sm text-surface-500">Deadline Status</span>
                <span
                  class="rounded px-2 py-0.5 text-xs font-bold"
                  class:bg-success-50={$goalView.forecast.on_track}
                  class:text-success-600={$goalView.forecast.on_track}
                  class:bg-error-50={!$goalView.forecast.on_track}
                  class:text-error-600={!$goalView.forecast.on_track}
                >
                  {$goalView.forecast.on_track ? 'ON TRACK' : 'OFF TRACK'}
                </span>
              </div>

              <div class="flex items-baseline justify-between border-t border-surface-100 pt-3">
                <span class="text-sm text-surface-500">Est. Target Value</span>
                <span class="text-lg font-bold text-surface-900">
                  {formatValue($goalView.forecast.predicted)}
                  {$goalView.metric_unit}
                </span>
              </div>

              <div class="flex justify-between text-xs text-surface-400">
                <span>80% Confidence Range</span>
                <span class="font-medium">
                  [{formatValue($goalView.forecast.ci_lower)} – {formatValue(
                    $goalView.forecast.ci_upper
                  )}]
                </span>
              </div>

              <div class="border-t border-surface-100 pt-3">
                <span class="mb-1 block text-xs font-semibold text-surface-400">Recommendation</span
                >
                <p class="text-xs leading-relaxed text-surface-600">
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
              <span class="text-sm font-semibold text-surface-900">Goal Parameters</span>
            </div>
          {/snippet}
          <div class="space-y-3 p-6 text-sm text-surface-600">
            <div class="flex justify-between">
              <span>Goal Type</span>
              <span class="font-medium text-surface-800 capitalize">{$goalView.frequency}</span>
            </div>
            <div class="flex justify-between">
              <span>Direction</span>
              <span class="font-medium text-surface-800 capitalize">{$goalView.direction}</span>
            </div>
            <div class="flex justify-between">
              <span>Metric</span>
              <span class="font-medium text-surface-800">{$goalView.metric_name}</span>
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
              <span class="text-sm font-semibold text-surface-900">Recent Contributions</span>
            </div>
            <a
              href="/entries/{$goalView.id}"
              class="text-xs font-semibold text-primary-600 hover:text-primary-700"
            >
              Manage Entries
            </a>
          </div>
        {/snippet}
        <div class="divide-y divide-surface-100">
          {#if $measurements.length === 0}
            <div class="p-6 text-center text-sm text-surface-400">
              No measurements logged for this metric yet.
            </div>
          {:else}
            {#each $measurements.slice(-5).reverse() as m}
              <div class="flex items-center justify-between px-6 py-3.5 hover:bg-surface-50">
                <div class="flex items-baseline gap-1">
                  <span class="text-sm font-bold text-surface-900">
                    {formatValue(m.value_numeric)}
                  </span>
                  <span class="text-xs text-surface-400">{$goalView.metric_unit}</span>
                </div>
                <div class="text-xs text-surface-400">
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
