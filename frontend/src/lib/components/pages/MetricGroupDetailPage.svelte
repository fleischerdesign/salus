<script lang="ts">
  import Breadcrumb from '../ui/Breadcrumb.svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
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

  let group = $derived(METRIC_GROUPS.find((g) => g.key === groupKey) || METRIC_GROUPS[0]);

  // Combined Form Inputs
  let val1 = $state(120);
  let val2 = $state(80);
  let val3 = $state(65);

  function submitCombined() {
    alert(
      `Messung erfasst: ${val1}/${val2} mmHg, Puls ${val3} bpm. Lokal in Dexie gespeichert und via SSE synchronisiert.`
    );
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
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">{group.title}</h1>
      <p class="mt-0.5 text-sm text-[var(--text-muted)]">{group.description}</p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Status: Optimal (ESC Leitlinie)</Badge>
    </div>
  </div>

  <!-- Combined Entry Card (if inputMode === 'combined') -->
  {#if group.inputMode === 'combined'}
    <div
      class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div class="mb-4 flex items-center justify-between">
        <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
          <Icon name="vitals" class="text-[var(--color-vital)]" />
          <span>Kombinierte Messwerterfassung</span>
        </div>
        <span class="text-xs text-[var(--text-muted)]">Erzeugt synchrone Messpunkte</span>
      </div>

      <div class="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Input label="Systolisch" unit="mmHg" type="number" bind:value={val1} />
        <Input label="Diastolisch" unit="mmHg" type="number" bind:value={val2} />
        <Input label="Puls" unit="bpm" type="number" bind:value={val3} />
      </div>

      <Btn variant="primary" class="w-full" onclick={submitCombined}>
        Kombinierte Messung speichern
      </Btn>
    </div>
  {/if}

  <!-- Multi-Metric Overview Cards -->
  <div>
    <h2 class="mb-3 text-sm font-bold tracking-wider text-[var(--text-muted)] uppercase">
      Enthaltene Einzel-Metriken
    </h2>
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {#each group.subMetrics as metric}
        <button
          type="button"
          onclick={() => onSelectMetric(group.key, metric.code)}
          class="cursor-pointer rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-4 text-left shadow-[var(--shadow-card)] transition-all hover:border-[var(--color-primary)]"
        >
          <div class="text-xs font-bold text-[var(--text-muted)]">{metric.name}</div>
          <div class="mt-1 font-mono text-2xl font-extrabold text-[var(--text-main)]">
            {metric.currentValue}
            <span class="font-sans text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
          </div>
          <div class="mt-2 font-mono text-[0.6875rem] text-[var(--text-soft)]">
            Ziel: {metric.referenceRange}
          </div>
          <div
            class="mt-3 flex items-center justify-between border-t border-[var(--border-subtle)] pt-2 text-xs font-semibold text-[var(--color-primary)]"
          >
            <span>Metrik-Details & Historie</span>
            <span>&rarr;</span>
          </div>
        </button>
      {/each}
    </div>
  </div>

  <!-- Recent Entries Table -->
  <div
    class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
  >
    <div class="mb-3 flex items-center justify-between">
      <span class="text-sm font-bold">Historie der Messungen</span>
      <span class="text-xs text-[var(--text-muted)]">Letzte 7 Tage</span>
    </div>
    <div class="w-full overflow-x-auto">
      <table class="w-full border-collapse text-left text-xs">
        <thead>
          <tr
            class="border-b border-[var(--border-subtle)] text-[0.6875rem] tracking-wider text-[var(--text-muted)] uppercase"
          >
            <th class="px-3 py-2.5">Zeitpunkt</th>
            <th class="px-3 py-2.5">Metrik</th>
            <th class="px-3 py-2.5">Wert</th>
            <th class="px-3 py-2.5">Quelle</th>
            <th class="px-3 py-2.5">Notiz</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)] font-mono">
          {#each MOCK_MEASUREMENTS[group.subMetrics[0]?.code] || [] as entry}
            <tr>
              <td class="px-3 py-2.5 text-[var(--text-soft)]">{entry.timestamp}</td>
              <td class="px-3 py-2.5 font-sans font-semibold text-[var(--text-main)]"
                >{group.subMetrics[0]?.name}</td
              >
              <td class="px-3 py-2.5 font-bold text-[var(--color-primary)]"
                >{entry.value} {entry.unit}</td
              >
              <td class="px-3 py-2.5 font-sans"><Badge variant="default">{entry.source}</Badge></td>
              <td class="px-3 py-2.5 font-sans text-[var(--text-muted)]">{entry.note || '—'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>
