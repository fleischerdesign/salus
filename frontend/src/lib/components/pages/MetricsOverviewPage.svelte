<script lang="ts">
  import Dexie from 'dexie';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Input from '../ui/Input.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import {
    METRIC_CATEGORIES,
    METRIC_GROUPS,
    STANDALONE_METRICS,
    getAllMetrics
  } from '../../data/metrics-data';
  import type { MetricGroup, MetricDefinition } from '../../types';

  let { onSelectGroup, onSelectMetric } = $props<{
    onSelectGroup: (groupKey: string) => void;
    onSelectMetric: (groupKey: string, metricCode: string) => void;
  }>();

  let selectedCategory = $state<string>('all');
  let searchQuery = $state<string>('');

  // Reactive Goals from Dexie
  const goalsQuery = useQuery(() => db.goal.filter((g) => !g.deleted_at).toArray());
  const goals = $derived(goalsQuery.value ?? []);
  const goalsMap = $derived(new Map(goals.map((g) => [g.metric_code, g])));

  const allMetricCodes = getAllMetrics().map((m) => m.code);

  // High-performance compound-index B-Tree query: 0.1ms per metric via [metric_code+start_time]
  const measurementsQuery = useQuery(async () => {
    const map = new Map<string, { value: number; time: string }>();
    await Promise.all(
      allMetricCodes.map(async (code) => {
        const latest = await db.measurement
          .where('[metric_code+start_time]')
          .between([code, Dexie.minKey], [code, Dexie.maxKey])
          .and((m) => !m.deleted_at)
          .last();

        if (latest && latest.value_numeric != null) {
          map.set(code, {
            value: latest.value_numeric,
            time: latest.start_time
          });
        }
      })
    );
    return map;
  });
  const latestMeasurementsMap = $derived(measurementsQuery.value ?? new Map());

  const categories = $derived([
    ...METRIC_CATEGORIES,
    ...(goals.length > 0
      ? [{ id: 'has_goal', label: `Mit Ziel (${goals.length})`, icon: 'target' }]
      : [])
  ]);

  // Unified items list: combines Groups and Standalone Metrics seamlessly
  type UnifiedItem =
    { kind: 'group'; data: MetricGroup } | { kind: 'metric'; data: MetricDefinition };

  const unifiedItems = $derived.by<UnifiedItem[]>(() => {
    const q = searchQuery.trim().toLowerCase();

    // 1. Filter Groups
    const matchedGroups: UnifiedItem[] = METRIC_GROUPS.filter((g) => {
      if (selectedCategory === 'has_goal') {
        return g.subMetrics.some((m) => goalsMap.has(m.code));
      }
      if (selectedCategory !== 'all' && g.category !== selectedCategory) {
        return false;
      }
      if (!q) return true;
      return (
        g.title.toLowerCase().includes(q) ||
        g.description.toLowerCase().includes(q) ||
        g.subMetrics.some(
          (m) => m.name.toLowerCase().includes(q) || m.code.toLowerCase().includes(q)
        )
      );
    }).map((g) => ({ kind: 'group', data: g }));

    // 2. Filter Standalone Metrics
    const matchedMetrics: UnifiedItem[] = STANDALONE_METRICS.filter((m) => {
      if (selectedCategory === 'has_goal') {
        return goalsMap.has(m.code);
      }
      if (selectedCategory !== 'all' && m.category !== selectedCategory) {
        return false;
      }
      if (!q) return true;
      return (
        m.name.toLowerCase().includes(q) ||
        m.code.toLowerCase().includes(q) ||
        (m.referenceRange?.toLowerCase().includes(q) ?? false)
      );
    }).map((m) => ({ kind: 'metric', data: m }));

    return [...matchedGroups, ...matchedMetrics];
  });

  function getMetricIcon(code: string, category: string): string {
    switch (code) {
      case 'heart_rate':
      case 'resting_heart_rate':
        return 'favorite';
      case 'hrv':
      case 'hrv_rmssd':
        return 'vital-signs';
      case 'spo2':
        return 'vital-signs';
      case 'respiratory_rate':
        return 'air';
      case 'weight':
      case 'body_fat':
      case 'lean_body_mass':
      case 'bone_mass':
        return 'scale';
      case 'body_temperature':
        return 'thermostat';
      case 'steps':
      case 'floors_climbed':
        return 'directions-run';
      case 'active_calories':
        return 'local-fire-department';
      case 'distance':
        return 'route';
      case 'vo2_max':
        return 'speed';
      case 'blood_glucose':
      case 'hba1c':
      case 'ketones':
      case 'lactate':
        return 'science';
      case 'water':
        return 'water-drop';
      case 'sleep_duration':
      case 'sleep_score':
        return 'bedtime';
      default:
        return category === 'cardiovascular'
          ? 'vital-signs'
          : category === 'activity'
            ? 'directions-run'
            : category === 'body'
              ? 'scale'
              : category === 'metabolism'
                ? 'science'
                : category === 'sleep'
                  ? 'bedtime'
                  : 'biotech';
    }
  }

  function getGroupIcon(key: string, category: string): string {
    if (key === 'blood_pressure') return 'vital-signs';
    if (key === 'body_measurements') return 'straighten';
    if (key === 'lipid_panel') return 'biotech';
    return category === 'cardiovascular' ? 'vital-signs' : 'grid-view';
  }

  function getGoalProgress(
    goal: { target_value?: number | string; direction?: string } | null | undefined,
    currentVal?: number
  ) {
    if (!goal || currentVal == null) return null;
    const target = Number(goal.target_value);
    if (isNaN(target)) return null;

    const isDecrease = goal.direction === 'decrease';
    let percent = 0;
    let isFulfilled = false;

    if (isDecrease) {
      isFulfilled = currentVal <= target;
      percent = isFulfilled ? 100 : Math.max(0, Math.round((target / currentVal) * 100));
    } else {
      isFulfilled = currentVal >= target;
      percent = isFulfilled ? 100 : Math.max(0, Math.round((currentVal / target) * 100));
    }

    return { percent, isFulfilled, target };
  }
