<script lang="ts">
  import {
    useAnalytics,
    useCorrelations,
    useSleepDebt,
    useTrend,
    useWellness
  } from '$lib/analytics/views/analytics';
  import Card from '$components/ui/Card.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ListItem from '$components/ui/ListItem.svelte';
  import SegmentedControl from '$components/ui/SegmentedControl.svelte';
  import LineChart from '$components/dashboard/LineChart.svelte';
  import VizBar from '$components/dashboard/VizBar.svelte';
  import CalendarHeatmap from '$components/dashboard/CalendarHeatmap.svelte';
  import CorrelationMatrix from '$components/dashboard/CorrelationMatrix.svelte';
  import MethodologyBadge from '$components/ui/MethodologyBadge.svelte';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  let tab = $state('trends');
  let range = $state('30d');

  const tabs = [
    { value: 'trends', label: 'Trends' },
    { value: 'forecast', label: 'Forecast Lab' },
    { value: 'deep', label: 'Deep Analysis' }
  ];
  const ranges = [
    { value: '7d', label: '7D' },
    { value: '30d', label: '30D' },
    { value: '90d', label: '90D' },
    { value: '1y', label: '1Y' }
  ];

  let data = $derived(useAnalytics(range));
  let correlations = $derived(useCorrelations('90d'));
  let weightTrend = $derived(useTrend('weight', range));
  let hrTrend = $derived(useTrend('heart_rate', range));
  let sleepDebt = $derived(useSleepDebt(30));
  let wellness = $derived(useWellness());

  function formatDuration(seconds: number): string {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return h > 0 ? `${h}h ${m}min` : `${m}min`;
  }

  let hasWeightData = $derived(($data?.weight_data?.length ?? 0) > 0);
  let hasStepsData = $derived(($data?.steps_data ?? []).some((v: number) => v > 0));

  let chartSeries = $derived.by(() => {
    if (!data) return [];
    const s: { label: string; data: number[]; color: string; yAxis: 'left' | 'right' }[] = [];
    if (hasWeightData) {
      s.push({
        label: 'Weight (kg)',
        data: $data!.weight_data,
        color: 'var(--color-primary-500)',
        yAxis: 'left'
      });
    }
    if (hasStepsData) {
      s.push({
        label: 'Steps',
        data: $data!.steps_data,
        color: 'var(--color-success-500)',
        yAxis: 'right'
      });
    }
    return s;
  });
</script>

<svelte:head><title>Salus — Analytics</title></svelte:head>

