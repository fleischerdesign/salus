<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { METRIC_GROUPS } from '../../data/metrics-data';
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

  // Reactive Measurements from Dexie for real values
  const measurementsQuery = useQuery(() => db.measurement.filter((m) => !m.deleted_at).toArray());
  const measurements = $derived(measurementsQuery.value ?? []);

  const latestMeasurementsMap = $derived.by(() => {
    const map = new Map<string, number>();
    const sorted = [...measurements].sort(
      (a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
    );
    for (const m of sorted) {
      if (m.metric_code && m.value_numeric != null && !map.has(m.metric_code)) {
        map.set(m.metric_code, m.value_numeric);
      }
    }
    return map;
  });

  const categories = $derived([
    { id: 'all', label: 'Alle Metriken' },
    ...(goals.length > 0 ? [{ id: 'has_goal', label: `Mit Ziel (${goals.length})` }] : []),
    { id: 'cardiovascular', label: 'Kardiovaskulär' },
    { id: 'body', label: 'Körper & Gewicht' },
    { id: 'metabolism', label: 'Stoffwechsel' },
    { id: 'sleep', label: 'Schlaf' },
    { id: 'labs', label: 'Klinische Labore' }
  ]);

  let filteredGroups = $derived(
    METRIC_GROUPS.map((g: MetricGroup) => {
      let sub = g.subMetrics;
      if (selectedCategory === 'has_goal') {
        sub = sub.filter((m) => goalsMap.has(m.code));
      }
      return { ...g, subMetrics: sub };
    }).filter((g: MetricGroup) => {
      if (selectedCategory === 'has_goal') {
        if (g.subMetrics.length === 0) return false;
      } else if (selectedCategory !== 'all' && g.category !== selectedCategory) {
        return false;
      }

      const matchQuery =
        !searchQuery ||
        g.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        g.subMetrics.some((m: MetricDefinition) =>
          m.name.toLowerCase().includes(searchQuery.toLowerCase())
        );
      return matchQuery;
    })
  );
</script>

<div class="space-y-6">
  <!-- Page Header -->
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Vitalparameter &amp; Metriken</h1>
      <p class="mt-0.5 text-sm text-[var(--text-muted)]">
        Evidenzbasierte Definitionen mit Längsschnitt-Verläufen, Zielwerten und statistischen
        Prognosen
      </p>
    </div>
    <div class="w-64">
      <Input icon="search" placeholder="Metrik suchen..." bind:value={searchQuery} />
    </div>
  </div>

  <!-- Category Filter Pills -->
  <div class="flex gap-2 overflow-x-auto pb-1">
    {#each categories as cat}
      <button
        type="button"
        onclick={() => (selectedCategory = cat.id)}
        class="cursor-pointer rounded-full px-3.5 py-1.5 text-xs font-semibold whitespace-nowrap transition-all {selectedCategory ===
        cat.id
          ? 'bg-[var(--color-primary)] text-white shadow-sm'
          : 'border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        {cat.label}
      </button>
    {/each}
  </div>

  <!-- Metric Groups Grid -->
  <div class="space-y-5">
    {#each filteredGroups as group}
      <div
        class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
      >
        <!-- Group Header (Clickable to Group Detail) -->
        <div
          class="mb-3 flex items-center justify-between border-b border-[var(--border-subtle)] pb-3"
        >
          <div>
            <button
              type="button"
              onclick={() => onSelectGroup(group.key)}
              class="flex cursor-pointer items-center gap-2 text-base font-extrabold text-[var(--text-main)] transition-colors hover:text-[var(--color-primary)]"
            >
              <span>{group.title}</span>
              <Icon name="expand-more" size={14} class="-rotate-90 text-[var(--text-soft)]" />
            </button>
            <p class="mt-0.5 text-xs text-[var(--text-muted)]">{group.description}</p>
          </div>
          <div class="flex items-center gap-2">
            {#if group.inputMode === 'combined'}
              <Badge variant="primary">Kombinierte Erfassung</Badge>
            {/if}
            <Btn variant="secondary" size="sm" onclick={() => onSelectGroup(group.key)}>
              Gruppe öffnen
            </Btn>
          </div>
        </div>

        <!-- Sub-Metrics Cards Grid -->
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {#each group.subMetrics as metric}
            {@const goal = goalsMap.get(metric.code)}
            {@const realVal = latestMeasurementsMap.get(metric.code)}
            <button
              type="button"
              onclick={() => onSelectMetric(group.key, metric.code)}
              class="group flex cursor-pointer flex-col justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5 text-left transition-all hover:bg-[var(--bg-surface-100)]"
            >
              <div>
                <div class="mb-1 flex items-center justify-between">
                  <span
                    class="text-xs font-bold text-[var(--text-main)] transition-colors group-hover:text-[var(--color-primary)]"
                  >
                    {metric.name}
                  </span>
                  <span class="text-[0.6875rem] font-medium text-[var(--text-soft)]"
                    >{metric.unit}</span
                  >
                </div>
                <div class="mt-1 flex items-baseline gap-2">
                  <span class="text-xl font-extrabold text-[var(--text-main)] tabular-nums">
                    {#if realVal != null}
                      {realVal}
                    {:else}
                      <span class="text-base font-normal text-[var(--text-muted)]">—</span>
                    {/if}
                  </span>
                </div>

                <!-- Goal Badge if defined -->
                {#if goal}
                  <div
                    class="mt-2 flex items-center justify-between rounded-md bg-[var(--color-primary-soft)]/20 px-2 py-1 text-[0.6875rem] font-semibold text-[var(--color-primary)]"
                  >
                    <span>🎯 Ziel: {goal.target_value} {metric.unit}</span>
                  </div>
                {/if}
              </div>

              <!-- Footer -->
              <div
                class="mt-3 flex items-center justify-between border-t border-[var(--border-subtle)] pt-2 text-[0.6875rem] text-[var(--text-soft)]"
              >
                <span class="font-medium">
                  {realVal != null ? 'Messwert erfasst' : 'Keine Messdaten'}
                </span>
                <span class="font-semibold text-[var(--color-primary)] group-hover:underline"
                  >Detail &rarr;</span
                >
              </div>
            </button>
          {/each}
        </div>
      </div>
    {/each}
  </div>
</div>