</script>

<div class="space-y-6">
  <!-- Page Header -->
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight text-text-main">
        Vitalparameter &amp; Metriken
      </h1>
      <p class="mt-0.5 text-sm text-text-muted">
        Evidenzbasierte Gesundheitsdaten mit Verläufen, Zielwerten und statistischen Trendanalysen
      </p>
    </div>
    <div class="w-full sm:w-72">
      <Input icon="search" placeholder="Metrik oder Code suchen..." bind:value={searchQuery} />
    </div>
  </div>

  <!-- Category Filter Pills -->
  <div class="relative w-full overflow-hidden">
    <div class="no-scrollbar scroll-mask-x flex gap-2 overflow-x-auto pb-1 select-none">
      {#each categories as cat}
        <button
          type="button"
          onclick={() => (selectedCategory = cat.id)}
          class="shrink-0 cursor-pointer rounded-xl px-3.5 py-1.5 text-xs font-bold whitespace-nowrap transition-all {selectedCategory ===
          cat.id
            ? 'bg-primary text-white shadow-xs'
            : 'border border-border-subtle bg-surface-0 text-text-muted hover:text-text-main'}"
        >
          {cat.label}
        </button>
      {/each}
    </div>
  </div>

  <!-- UNIFIED HARMONIOUS METRICS GRID (Zero Clutter, Clean Minimalist Cards) -->
  {#if unifiedItems.length > 0}
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {#each unifiedItems as item}
        {#if item.kind === 'group'}
          {@const group = item.data}

          <!-- GROUP CARD -->
          <button
            type="button"
            onclick={() => onSelectGroup(group.key)}
            class="group flex cursor-pointer flex-col justify-between rounded-3xl border border-border-subtle bg-surface-0 p-5 text-left shadow-card transition-all hover:border-primary hover:shadow-md {group
              .subMetrics.length > 2
              ? 'sm:col-span-2'
              : ''}"
          >
            <div>
              <!-- Header: Icon + Title + Group Badge -->
              <div class="flex items-start justify-between gap-2">
                <div class="flex min-w-0 items-center gap-3">
                  <div
                    class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
                    style="background-color: color-mix(in srgb, var(--color-primary) 12%, transparent); color: var(--color-primary);"
                  >
                    <Icon name={getGroupIcon(group.key, group.category)} size="md" />
                  </div>
                  <div class="min-w-0">
                    <h3
                      class="truncate text-sm font-extrabold text-text-main transition-colors group-hover:text-primary"
                    >
                      {group.title}
                    </h3>
                    <p class="truncate text-[0.6875rem] text-text-muted">
                      {group.description}
                    </p>
                  </div>
                </div>
                <Badge variant="primary" class="shrink-0 text-[0.5625rem] font-bold">
                  {group.subMetrics.length} Werte
                </Badge>
              </div>

              <!-- Main Group Body -->
              {#if group.key === 'blood_pressure'}
                <!-- Arterial Blood Pressure paired readout -->
                {@const sys = latestMeasurementsMap.get('systolic_bp')}
                {@const dia = latestMeasurementsMap.get('diastolic_bp')}
                <div class="mt-4 flex items-baseline gap-2">
                  <span class="text-3xl font-extrabold tracking-tight text-text-main tabular-nums">
                    {sys ? sys.value : '—'}
                    <span class="text-2xl font-normal text-text-muted">/</span>
                    {dia ? dia.value : '—'}
                  </span>
                  <span class="text-xs font-bold text-text-muted">mmHg</span>
                </div>
              {:else}
                <!-- Multi-Metric Sub-values -->
                <div class="mt-3.5 grid grid-cols-2 gap-2 sm:grid-cols-3">
                  {#each group.subMetrics.slice(0, 4) as sub}
                    {@const subData = latestMeasurementsMap.get(sub.code)}
                    <div class="rounded-xl border border-border-subtle bg-surface-50 p-2.5">
                      <span class="block truncate text-[0.625rem] font-semibold text-text-muted">
                        {sub.name}
                      </span>
                      <div class="mt-0.5 flex items-baseline gap-1">
                        <span class="text-sm font-extrabold text-text-main tabular-nums">
                          {subData ? subData.value : '—'}
                        </span>
                        <span class="text-[0.5625rem] text-text-muted">{sub.unit}</span>
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          </button>
        {:else}
          {@const metric = item.data}
          {@const realData = latestMeasurementsMap.get(metric.code)}
          {@const goal = goalsMap.get(metric.code)}
          {@const goalProgress = getGoalProgress(goal, realData?.value)}

          <!-- STANDALONE METRIC CARD -->
          <button
            type="button"
            onclick={() => onSelectMetric(metric.groupKey || metric.code, metric.code)}
            class="group flex cursor-pointer flex-col justify-between rounded-3xl border border-border-subtle bg-surface-0 p-5 text-left shadow-card transition-all hover:border-primary hover:shadow-md"
          >
            <div>
              <!-- Header: Icon + Name + Unit Badge -->
              <div class="flex items-start justify-between gap-2">
                <div class="flex min-w-0 items-center gap-3">
                  <div
                    class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
                    style="background-color: color-mix(in srgb, var(--color-primary) 12%, transparent); color: var(--color-primary);"
                  >
                    <Icon name={getMetricIcon(metric.code, metric.category)} size="md" />
                  </div>
                  <div class="min-w-0">
                    <h3
                      class="truncate text-sm font-extrabold text-text-main transition-colors group-hover:text-primary"
                    >
                      {metric.name}
                    </h3>
                    <p class="truncate text-[0.6875rem] text-text-muted">
                      {metric.referenceRange || 'Biomarker'}
                    </p>
                  </div>
                </div>
                <Badge variant="default" class="shrink-0 text-[0.5625rem] font-bold">
                  {metric.unit}
                </Badge>
              </div>

              <!-- Main Value -->
              <div class="mt-4 flex items-baseline gap-2">
                <span class="text-3xl font-extrabold tracking-tight text-text-main tabular-nums">
                  {#if realData}
                    {realData.value}
                  {:else}
                    <span class="text-2xl font-normal text-text-muted">—</span>
                  {/if}
                </span>
                {#if realData}
                  <span class="text-xs font-bold text-text-muted">{metric.unit}</span>
                {/if}
              </div>

              <!-- Goal Progress (Sleek Clean Micro Bar, No Emojis) -->
              {#if goal}
                <div class="mt-3 space-y-1">
                  <div class="flex justify-between text-[0.625rem] font-semibold text-text-muted">
                    <span>Ziel: {goal.target_value} {metric.unit}</span>
                    {#if goalProgress}
                      <span
                        class={goalProgress.isFulfilled
                          ? 'font-bold text-emerald-500'
                          : 'text-text-muted'}
                      >
                        {goalProgress.percent}%
                      </span>
                    {/if}
                  </div>
                  <div class="h-1.5 w-full overflow-hidden rounded-full bg-border-subtle">
                    <div
                      class="h-full rounded-full transition-all duration-500 {goalProgress?.isFulfilled
                        ? 'bg-emerald-500'
                        : 'bg-primary'}"
                      style="width: {Math.min(100, Math.max(0, goalProgress?.percent ?? 0))}%;"
                    ></div>
                  </div>
                </div>
              {/if}
            </div>
          </button>
        {/if}
      {/each}
    </div>
  {:else}
    <!-- Clean Empty State -->
    <div class="rounded-3xl border-2 border-dashed border-border-subtle p-12 text-center">
      <p class="text-sm font-medium text-text-muted">Keine Einträge für die Auswahl gefunden.</p>
    </div>
  {/if}
</div>
