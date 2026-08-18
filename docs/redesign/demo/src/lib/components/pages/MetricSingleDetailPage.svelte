<script lang="ts">
  import Breadcrumb from '../ui/Breadcrumb.svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import InteractiveChart from '../insights/InteractiveChart.svelte';
  import { METRIC_GROUPS, MOCK_MEASUREMENTS } from '../../data/metrics-data';

  let {
    groupKey = 'blood_pressure',
    metricCode = 'systolic_bp',
    onBackGroup,
    onBackAll
  } = $props<{
    groupKey: string;
    metricCode: string;
    onBackGroup: () => void;
    onBackAll: () => void;
  }>();

  let group = $derived(METRIC_GROUPS.find(g => g.key === groupKey) || METRIC_GROUPS[0]);
  let metric = $derived(group.subMetrics.find(m => m.code === metricCode) || group.subMetrics[0]);

  let entries = $derived(MOCK_MEASUREMENTS[metricCode] || [
    { id: '1', metricCode, value: Number(metric.currentValue) || 100, unit: metric.unit, timestamp: '2026-08-17 08:15', source: 'Withings Body Scan', note: 'Nüchtern nach dem Aufstehen', priority: 'Rang 1 Primär' }
  ]);

  let newEntryValue = $state('');

  function addEntry() {
    if (!newEntryValue) return;
    alert(`Neuer Messwert erfasst: ${newEntryValue} ${metric.unit}. Zeitstempel: Jetzt.`);
    newEntryValue = '';
  }
</script>

