<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import { METRIC_GROUPS } from '../../data/metrics-data';
  import type { MetricGroup, MetricDefinition } from '../../types';

  let {
    onSelectGroup,
    onSelectMetric
  } = $props<{
    onSelectGroup: (groupKey: string) => void;
    onSelectMetric: (groupKey: string, metricCode: string) => void;
  }>();

  let selectedCategory = $state<string>('all');
  let searchQuery = $state<string>('');

  const categories = [
    { id: 'all', label: 'Alle Metriken' },
    { id: 'cardiovascular', label: 'Kardiovaskulär' },
    { id: 'body', label: 'Körper und Gewicht' },
    { id: 'metabolism', label: 'Stoffwechsel' },
    { id: 'sleep', label: 'Schlaf' },
    { id: 'labs', label: 'Klinische Labore' }
  ];

  let filteredGroups = $derived(
    METRIC_GROUPS.filter(g => {
      const matchCat = selectedCategory === 'all' || g.category === selectedCategory;
      const matchQuery =
        !searchQuery ||
        g.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        g.subMetrics.some(m => m.name.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchCat && matchQuery;
    })
  );
</script>

<div class="space-y-6">
  <!-- Page Header -->
  <div class="flex items-center justify-between flex-wrap gap-3">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Vitalparameter und Metriken</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Evidenzbasierte Definitionen mit individuellen Längsschnitt-Verläufen
      </p>
    </div>
    <div class="flex items-center gap-2">
      <input
        type="text"
        placeholder="Metrik suchen (z.B. Blutdruck, LDL, Gewicht)..."
        bind:value={searchQuery}
        class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl px-3.5 py-2 text-xs text-[var(--text-main)] outline-none focus:border-[var(--color-primary)] w-64"
      />
    </div>
  </div>

  <!-- Category Filter Pills -->
  <div class="flex gap-2 overflow-x-auto pb-1">
    {#each categories as cat}
      <button
        type="button"
        onclick={() => selectedCategory = cat.id}
        class="px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap cursor-pointer transition-all {selectedCategory === cat.id ? 'bg-[var(--color-primary)] text-white shadow-sm' : 'bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)] border border-[var(--border-subtle)]'}"
      >
        {cat.label}
      </button>
    {/each}
  </div>

  <!-- Metric Groups Grid -->
  <div class="space-y-5">
    {#each filteredGroups as group}
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <!-- Group Header (Clickable to Group Detail) -->
        <div class="flex items-center justify-between mb-3 border-b border-[var(--border-subtle)] pb-3">
          <div>
            <button
              type="button"
              onclick={() => onSelectGroup(group.key)}
              class="text-base font-extrabold text-[var(--text-main)] hover:text-[var(--color-primary)] transition-colors flex items-center gap-2 cursor-pointer"
            >
              <span>{group.title}</span>
              <Icon name="chevron-down" size={14} class="-rotate-90 text-[var(--text-soft)]" />
            </button>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">{group.description}</p>
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
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {#each group.subMetrics as metric}
            <button
              type="button"
              onclick={() => onSelectMetric(group.key, metric.code)}
              class="text-left bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3.5 hover:bg-[var(--bg-surface-100)] transition-all cursor-pointer flex flex-col justify-between group"
            >
              <div>
                <div class="flex items-center justify-between mb-1">
                  <span class="text-xs font-bold text-[var(--text-main)] group-hover:text-[var(--color-primary)] transition-colors">
                    {metric.name}
                  </span>
                  <span class="text-[0.6875rem] font-mono text-[var(--text-soft)]">{metric.unit}</span>
                </div>
                <div class="flex items-baseline gap-2 mt-1">
                  <span class="text-xl font-extrabold font-mono text-[var(--text-main)] tabular-nums">
                    {metric.currentValue}
                  </span>
                  {#if metric.deltaPercent}
                    <span class="text-xs font-mono font-bold {metric.deltaPercent < 0 ? 'text-[var(--color-success)]' : 'text-[var(--color-vital)]'}">
                      {metric.deltaPercent > 0 ? '+' : ''}{metric.deltaPercent}%
                    </span>
                  {/if}
                </div>
              </div>

              <!-- Sparkline & EMA Footer -->
              <div class="mt-3 pt-2 border-t border-[var(--border-subtle)] flex items-center justify-between text-[0.6875rem] text-[var(--text-soft)] font-mono">
                <span>7T-EMA: {metric.ema7d}</span>
                <span class="text-[var(--color-primary)] group-hover:underline">Detail &rarr;</span>
              </div>
            </button>
          {/each}
        </div>
      </div>
    {/each}
  </div>
</div>
