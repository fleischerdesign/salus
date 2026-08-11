<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { getSourceStats } from '$lib/db/metric-stats';
  import type { MetricDefinition, UserSourcePreference } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import SearchInput from '$components/ui/SearchInput.svelte';
  import Select from '$components/ui/Select.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import SourcePriorityCard from '$components/forms/SourcePriorityCard.svelte';
  import SourceDetailsModal from '$components/forms/SourceDetailsModal.svelte';
  import { updateSourcePreferences } from '$lib/mutations/misc';

  let loading = $state(true);
  let sourceSearchQuery = $state('');
  let matrixSearchQuery = $state('');
  let selectedCategory = $state('all');
  let sourceModalOpen = $state(false);
  let selectedSource = $state<{ id: string; name: string; icon: string; color: string } | null>(
    null
  );

  let metrics = $state<MetricDefinition[]>([]);
  let preferencesMap = $state<Record<string, UserSourcePreference[]>>({});
  let sourceCounts = $state<Record<string, number>>({});
  let metricKnownSources = $state<Record<string, string[]>>({});
  let savingMetric = $state<string | null>(null);

  const CATEGORY_OPTIONS = [
    { value: 'all', label: 'All Categories' },
    { value: 'sleep', label: 'Sleep & Recovery' },
    { value: 'cardio', label: 'Cardiovascular' },
    { value: 'activity', label: 'Activity & Sports' },
    { value: 'body', label: 'Body Metrics' }
  ];

  const KNOWN_SOURCES = [
    { id: 'health_connect', name: 'Android Health Connect', icon: 'smartphone', color: '#3ddc84' },
    { id: 'apple_health', name: 'Apple Health', icon: 'favorite', color: '#ff2d55' },
    { id: 'samsung_health', name: 'Samsung Health', icon: 'health-and-safety', color: '#1428a0' },
    { id: 'oura', name: 'Oura Ring', icon: 'bedtime', color: '#1f2937' },
    { id: 'garmin', name: 'Garmin Connect', icon: 'watch', color: '#007cc3' },
    { id: 'manual', name: 'Manual Input', icon: 'edit', color: '#4f46e5' },
    { id: 'seed', name: 'Dev Seed Data', icon: 'database', color: '#8b5cf6' }
  ];

  $effect(() => {
    loading = true;
    const sub = liveQuery(async () => {
      const allMetrics = await db.metric_definition.toArray();
      const allPrefs = await db.user_source_preference.toArray();
      const srcStats = await getSourceStats();

      const counts: Record<string, number> = {};
      const knownPerMetric: Record<string, Set<string>> = {};

      for (const src of KNOWN_SOURCES) {
        counts[src.id] = srcStats[src.id]?.entry_count ?? 0;
      }

      allPrefs.forEach((p) => {
        if (p.metric_code && p.source) {
          if (!knownPerMetric[p.metric_code]) {
            knownPerMetric[p.metric_code] = new Set();
          }
          knownPerMetric[p.metric_code].add(p.source);
        }
      });

      const prefGrouped: Record<string, UserSourcePreference[]> = {};
      allPrefs.forEach((p) => {
        if (!prefGrouped[p.metric_code]) {
          prefGrouped[p.metric_code] = [];
        }
        prefGrouped[p.metric_code].push(p);
      });

      Object.keys(prefGrouped).forEach((code) => {
        prefGrouped[code].sort((a, b) => a.priority_rank - b.priority_rank);
      });

      const knownConverted: Record<string, string[]> = {};
      Object.keys(knownPerMetric).forEach((code) => {
        knownConverted[code] = Array.from(knownPerMetric[code]);
      });

      return {
        allMetrics: allMetrics.sort((a, b) => a.name.localeCompare(b.name)),
        prefGrouped,
        counts,
        knownConverted
      };
    }).subscribe((val) => {
      if (val) {
        metrics = val.allMetrics;
        preferencesMap = val.prefGrouped;
        sourceCounts = val.counts;
        metricKnownSources = val.knownConverted;
      }
      loading = false;
    });

    return () => sub.unsubscribe();
  });

  let sortedAndFilteredSources = $derived.by(() => {
    const query = sourceSearchQuery.trim().toLowerCase();
    let sources = KNOWN_SOURCES.filter((s) => {
      if (!query) return true;
      return s.name.toLowerCase().includes(query) || s.id.toLowerCase().includes(query);
    });

    return sources.sort((a, b) => {
      const countA = sourceCounts[a.id] ?? 0;
      const countB = sourceCounts[b.id] ?? 0;
      const activeA = countA > 0 ? 1 : 0;
      const activeB = countB > 0 ? 1 : 0;

      if (activeA !== activeB) return activeB - activeA;
      if (countA !== countB) return countB - countA;
      return a.name.localeCompare(b.name);
    });
  });

  function matchesCategory(metricCode: string, category: string): boolean {
    if (category === 'all') return true;
    const code = metricCode.toLowerCase();
    if (category === 'sleep')
      return (
        code.includes('sleep') ||
        code.includes('hrv') ||
        code.includes('temp') ||
        code.includes('recovery')
      );
    if (category === 'cardio')
      return (
        code.includes('heart') ||
        code.includes('pulse') ||
        code.includes('bp') ||
        code.includes('systolic') ||
        code.includes('diastolic')
      );
    if (category === 'activity')
      return (
        code.includes('step') ||
        code.includes('calorie') ||
        code.includes('distance') ||
        code.includes('workout') ||
        code.includes('active')
      );
    if (category === 'body')
      return (
        code.includes('weight') ||
        code.includes('fat') ||
        code.includes('bmi') ||
        code.includes('muscle')
      );
    return true;
  }

  function getMetricItems(metricCode: string): UserSourcePreference[] {
    const existing = preferencesMap[metricCode] ?? [];
    const existingSources = new Set(existing.map((p) => p.source));
    const known = metricKnownSources[metricCode] ?? [];

    const items = [...existing];
    let nextRank = items.length + 1;
    for (const k of known) {
      if (!existingSources.has(k)) {
        items.push({
          id: `temp-${k}`,
          user_id: '',
          metric_code: metricCode,
          source: k,
          priority_rank: nextRank++,
          is_enabled: true,
          created_at: new Date().toISOString()
        });
      }
    }
    return items.sort((a, b) => a.priority_rank - b.priority_rank);
  }

  // Priority Matrix ONLY shows metrics with 2+ sources (where priority conflicts actually exist!)
  let filteredMatrixMetrics = $derived.by(() => {
    const query = matrixSearchQuery.trim().toLowerCase();
    return metrics.filter((m) => {
      const items = getMetricItems(m.code);
      if (items.length < 2) return false;

      const matchesSearch =
        !query || m.name.toLowerCase().includes(query) || m.code.toLowerCase().includes(query);
      const matchesCat = matchesCategory(m.code, selectedCategory);
      return matchesSearch && matchesCat;
    });
  });

  async function handleMetricUpdate(metricCode: string, items: UserSourcePreference[]) {
    preferencesMap[metricCode] = items;
    savingMetric = metricCode;
    try {
      const payload = items.map((p, idx) => ({
        source: p.source,
        priority_rank: idx + 1,
        is_enabled: p.is_enabled
      }));
      await updateSourcePreferences(metricCode, payload);
    } finally {
      savingMetric = null;
    }
  }

  async function applyToCategory(sourceMetricCode: string) {
    const templateItems = getMetricItems(sourceMetricCode);
    const templateOrder = templateItems.map((p) => p.source);

    const sisterMetrics = metrics.filter((m) =>
      matchesCategory(m.code, selectedCategory === 'all' ? 'sleep' : selectedCategory)
    );

    for (const target of sisterMetrics) {
      const currentItems = getMetricItems(target.code);
      const currentMap = new Map(currentItems.map((i) => [i.source, i]));

      const reordered: UserSourcePreference[] = [];
      let rank = 1;
      for (const s of templateOrder) {
        const match = currentMap.get(s);
        if (match) {
          reordered.push({ ...match, priority_rank: rank++ });
          currentMap.delete(s);
        }
      }
      for (const [, remaining] of currentMap) {
        reordered.push({ ...remaining, priority_rank: rank++ });
      }

      await handleMetricUpdate(target.code, reordered);
    }
  }
  function openSourceModal(src: { id: string; name: string; icon: string; color: string }) {
    selectedSource = src;
    sourceModalOpen = true;
  }
