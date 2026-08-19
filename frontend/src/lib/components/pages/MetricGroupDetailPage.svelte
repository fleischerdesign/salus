<script lang="ts">
  import Breadcrumb from '../ui/Breadcrumb.svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import EmptyState from '../ui/EmptyState.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { METRIC_GROUPS } from '../../data/metrics-data';
  import { createMeasurement, deleteMeasurement } from '$lib/mutations/measurement';
  import { nowIso } from '$lib/utils/datetime';

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
  let subCodes = $derived(group.subMetrics.map((m) => m.code));

  // Reactive Dexie measurements for all submetrics in this group (Top 100)
  const groupMeasurementsQuery = useQuery(
    async () => {
      const items = await db.measurement
        .where('metric_code')
        .anyOf(subCodes)
        .and((m) => !m.deleted_at)
        .reverse()
        .sortBy('start_time');
      return items.slice(0, 100);
    },
    () => groupKey
  );
  const groupMeasurements = $derived(groupMeasurementsQuery.value ?? []);

  // Map of latest measurements by metric code
  const latestByCode = $derived.by(() => {
    const map = new Map<string, number>();
    for (const m of groupMeasurements) {
      if (m.metric_code && m.value_numeric != null && !map.has(m.metric_code)) {
        map.set(m.metric_code, m.value_numeric);
      }
    }
    return map;
  });

  // Combined Form Inputs
  let val1 = $state(120);
  let val2 = $state(80);
  let val3 = $state(65);
  let isSaving = $state(false);
  let saveSuccess = $state(false);

  async function submitCombined() {
    isSaving = true;
    try {
      const now = nowIso();
      await Promise.all([
        createMeasurement('systolic_bp', {
          value: Number(val1),
          measured_at: now,
          source: 'manual',
          note: 'Kombinierte Blutdruckmessung'
        }),
        createMeasurement('diastolic_bp', {
          value: Number(val2),
          measured_at: now,
          source: 'manual',
          note: 'Kombinierte Blutdruckmessung'
        }),
        createMeasurement('resting_heart_rate', {
          value: Number(val3),
          measured_at: now,
          source: 'manual',
          note: 'Kombinierte Blutdruckmessung'
        })
      ]);
      saveSuccess = true;
      setTimeout(() => (saveSuccess = false), 3500);
    } catch (e) {
      console.error('Fehler beim Speichern der kombinierten Messung:', e);
    } finally {
      isSaving = false;
    }
  }

  async function handleDeleteEntry(id: string) {
    if (!confirm('Möchtest du diesen Messwert wirklich löschen?')) return;
    await deleteMeasurement(id);
  }

  function formatTimestamp(iso: string): string {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return iso;
    }
  }

  function getMetricName(code: string | null): string {
    if (!code) return '—';
    const found = group.subMetrics.find((m) => m.code === code);
    return found ? found.name : code;
  }

  function getMetricUnit(code: string | null): string {
    if (!code) return '';
    const found = group.subMetrics.find((m) => m.code === code);
    return found ? found.unit : '';
  }
</script>

<div class="space-y-6">
  <!-- Breadcrumbs -->
  <Breadcrumb
    items={[
      { label: 'Metriken', onclick: onBack },
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

      {#if saveSuccess}
        <div
          class="mb-3 flex items-center gap-2 rounded-xl bg-[var(--color-success-soft)] p-3 text-xs font-semibold text-[var(--color-success)]"
        >
          <Icon name="check" size="sm" />
          Messwerte (Blutdruck &amp; Puls) erfolgreich synchron in Dexie gespeichert.
        </div>
      {/if}

      <Btn variant="primary" class="w-full" onclick={submitCombined} disabled={isSaving}>
        {isSaving ? 'Wird gespeichert...' : 'Kombinierte Messung speichern'}
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
        {@const realVal = latestByCode.get(metric.code)}
        <button
          type="button"
          onclick={() => onSelectMetric(group.key, metric.code)}
          class="cursor-pointer rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-4 text-left shadow-[var(--shadow-card)] transition-all hover:border-[var(--color-primary)]"
        >
          <div class="text-xs font-bold text-[var(--text-muted)]">{metric.name}</div>
          <div class="mt-1 text-2xl font-extrabold text-[var(--text-main)] tabular-nums">
            {#if realVal != null}
              {realVal}
              <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
            {:else}
              <span class="text-base font-normal text-[var(--text-muted)]">—</span>
            {/if}
          </div>
          <div class="mt-2 text-[0.6875rem] text-[var(--text-soft)]">
            Ziel: {metric.referenceRange}
          </div>
          <div
            class="mt-3 flex items-center justify-between border-t border-[var(--border-subtle)] pt-2 text-xs font-semibold text-[var(--color-primary)]"
          >
            <span>Metrik-Details &amp; Historie</span>
            <span>&rarr;</span>
          </div>
        </button>
      {/each}
    </div>
  </div>

  <!-- Real Entries Table -->
  <div
    class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
  >
    <div class="mb-3 flex items-center justify-between">
      <span class="text-sm font-bold">Historie der Messungen ({groupMeasurements.length})</span>
      <span class="text-xs text-[var(--text-muted)]">Aus Dexie IndexedDB</span>
    </div>

    {#if groupMeasurements.length === 0}
      <div class="py-6">
        <EmptyState
          title="Noch keine Messungen in dieser Gruppe"
          description="Erfasse deine erste Messung über das obige Erfassungsformular oder wähle eine Einzel-Metrik."
        />
      </div>
    {:else}
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
              <th class="px-3 py-2.5 text-right">Aktion</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-subtle)]">
            {#each groupMeasurements as entry (entry.id)}
              <tr>
                <td class="px-3 py-2.5 text-[var(--text-soft)]">
                  {formatTimestamp(entry.start_time)}
                </td>
                <td class="px-3 py-2.5 font-semibold text-[var(--text-main)]">
                  {getMetricName(entry.metric_code)}
                </td>
                <td class="px-3 py-2.5 font-bold text-[var(--color-primary)] tabular-nums">
                  {entry.value_numeric ?? '—'}
                  {getMetricUnit(entry.metric_code)}
                </td>
                <td class="px-3 py-2.5">
                  <Badge variant="default">{entry.source || 'Manuell'}</Badge>
                </td>
                <td class="px-3 py-2.5 text-[var(--text-muted)]">{entry.notes || '—'}</td>
                <td class="px-3 py-2.5 text-right">
                  <button
                    type="button"
                    class="cursor-pointer p-1 text-xs font-semibold text-[var(--text-muted)] transition-colors hover:text-[var(--color-vital)]"
                    title="Messwert löschen"
                    onclick={() => handleDeleteEntry(entry.id)}
                  >
                    <Icon name="delete" size="sm" />
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>