<div class="space-y-6">
  <!-- Tier-3 Breadcrumbs -->
  <Breadcrumb
    items={[
      { label: 'Klinik', onclick: onBackAll },
      { label: 'Metriken-Katalog', onclick: onBackAll },
      { label: group.title, onclick: onBackGroup },
      { label: metric.name, active: true }
    ]}
  />

  <!-- Hero Header with Mann-Kendall Statistical Test Badge -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <div class="flex items-center gap-2 flex-wrap">
        <h1 class="text-2xl font-extrabold tracking-tight">{metric.name}</h1>
        <Badge variant="success">{metric.referenceRange}</Badge>
        <Badge variant="primary">Mann-Kendall: p = 0.004 (Signifikant)</Badge>
      </div>
      <p class="text-xs sm:text-sm text-[var(--text-muted)] mt-0.5">
        Canonical Metric Code: <span class="font-bold text-[var(--text-main)]">{metric.code}</span> • PELT-Wendepunkt am 04. Aug erkannt
      </p>
    </div>

    <!-- Quick Entry Input -->
    <div class="flex items-center gap-2 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-1.5 shadow-xs">
      <input
        type="number"
        placeholder={`Neuer Wert in ${metric.unit}...`}
        bind:value={newEntryValue}
        class="bg-transparent border-none outline-none text-xs px-2 w-36 text-[var(--text-main)]"
      />
      <Btn variant="primary" size="sm" onclick={addEntry}>
        Erfassen +
      </Btn>
    </div>
  </div>

  <!-- 4 Statistical KPI Tiles (Calculated via services/analytics/stats.py) -->
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-3.5 shadow-xs">
      <span class="text-[0.6875rem] text-[var(--text-muted)] uppercase tracking-wider block font-bold">Aktueller Wert</span>
      <div class="text-xl font-extrabold text-[var(--text-main)] mt-0.5 tabular-nums">
        {metric.currentValue} <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
      </div>
    </div>

    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-3.5 shadow-xs">
      <span class="text-[0.6875rem] text-[var(--text-muted)] uppercase tracking-wider block font-bold">7-Tage EMA (Glättung)</span>
      <div class="text-xl font-extrabold text-[var(--color-primary)] mt-0.5 tabular-nums">
        {metric.ema7d} <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
      </div>
    </div>

    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-3.5 shadow-xs">
      <span class="text-[0.6875rem] text-[var(--text-muted)] uppercase tracking-wider block font-bold">Standardabweichung (σ)</span>
      <div class="text-xl font-extrabold text-[var(--text-main)] mt-0.5 tabular-nums">
        &plusmn; 2.1 <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
      </div>
    </div>

    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-3.5 shadow-xs">
      <span class="text-[0.6875rem] text-[var(--text-muted)] uppercase tracking-wider block font-bold">Mann-Kendall Trend (τ)</span>
      <div class="text-xl font-extrabold text-emerald-500 mt-0.5 tabular-nums">
        ↘ -0.38 (p &lt; 0.01)
      </div>
    </div>
  </div>

  <!-- Full-Width Interactive Spline Chart -->
  <InteractiveChart data={[]} metricCode={metric.code} unit={metric.unit} />

  <!-- 2-Column: Clinical Target Zones & Pearson Correlations -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Clinical Range Bands -->
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] space-y-3">
      <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="labs" class="text-[var(--color-primary)]" />
        <span>Klinische Referenz- und Zielkorridore</span>
      </div>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between p-2.5 rounded-xl bg-[var(--color-success-soft)]/20 border border-[var(--color-success)]/30">
          <span class="text-[var(--color-success)] font-bold">Optimal / Zielkorridor</span>
          <span class="font-bold">105 – 120 {metric.unit}</span>
        </div>
        <div class="flex justify-between p-2.5 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)]">
          <span>Normwert / Grenzwertig</span>
          <span>120 – 139 {metric.unit}</span>
        </div>
        <div class="flex justify-between p-2.5 rounded-xl bg-[var(--color-vital-soft)]/20 border border-[var(--color-vital)]/30 text-[var(--color-vital)]">
          <span>Erhöhtes Risiko</span>
          <span class="font-bold">&ge; 140 {metric.unit}</span>
        </div>
      </div>
    </div>

    <!-- Biometric Correlations -->
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] space-y-3">
      <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="insights" class="text-[var(--color-circadian)]" />
        <span>Statistische Korrelationen (Pearson r)</span>
      </div>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between items-center p-2.5 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]">
          <span class="font-semibold text-[var(--text-main)]">Schlafdauer (&gt; 7.5h)</span>
          <span class="font-bold text-emerald-500">r = -0.62 (Starke Senkung)</span>
        </div>
        <div class="flex justify-between items-center p-2.5 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]">
          <span class="font-semibold text-[var(--text-main)]">Körpergewicht</span>
          <span class="font-bold text-[var(--color-primary)]">r = +0.58 (Positiver Trend)</span>
        </div>
        <div class="flex justify-between items-center p-2.5 rounded-xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]">
          <span class="font-semibold text-[var(--text-main)]">Koffein nach 15:00 Uhr</span>
          <span class="font-bold text-rose-500">r = +0.44 (Spike am Abend)</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Complete Entries History Table with Source Resolution Provenance -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] space-y-3">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h2 class="text-sm font-bold text-[var(--text-main)]">Lückenlose Messwert-Historie ({entries.length} Einträge)</h2>
        <p class="text-xs text-[var(--text-muted)] mt-0.5">Multi-Source Prioritätsprüfung (services/source_resolution.py)</p>
      </div>
      <Badge variant="success">0 Duplikate • Dedup Aktiv</Badge>
    </div>
    
    <div class="w-full overflow-x-auto">
      <table class="w-full text-left text-xs border-collapse">
        <thead>
          <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.6875rem]">
            <th class="py-2.5 px-3">Zeitpunkt</th>
            <th class="py-2.5 px-3">Messwert</th>
            <th class="py-2.5 px-3">Abweichung zum EMA</th>
            <th class="py-2.5 px-3">Quelle und Priorität</th>
            <th class="py-2.5 px-3">Notiz</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)]">
          {#each entries as e}
            <tr>
              <td class="py-2.5 px-3 text-[var(--text-soft)]">{e.timestamp}</td>
              <td class="py-2.5 px-3 font-bold text-[var(--text-main)] text-sm tabular-nums">{e.value} {e.unit}</td>
              <td class="py-2.5 px-3 text-emerald-500 font-semibold tabular-nums">-0.2 {e.unit}</td>
              <td class="py-2.5 px-3">
                <Badge variant="default" class="font-bold">{e.source || 'Withings Body Scan'} (Rang 1 Primär)</Badge>
              </td>
              <td class="py-2.5 px-3 text-[var(--text-muted)]">{e.note || 'Nüchtern gemessen'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>