</script>

<svelte:head><title>Salus — Data Sources</title></svelte:head>

{#if loading}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else}
  <div class="space-y-8">
    <!-- Section 1: Data Sources -->
    <div>
      <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div class="min-w-0 flex-1">
          <h2 class="text-base font-bold text-surface-900">Data Sources</h2>
          <p class="mt-0.5 text-xs text-surface-500">
            Overview of health platforms, sensors, and wearables integrated with Salus.
          </p>
        </div>
        <div class="w-full shrink-0 md:w-64">
          <SearchInput bind:value={sourceSearchQuery} placeholder="Filter data sources…" />
        </div>
      </div>

      {#if sortedAndFilteredSources.length === 0}
        <Card class="py-8">
          <EmptyState
            icon="search"
            title="No Sources Found"
            description="No data sources matching '{sourceSearchQuery}'"
          />
        </Card>
      {:else}
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {#each sortedAndFilteredSources as src (src.id)}
            {@const count = sourceCounts[src.id] ?? 0}
            {@const isActive = count > 0}
            <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
            <div onclick={() => openSourceModal(src)} class="cursor-pointer">
              <Card padding={false} hoverable disabled={!isActive}>
                <div class="p-3.5">
                  <div class="flex items-start justify-between">
                    <div class="flex items-center gap-3">
                      <div
                        class="flex h-9 w-9 items-center justify-center rounded-lg text-white shadow-2xs transition-all {isActive
                          ? ''
                          : 'opacity-75 grayscale'}"
                        style="background-color: {isActive ? src.color : '#9ca3af'}"
                      >
                        <Icon name={src.icon} size="sm" />
                      </div>
                      <div>
                        <h3
                          class="text-xs font-semibold {isActive
                            ? 'text-surface-900'
                            : 'text-surface-600'}"
                        >
                          {src.name}
                        </h3>
                        <span class="font-mono text-[10px] text-surface-400">{src.id}</span>
                      </div>
                    </div>

                    {#if isActive}
                      <span
                        class="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700"
                      >
                        <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span> Active
                      </span>
                    {:else}
                      <span
                        class="inline-flex items-center rounded-full border border-surface-200/60 bg-surface-100 px-2 py-0.5 text-[10px] font-medium text-surface-500"
                      >
                        Inactive
                      </span>
                    {/if}
                  </div>

                  <div
                    class="mt-3 flex items-center justify-between border-t border-surface-100 pt-2 text-[11px]"
                  >
                    <span class="text-surface-500">Measurements</span>
                    <span
                      class="font-bold {isActive
                        ? 'text-surface-900'
                        : 'font-normal text-surface-500'}"
                    >
                      {count > 0 ? count.toLocaleString() : '—'}
                    </span>
                  </div>
                </div></Card
              >
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Section 2: Priority Matrix Concept C+ Board -->
    <div>
      <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div class="min-w-0 flex-1">
          <h2 class="text-base font-bold text-surface-900">Priority Matrix</h2>
          <p class="mt-0.5 text-xs text-surface-500">
            Resolve data conflicts for metrics with multiple active devices or sources.
          </p>
        </div>

        <!-- Priority Matrix Toolbar: SearchInput + Category Select -->
        <div class="flex shrink-0 flex-col gap-2.5 sm:flex-row sm:items-center">
          <SearchInput
            bind:value={matrixSearchQuery}
            placeholder="Filter metrics…"
            class="w-full sm:w-48"
          />
          <Select
            name="category"
            options={CATEGORY_OPTIONS}
            bind:value={selectedCategory}
            class="w-full sm:w-48"
          />
        </div>
      </div>

      {#if filteredMatrixMetrics.length === 0}
        <Card class="py-8">
          <EmptyState
            icon="tune"
            title="No Conflict Metrics Found"
            description="No metrics with multiple data sources matching the current search or category filter."
          />
        </Card>
      {:else}
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {#each filteredMatrixMetrics as metric (metric.code)}
            {@const items = getMetricItems(metric.code)}
            <SourcePriorityCard
              {metric}
              {items}
              saving={savingMetric === metric.code}
              onUpdate={(newItems) => handleMetricUpdate(metric.code, newItems)}
              onApplyToCategory={() => applyToCategory(metric.code)}
            />
          {/each}
        </div>
      {/if}
    </div>
  </div>
{/if}

{#if selectedSource}
  <SourceDetailsModal
    bind:open={sourceModalOpen}
    source={selectedSource}
    count={sourceCounts[selectedSource.id] ?? 0}
  />
{/if}
