<script lang="ts">
  import Breadcrumb from '../ui/Breadcrumb.svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import { METRIC_GROUPS, MOCK_MEASUREMENTS } from '../../data/metrics-data';

  let {
    groupKey = 'blood_pressure',
    onBack,
    onSelectMetric
  } = $props<{
    groupKey: string;
    onBack: () => void;
    onSelectMetric: (groupKey: string, metricCode: string) => void;
  }>();

  let group = $derived(METRIC_GROUPS.find(g => g.key === groupKey) || METRIC_GROUPS[0]);

  // Combined Form Inputs
  let val1 = $state(120);
  let val2 = $state(80);
  let val3 = $state(65);

  function submitCombined() {
    alert(`Messung erfasst: ${val1}/${val2} mmHg, Puls ${val3} bpm. Lokal in Dexie gespeichert und via SSE synchronisiert.`);
  }
</script>

<div class="space-y-6">
  <!-- Tier-3 Breadcrumbs -->
  <Breadcrumb
    items={[
      { label: 'Klinik', onclick: onBack },
      { label: 'Metriken-Katalog', onclick: onBack },
      { label: group.title, active: true }
    ]}
  />

  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-3">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">{group.title}</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">{group.description}</p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Status: Optimal (ESC Leitlinie)</Badge>
    </div>
  </div>

  <!-- Combined Entry Card (if inputMode === 'combined') -->
  {#if group.inputMode === 'combined'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
      <div class="flex items-center justify-between mb-4">
        <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
          <Icon name="vitals" class="text-[var(--color-vital)]" />
          <span>Kombinierte Messwerterfassung</span>
        </div>
        <span class="text-xs text-[var(--text-muted)]">Erzeugt synchrone Messpunkte</span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        <div>
          <label for="input-sys" class="block text-xs font-semibold text-[var(--text-muted)] mb-1">Systolisch (mmHg)</label>
          <input
            id="input-sys"
            type="number"
            bind:value={val1}
            class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 font-mono text-base font-bold text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
          />
        </div>
        <div>
          <label for="input-dia" class="block text-xs font-semibold text-[var(--text-muted)] mb-1">Diastolisch (mmHg)</label>
          <input
            id="input-dia"
            type="number"
            bind:value={val2}
            class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 font-mono text-base font-bold text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
          />
        </div>
        <div>
          <label for="input-pulse" class="block text-xs font-semibold text-[var(--text-muted)] mb-1">Puls (bpm)</label>
          <input
            id="input-pulse"
            type="number"
            bind:value={val3}
            class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 font-mono text-base font-bold text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]"
          />
        </div>
      </div>

      <Btn variant="primary" class="w-full" onclick={submitCombined}>
        Kombinierte Messung speichern
      </Btn>
    </div>
  {/if}

  <!-- Multi-Metric Overview Cards -->
  <div>
    <h2 class="text-sm font-bold uppercase tracking-wider text-[var(--text-muted)] mb-3">Enthaltene Einzel-Metriken</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      {#each group.subMetrics as metric}
        <button
          type="button"
          onclick={() => onSelectMetric(group.key, metric.code)}
          class="text-left bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-4 hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-[var(--shadow-card)]"
        >
          <div class="text-xs font-bold text-[var(--text-muted)]">{metric.name}</div>
          <div class="text-2xl font-extrabold font-mono text-[var(--text-main)] mt-1">
            {metric.currentValue} <span class="text-xs font-sans font-normal text-[var(--text-soft)]">{metric.unit}</span>
          </div>
          <div class="text-[0.6875rem] text-[var(--text-soft)] mt-2 font-mono">
            Ziel: {metric.referenceRange}
          </div>
          <div class="mt-3 pt-2 border-t border-[var(--border-subtle)] flex justify-between items-center text-xs text-[var(--color-primary)] font-semibold">
            <span>Metrik-Details & Historie</span>
            <span>&rarr;</span>
          </div>
        </button>
      {/each}
    </div>
  </div>

  <!-- Recent Entries Table -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
    <div class="flex items-center justify-between mb-3">
      <span class="text-sm font-bold">Historie der Messungen</span>
      <span class="text-xs text-[var(--text-muted)]">Letzte 7 Tage</span>
    </div>
    <div class="w-full overflow-x-auto">
      <table class="w-full text-left text-xs border-collapse">
        <thead>
          <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.6875rem]">
            <th class="py-2.5 px-3">Zeitpunkt</th>
            <th class="py-2.5 px-3">Metrik</th>
            <th class="py-2.5 px-3">Wert</th>
            <th class="py-2.5 px-3">Quelle</th>
            <th class="py-2.5 px-3">Notiz</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)] font-mono">
          {#each (MOCK_MEASUREMENTS[group.subMetrics[0]?.code] || []) as entry}
            <tr>
              <td class="py-2.5 px-3 text-[var(--text-soft)]">{entry.timestamp}</td>
              <td class="py-2.5 px-3 font-sans font-semibold text-[var(--text-main)]">{group.subMetrics[0]?.name}</td>
              <td class="py-2.5 px-3 font-bold text-[var(--color-primary)]">{entry.value} {entry.unit}</td>
              <td class="py-2.5 px-3 font-sans"><Badge variant="default">{entry.source}</Badge></td>
              <td class="py-2.5 px-3 font-sans text-[var(--text-muted)]">{entry.note || '—'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>
