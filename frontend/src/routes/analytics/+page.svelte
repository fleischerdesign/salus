<script lang="ts">
  import { liveQuery } from 'dexie';
  import { fetchAnalytics } from '$lib/analytics/views/analytics';
  import Card from '$components/ui/Card.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ListItem from '$components/ui/ListItem.svelte';
  import SegmentedControl from '$components/ui/SegmentedControl.svelte';
  import LineChart from '$components/dashboard/LineChart.svelte';
  import VizBar from '$components/dashboard/VizBar.svelte';

  let range = $state('30d');

  const ranges = [
    { value: '7d', label: '7D' },
    { value: '30d', label: '30D' },
    { value: '90d', label: '90D' },
    { value: '1y', label: '1Y' },
  ];

  let data = liveQuery(() => fetchAnalytics(range));

  function formatDuration(seconds: number): string {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return h > 0 ? `${h}h ${m}min` : `${m}min`;
  }

  let hasWeightData = $derived(($data?.weight_data?.length ?? 0) > 0);
  let hasStepsData = $derived(($data?.steps_data ?? []).some((v: number) => v > 0));
  let hasAnyTrendData = $derived(hasWeightData || hasStepsData);

  let chartSeries = $derived.by(() => {
    if (!data) return [];
    const s: { label: string; data: number[]; color: string; yAxis: 'left' | 'right' }[] = [];
    if (hasWeightData) {
      s.push({ label: 'Weight (kg)', data: $data!.weight_data, color: 'var(--color-primary-500)', yAxis: 'left' });
    }
    if (hasStepsData) {
      s.push({ label: 'Steps', data: $data!.steps_data, color: 'var(--color-success-500)', yAxis: 'right' });
    }
    return s;
  });
</script>

<svelte:head><title>Salus — Analytics</title></svelte:head>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-semibold text-surface-900">Analytics</h1>
      <p class="text-sm text-surface-500">Metabolic & Activity Trends</p>
    </div>
    <SegmentedControl options={ranges} bind:value={range} />
  </div>

  {#if !$data}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else}
    <div class="grid gap-4 lg:grid-cols-12">
      <Card padding={false} class="lg:col-span-8">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="monitoring" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Physiological Trends</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if hasAnyTrendData}
            <LineChart
              labels={$data.weight_labels.length > 0 ? $data.weight_labels : $data.steps_labels}
              series={chartSeries}
              leftUnit="kg"
              rightUnit="steps"
            />
          {:else}
            <div class="flex h-[280px] items-center justify-center">
              <p class="text-sm text-surface-400">No trend data available for this range.</p>
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
            <Stat value={$data.tdee.tdee_kcal.toFixed(0)} unit="kcal/day" label="TDEE" />
            <div class="mt-4 space-y-1.5 text-sm text-surface-500">
              <div class="flex justify-between"><span>BMR (Cunningham)</span><span class="font-medium text-surface-700">{$data.tdee.bmr_kcal.toFixed(0)} kcal</span></div>
              <div class="flex justify-between"><span>Activity Factor</span><span class="font-medium text-surface-700">{$data.tdee.pal_factor.toFixed(2)}x</span></div>
              <div class="flex justify-between"><span>HRR Utilization</span><span class="font-medium text-surface-700">{($data.tdee.hrr_pct * 100).toFixed(0)}%</span></div>
            </div>
            {#if $data.weight_trend.current}
              <div class="mt-3 flex justify-between border-t border-surface-100 pt-3 text-sm text-surface-500">
                <span>Current Weight</span><span class="font-medium text-surface-700">{$data.weight_trend.current.toFixed(1)} kg</span>
              </div>
            {/if}
          {:else}
            <p class="text-sm text-surface-400">No weight data available for TDEE calculation.</p>
          {/if}
        </div>
      </Card>

      <Card padding={false} class="lg:col-span-6">
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="bedtime" size="sm" class="text-surface-400" />
            <span class="text-sm font-semibold text-surface-900">Sleep Analysis</span>
          </div>
        {/snippet}
        <div class="p-6">
          {#if $data.latest_sleep}
            <Stat value={`${$data.latest_sleep.duration_hours.toFixed(1)}h`} label="Latest Sleep Duration" />
            <div class="mt-4">
              <VizBar
                segments={[
                  { label: 'Awake', value: $data.latest_sleep.awake_pct, color: 'var(--color-warning-400)' },
                  { label: 'Light', value: $data.latest_sleep.light_pct, color: 'var(--color-primary-300)' },
                  { label: 'Deep', value: $data.latest_sleep.deep_pct, color: 'var(--color-primary-500)' },
                  { label: 'REM', value: $data.latest_sleep.rem_pct, color: 'var(--color-success-400)' },
                ]}
                total={100}
              />
            </div>
          {:else}
            <p class="text-sm text-surface-400">No sleep data available.</p>
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
              {#each $data.exercise_sessions as session}
                <ListItem primary={session.type_name} secondary={`${session.date} ${session.time}`}>
                  {#snippet children()}
                    <div class="flex min-w-0 flex-1 items-center justify-between gap-3">
                      <div class="min-w-0">
                        <p class="truncate text-sm font-medium text-surface-900">{session.type_name}</p>
                        <p class="mt-0.5 truncate text-xs text-surface-500">
                          {session.date} {session.time}
                          {#if session.distance_meters > 0} · {(session.distance_meters / 1000).toFixed(1)}km{/if}
                          {#if session.calories > 0} · {session.calories.toFixed(0)} kcal{/if}
                        </p>
                      </div>
                      <span class="flex-shrink-0 text-sm text-surface-500">{formatDuration(session.duration_seconds)}</span>
                    </div>
                  {/snippet}
                </ListItem>
              {/each}
            </div>
          {:else}
            <div class="px-4 py-8"><p class="text-sm text-surface-400">No exercise sessions recorded.</p></div>
          {/if}
        </div>
      </Card>
    </div>
  {/if}
</div>