<div class="space-y-4">
  <div class="flex items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-semibold text-surface-900">Analytics</h1>
      <p class="text-sm text-surface-500">
        {tab === 'trends'
          ? 'Statistical time series with regression analysis'
          : tab === 'forecast'
            ? 'Predictions, projections & sleep debt'
            : 'Cross-metric correlations & historical calendar'}
      </p>
    </div>
    <SegmentedControl options={ranges} bind:value={range} />
  </div>

  <div class="flex items-center gap-2">
    <SegmentedControl options={tabs} bind:value={tab} />
  </div>

  {#if !$data}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if tab === 'trends'}
    <div class="grid gap-4 lg:grid-cols-12">
      <Card padding={false} class="lg:col-span-8">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="monitoring" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Weight & Activity Trends</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $weightTrend && (hasWeightData || hasStepsData)}
            {#if $weightTrend.regression}
              <div class="mb-2">
                <MethodologyBadge
                  n={$weightTrend.regression.n}
                  method="OLS Regression"
                  citation={{ text: 'Kutner et al., Ch. 1' }}
                />
              </div>
            {/if}
            <LineChart
              labels={$data.weight_labels.length > 0 ? $data.weight_labels : $data.steps_labels}
              series={chartSeries}
              leftUnit="kg"
              rightUnit="steps"
              regressionLine={$weightTrend.regression?.points ?? null}
              regressionCI={$weightTrend.regression?.ci ?? null}
            />
          {:else}
            <div class="flex h-[280px] items-center justify-center">
              <p class="text-sm text-surface-400">No trend data available.</p>
            </div>
          {/if}
        </div>
      </Card>

      <Card padding={false} class="lg:col-span-4">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="whatshot" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Metabolic Baseline</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $data.tdee}
            <div class="mb-3">
              <MethodologyBadge
                n={$data.weight_trend.points.length}
                method="Cunningham BMR + HRR PAL"
                citation={{ text: 'Cunningham 1991; Tanaka 2001; Brage 2005' }}
              />
            </div>
            <Stat value={$data.tdee.tdee_kcal.toFixed(0)} unit="kcal/day" label="TDEE" />
            <div class="mt-4 space-y-1.5 text-sm text-surface-500">
              <div class="flex justify-between">
                <span>BMR (Cunningham)</span><span class="font-medium text-surface-700"
                  >{$data.tdee.bmr_kcal.toFixed(0)} kcal</span
                >
              </div>
              <div class="flex justify-between">
                <span>Activity Factor</span><span class="font-medium text-surface-700"
                  >{$data.tdee.pal_factor.toFixed(2)}x</span
                >
              </div>
              <div class="flex justify-between">
                <span>HRR Utilisation</span><span class="font-medium text-surface-700"
                  >{($data.tdee.hrr_pct * 100).toFixed(0)}%</span
                >
              </div>
            </div>
            {#if $data.weight_trend.current}
              <div
                class="mt-3 flex justify-between border-t border-surface-100 pt-3 text-sm text-surface-500"
              >
                <span>Current Weight</span><span class="font-medium text-surface-700"
                  >{$data.weight_trend.current.toFixed(1)} kg</span
                >
              </div>
            {/if}
          {:else}
            <p class="text-sm text-surface-400">No weight data available for TDEE calculation.</p>
          {/if}
        </div>
      </Card>

      <Card padding={false} class="lg:col-span-full">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="ecg_heart" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Resting Heart Rate Trend</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $hrTrend && $hrTrend.regression}
            <div class="mb-2">
              <MethodologyBadge
                n={$hrTrend.regression.n}
                p={0.05}
                method="OLS Regression + Mann-Kendall"
                citation={{ text: 'Mann 1945; Kendall 1975' }}
              />
            </div>
            <LineChart
              labels={$hrTrend.labels}
              series={[
                {
                  label: 'Resting HR (bpm)',
                  data: $hrTrend.values,
                  color: 'var(--color-error-500)',
                  yAxis: 'left'
                }
              ]}
              leftUnit="bpm"
              regressionLine={$hrTrend.regression.points}
              regressionCI={$hrTrend.regression.ci}
            />
          {:else}
            <div class="flex h-[220px] items-center justify-center">
              <p class="text-sm text-surface-400">
                Insufficient heart rate data for trend analysis.
              </p>
            </div>
          {/if}
        </div>
      </Card>

      <Card padding={false} class="lg:col-span-6">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="bedtime" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Sleep Duration Trend</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $data.sleep_list.length >= 3}
            <LineChart
              labels={$data.sleep_list.map((s: { date: string }) => s.date)}
              series={[
                {
                  label: 'Sleep (hours)',
                  data: $data.sleep_list.map((s: { duration_hours: number }) => s.duration_hours),
                  color: 'var(--color-primary-500)',
                  yAxis: 'left'
                }
              ]}
              leftUnit="h"
            />
          {:else}
            <div class="flex h-[220px] items-center justify-center">
              <p class="text-sm text-surface-400">Insufficient sleep data.</p>
            </div>
          {/if}
        </div>
      </Card>

      <Card padding={false} class="lg:col-span-6">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="exercise" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Exercise History</span>
          </div>
        {/snippet}
        <div class="p-2">
          {#if $data.exercise_sessions.length > 0}
            <div class="divide-y divide-surface-100">
              {#each $data.exercise_sessions as session, i}
                <div in:fade={{ ...staggerFade(i) }}>
                  <ListItem
                    primary={session.type_name}
                    secondary={`${session.date} ${session.time}`}
                  >
                    {#snippet children()}
                      <div class="flex min-w-0 flex-1 items-center justify-between gap-3">
                        <div class="min-w-0">
                          <p class="truncate text-sm font-medium text-surface-900">
                            {session.type_name}
                          </p>
                          <p class="mt-0.5 truncate text-xs text-surface-500">
                            {session.date}
                            {session.time}
                            {#if session.distance_meters > 0}
                              · {(session.distance_meters / 1000).toFixed(1)}km{/if}
                            {#if session.calories > 0}
                              · {session.calories.toFixed(0)} kcal{/if}
                          </p>
                        </div>
                        <span class="flex-shrink-0 text-sm text-surface-500"
                          >{formatDuration(session.duration_seconds)}</span
                        >
                      </div>
                    {/snippet}
                  </ListItem>
                </div>
              {/each}
            </div>
          {:else}
            <div class="px-4 py-8">
              <p class="text-sm text-surface-400">No exercise sessions recorded.</p>
            </div>
          {/if}
        </div>
      </Card>
    </div>
  {:else if tab === 'forecast'}
    <div class="grid gap-4 lg:grid-cols-12">
      <Card padding={false} class="lg:col-span-full">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="trending_up" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Weight Forecast</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $weightTrend && $weightTrend.regression}
            <div class="mb-2">
              <MethodologyBadge
                n={$weightTrend.regression.n}
                method="OLS + 95% PI"
                citation={{ text: 'Kutner et al., §2.4' }}
              />
            </div>
            <LineChart
              labels={$weightTrend.labels}
              series={[
                {
                  label: 'Weight (kg)',
                  data: $weightTrend.values,
                  color: 'var(--color-primary-500)',
                  yAxis: 'left'
                }
              ]}
              leftUnit="kg"
              regressionLine={$weightTrend.regression.points}
              regressionCI={$weightTrend.regression.ci}
            />
            <div class="mt-2 text-center text-xs text-surface-400">
              r² = {$weightTrend.regression.r_squared.toFixed(3)} · n = {$weightTrend.regression.n}
            </div>
          {:else}
            <div class="flex h-[280px] items-center justify-center">
              <p class="text-sm text-surface-400">
                Insufficient data for weight forecasting (need ≥3 points).
              </p>
            </div>
          {/if}
        </div>
      </Card>

      <Card padding={false} class="lg:col-span-6">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="whatshot" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Metabolic Baseline</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $data.tdee}
            <Stat value={$data.tdee.tdee_kcal.toFixed(0)} unit="kcal/day" label="TDEE" />
            <div class="mt-4 space-y-1.5 text-sm text-surface-500">
              <div class="flex justify-between">
                <span>BMR</span><span class="font-medium text-surface-700"
                  >{$data.tdee.bmr_kcal.toFixed(0)} kcal</span
                >
              </div>
              <div class="flex justify-between">
                <span>Activity Factor</span><span class="font-medium text-surface-700"
                  >{$data.tdee.pal_factor.toFixed(2)}x</span
                >
              </div>
              <div class="flex justify-between">
                <span>HRR</span><span class="font-medium text-surface-700"
                  >{($data.tdee.hrr_pct * 100).toFixed(0)}%</span
                >
              </div>
            </div>
          {:else}
            <p class="text-sm text-surface-400">No TDEE data.</p>
          {/if}
        </div>
      </Card>

      <Card padding={false} class="lg:col-span-6">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="hotel" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Sleep Debt</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $sleepDebt}
            <div class="mb-3">
              <MethodologyBadge
                n={$sleepDebt.debt.length}
                method="Cumulative Sleep Debt"
                citation={{
                  text: 'Hirshkowitz et al. 2015, NSF recommendations',
                  doi: '10.1016/j.sleep.2014.07.014'
                }}
              />
            </div>
            <Stat
              value="{$sleepDebt.cumulative_last > 0 ? '+' : ''}{$sleepDebt.cumulative_last.toFixed(
                1
              )}h"
              label="28-Day Cumulative"
              unit={$sleepDebt.cumulative_last > 0 ? 'deficit' : 'surplus'}
            />
            <div class="mt-4">
              <VizBar
                segments={$sleepDebt.debt.slice(-7).map((v: number) => ({
                  label: '',
                  value: Math.abs(v),
                  color: v > 0 ? 'var(--color-error-400)' : 'var(--color-success-400)'
                }))}
                total={Math.max(...$sleepDebt.debt.map((v: number) => Math.abs(v)), 1)}
                showLegend={false}
              />
            </div>
          {:else}
            <p class="text-sm text-surface-400">Insufficient sleep data for debt calculation.</p>
          {/if}
        </div>
      </Card>

      <Card padding={false} class="lg:col-span-full">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="vital_signs" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Recovery Score</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $wellness}
            <div class="mb-3">
              <MethodologyBadge
                n={28}
                method="z-Score Composite"
                citation={{ text: 'Plews et al. 2013 (heuristic weights)', doi: '10.1152/japplphysiol.00770.2013' }}
              />
            </div>
            <div class="flex items-center gap-6">
              <div class="text-center">
                <div class="flex h-24 w-24 items-center justify-center rounded-full border-4"
                  style="border-color:{$wellness.score >= 75 ? 'var(--color-success-400)' : $wellness.score >= 50 ? 'var(--color-warning-400)' : 'var(--color-error-400)'}"
                >
                  <span class="text-2xl font-bold text-surface-900">{$wellness.score.toFixed(0)}</span>
                </div>
                <p class="mt-1 text-xs font-medium text-surface-600 capitalize">{$wellness.interpretation}</p>
              </div>
              <div class="grid flex-1 grid-cols-4 gap-3 text-center text-xs">
                <div><div class="font-mono text-surface-800">{$wellness.sleep_z.toFixed(1)}</div><div class="text-surface-400">Sleep z</div></div>
                <div><div class="font-mono text-surface-800">{$wellness.hrv_z.toFixed(1)}</div><div class="text-surface-400">HRV z</div></div>
                <div><div class="font-mono text-surface-800">{$wellness.hr_z.toFixed(1)}</div><div class="text-surface-400">HR z</div></div>
                <div><div class="font-mono text-surface-800">{$wellness.steps_z.toFixed(1)}</div><div class="text-surface-400">Steps z</div></div>
              </div>
            </div>
          {:else}
            <p class="text-sm text-surface-400">Insufficient data for recovery scoring (need 28 days).</p>
          {/if}
        </div>
      </Card>

      <Card padding={false} class="lg:col-span-full">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="ecg_heart" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Resting HR Forecast</span>>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $hrTrend && $hrTrend.regression}
            <LineChart
              labels={$hrTrend.labels}
              series={[
                {
                  label: 'Resting HR (bpm)',
                  data: $hrTrend.values,
                  color: 'var(--color-error-500)',
                  yAxis: 'left'
                }
              ]}
              leftUnit="bpm"
              regressionLine={$hrTrend.regression.points}
              regressionCI={$hrTrend.regression.ci}
            />
            <div class="mt-2 text-center text-xs text-surface-400">
              r² = {$hrTrend.regression.r_squared.toFixed(3)} · n = {$hrTrend.regression.n}
            </div>
          {:else}
            <div class="flex h-[220px] items-center justify-center">
              <p class="text-sm text-surface-400">Insufficient heart rate data.</p>
            </div>
          {/if}
        </div>
      </Card>
    </div>
  {:else}
    <div class="grid gap-4 lg:grid-cols-12">
      <Card padding={false} class="lg:col-span-full">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="calendar_month" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Activity Calendar</span>
          </div>
        {/snippet}
        <div class="p-4"><CalendarHeatmap metric="steps" /></div>
      </Card>

      {#if $correlations && $correlations.pairs.length > 0}
        <Card padding={false} class="lg:col-span-full">
          {#snippet header()}
            <div class="flex items-center gap-2">
              <Icon name="hub" size="sm" class="text-surface-400" />
              <span class="text-sm font-semibold text-surface-900">Cross-Metric Correlations</span>
            </div>
          {/snippet}
          <div class="p-4">
            <CorrelationMatrix
              pairs={$correlations.pairs}
              nComparisons={$correlations.n_comparisons}
              correction={$correlations.correction}
            />
          </div>
        </Card>
      {/if}
    </div>
  {/if}
</div>
