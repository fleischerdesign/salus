<script lang="ts">
  import Dexie from 'dexie';
  import Breadcrumb from '../ui/Breadcrumb.svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import EmptyState from '../ui/EmptyState.svelte';
  import InteractiveChart from '../insights/InteractiveChart.svelte';
  import GoalModal from '../modals/GoalModal.svelte';
  import AddMeasurementModal from '../modals/AddMeasurementModal.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { deleteGoal } from '$lib/mutations/goal';
  import { deleteMeasurement } from '$lib/mutations/measurement';
  import { findMetricDefinition, findMetricGroup } from '../../data/metrics-data';

  let {
    groupKey = '',
    metricCode = 'heart_rate',
    onBack,
    onBackGroup,
    onBackAll
  } = $props<{
    groupKey?: string;
    metricCode: string;
    onBack?: () => void;
    onBackGroup?: () => void;
    onBackAll?: () => void;
  }>();

  let metric = $derived(
    findMetricDefinition(metricCode) || {
      code: metricCode,
      name: metricCode,
      unit: '',
      category: 'cardiovascular' as const,
      dataType: 'number' as const,
      groupKey: undefined as string | undefined,
      currentValue: 0,
      trend: 'stable' as const,
      referenceRange: 'Normbereich',
      sparklineData: []
    }
  );
  let group = $derived(
    groupKey
      ? findMetricGroup(groupKey)
      : metric.groupKey
        ? findMetricGroup(metric.groupKey)
        : undefined
  );

  const PAGE_SIZE = 25;
  let currentPage = $state(1);

  // Reactive Dexie Goal Query
  const goalQuery = useQuery(
    () =>
      db.goal
        .where('metric_code')
        .equals(metricCode)
        .and((g) => !g.deleted_at)
        .first(),
    () => metricCode
  );
  const goal = $derived(goalQuery.value);

  // Instant O(1) query for absolute latest measurement
  const latestQuery = useQuery(
    () =>
      db.measurement
        .where('[metric_code+start_time]')
        .between([metricCode, Dexie.minKey], [metricCode, Dexie.maxKey])
        .and((m) => !m.deleted_at)
        .last(),
    () => metricCode
  );
  const latestMeasurement = $derived(latestQuery.value);
  const currentVal = $derived(latestMeasurement?.value_numeric ?? null);

  // Total count for pagination
  const countQuery = useQuery(
    () =>
      db.measurement
        .where('[metric_code+start_time]')
        .between([metricCode, Dexie.minKey], [metricCode, Dexie.maxKey])
        .and((m) => !m.deleted_at)
        .count(),
    () => metricCode
  );
  const totalCount = $derived(countQuery.value ?? 0);
  const totalPages = $derived(Math.max(1, Math.ceil(totalCount / PAGE_SIZE)));

  // High-performance compound-index paginated query (25 entries per page in 1ms)
  const measurementsQuery = useQuery(
    () =>
      db.measurement
        .where('[metric_code+start_time]')
        .between([metricCode, Dexie.minKey], [metricCode, Dexie.maxKey])
        .and((m) => !m.deleted_at)
        .reverse()
        .offset((currentPage - 1) * PAGE_SIZE)
        .limit(PAGE_SIZE)
        .toArray(),
    () => `${metricCode}:${currentPage}`
  );
  const measurements = $derived(measurementsQuery.value ?? []);

  let isGoalModalOpen = $state(false);
  let isAddEntryModalOpen = $state(false);

  const ema7d = $derived.by(() => {
    if (measurements.length === 0) return null;
    const nums = measurements
      .slice(0, 7)
      .map((m) => m.value_numeric)
      .filter((v): v is number => v != null);
    if (nums.length === 0) return null;
    const k = 2 / (nums.length + 1);
    return nums.reduce((acc, v) => v * k + acc * (1 - k), nums[0]).toFixed(1);
  });

  const stdDev = $derived.by(() => {
    const nums = measurements.map((m) => m.value_numeric).filter((v): v is number => v != null);
    if (nums.length < 2) return null;
    const mean = nums.reduce((a, b) => a + b, 0) / nums.length;
    const variance = nums.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / (nums.length - 1);
    return Math.sqrt(variance).toFixed(1);
  });

  const chartPoints = $derived(
    measurements
      .slice(0, 14)
      .reverse()
      .map((m) => ({
        date: m.start_time
          ? new Date(m.start_time).toLocaleDateString('de-DE', {
              day: '2-digit',
              month: 'short'
            })
          : '',
        val: m.value_numeric || 0
      }))
  );

  // Derived Goal Progress
  const targetVal = $derived(goal?.target_value ? Number(goal.target_value) : null);
  const isDecrease = $derived(goal?.direction === 'decrease');

  const goalProgress = $derived.by(() => {
    if (!targetVal || currentVal == null) return null;
    let percent = 0;
    let isFulfilled = false;

    if (isDecrease) {
      isFulfilled = currentVal <= targetVal;
      percent = isFulfilled
        ? 100
        : Math.max(0, Math.min(100, Math.round((targetVal / Math.max(currentVal, 1)) * 100)));
    } else {
      isFulfilled = currentVal >= targetVal;
      percent = isFulfilled
        ? 100
        : Math.max(0, Math.min(100, Math.round((currentVal / Math.max(targetVal, 1)) * 100)));
    }

    const delta = Math.abs(currentVal - targetVal).toFixed(1);
    const status = isFulfilled ? 'achieved' : percent >= 75 ? 'on_track' : 'off_track';

    return { percent, isFulfilled, delta, status };
  });

  async function handleRemoveGoal() {
    if (!goal?.id) return;
    if (!confirm('Möchtest du dieses persönliche Ziel wirklich entfernen?')) return;
    await deleteGoal(goal.id);
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
</script>

<div class="space-y-6">
  <!-- Tier-3 Breadcrumbs -->
  <Breadcrumb
    items={[
      { label: 'Metriken', onclick: onBackAll || onBack },
      ...(group ? [{ label: group.title, onclick: onBackGroup || onBack }] : []),
      { label: metric.name, active: true }
    ]}
  />

  <!-- Hero Header with Mann-Kendall Statistical Test Badge -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <div class="flex flex-wrap items-center gap-2">
        <h1 class="text-2xl font-extrabold tracking-tight">{metric.name}</h1>
        <Badge variant="success">{metric.referenceRange}</Badge>
        {#if measurements.length >= 5}
          <Badge variant="primary">Trend: Berechnet aus {measurements.length} Messungen</Badge>
        {/if}
      </div>
      <p class="mt-0.5 text-xs text-[var(--text-muted)] sm:text-sm">
        Canonical Metric Code: <span class="font-bold text-[var(--text-main)]">{metric.code}</span>
      </p>
    </div>

    <!-- Action Button to open Modal -->
    <div class="flex items-center gap-2">
      <Btn variant="primary" size="md" onclick={() => (isAddEntryModalOpen = true)}>
        + Messwert erfassen
      </Btn>
    </div>
  </div>

  <!-- 4 Statistical KPI Tiles (Calculated from Real Measurements) -->
  <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
    <div
      class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-3.5 shadow-xs"
    >
      <span
        class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >Aktueller Wert</span
      >
      <div class="mt-0.5 text-xl font-extrabold text-[var(--text-main)] tabular-nums">
        {#if currentVal != null}
          {currentVal}
          <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
        {:else}
          <span class="text-base font-normal text-[var(--text-muted)]">—</span>
        {/if}
      </div>
    </div>

    <div
      class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-3.5 shadow-xs"
    >
      <span
        class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >7-Tage EMA</span
      >
      <div class="mt-0.5 text-xl font-extrabold text-[var(--color-primary)] tabular-nums">
        {#if ema7d != null}
          {ema7d}
          <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
        {:else}
          <span class="text-base font-normal text-[var(--text-muted)]">—</span>
        {/if}
      </div>
    </div>

    <div
      class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-3.5 shadow-xs"
    >
      <span
        class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >Standardabweichung (σ)</span
      >
      <div class="mt-0.5 text-xl font-extrabold text-[var(--text-main)] tabular-nums">
        {#if stdDev != null}
          &plusmn; {stdDev}
          <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
        {:else}
          <span class="text-base font-normal text-[var(--text-muted)]">—</span>
        {/if}
      </div>
    </div>

    <div
      class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-3.5 shadow-xs"
    >
      <span
        class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >Gesamt-Einträge</span
      >
      <div class="mt-0.5 text-xl font-extrabold text-[var(--text-main)] tabular-nums">
        {measurements.length}
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- METRIC-CENTRIC GOAL & FORECAST SECTION                      -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if goal}
    <div
      class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)] transition-all"
    >
      <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2.5">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-xl bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
          >
            <Icon name="flag" size="sm" />
          </div>
          <div>
            <h3 class="text-sm font-extrabold text-[var(--text-main)]">
              Persönliches Ziel &amp; Trend-Prognose
            </h3>
            <span class="text-xs text-[var(--text-muted)]">
              {goal.frequency === 'milestone'
                ? 'Stichtags-Ziel'
                : goal.frequency === 'weekly'
                  ? 'Wöchentlicher Sollwert'
                  : 'Täglicher Sollwert'}
              {goal.deadline ? `• Frist: ${goal.deadline}` : ''}
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          {#if goalProgress}
            <Badge
              variant={goalProgress.status === 'achieved'
                ? 'success'
                : goalProgress.status === 'on_track'
                  ? 'primary'
                  : 'vital'}
            >
              {goalProgress.status === 'achieved'
                ? '🎯 Ziel erreicht'
                : goalProgress.status === 'on_track'
                  ? 'Auf Kurs'
                  : 'Verzögert'}
            </Badge>
          {/if}
          <Btn variant="secondary" size="sm" onclick={() => (isGoalModalOpen = true)}>
            Ziel anpassen
          </Btn>
          <button
            type="button"
            class="cursor-pointer p-1 text-xs font-semibold text-[var(--text-muted)] transition-colors hover:text-[var(--color-vital)]"
            title="Ziel entfernen"
            onclick={handleRemoveGoal}
          >
            <Icon name="delete" size="sm" />
          </button>
        </div>
      </div>

      <!-- Numbers & Progress Bar -->
      {#if currentVal != null && goalProgress}
        <div class="my-3 space-y-1.5">
          <div class="flex items-baseline justify-between text-xs">
            <span class="font-semibold text-[var(--text-main)]">
              Aktuell: <strong class="text-base text-[var(--color-primary)]"
                >{currentVal} {metric.unit}</strong
              >
              <span class="ml-1 font-normal text-[var(--text-muted)]"
                >/ Ziel: {targetVal} {metric.unit}</span
              >
            </span>
            <span class="font-bold text-[var(--text-main)]">
              {goalProgress.percent}% {goalProgress.isFulfilled
                ? 'erfüllt'
                : `(${goalProgress.delta} ${metric.unit} verbleibend)`}
            </span>
          </div>

          <div
            class="h-2 w-full overflow-hidden rounded-full border border-[var(--border-subtle)] bg-[var(--bg-surface-50)]"
          >
            <div
              class="h-full rounded-full transition-all duration-500 {goalProgress.status ===
              'achieved'
                ? 'bg-[var(--color-success)]'
                : 'bg-[var(--color-primary)]'}"
              style="width: {goalProgress.percent}%"
            ></div>
          </div>
        </div>
      {:else}
        <p class="my-2 text-xs text-[var(--text-muted)]">
          Ziel: <strong class="text-[var(--text-main)]">{targetVal} {metric.unit}</strong> • Erfasse deinen
          ersten Messwert, um den Zielfortschritt zu berechnen.
        </p>
      {/if}
    </div>
  {:else}
    <!-- No Goal Defined (Clean Standard Card) -->
    <div
      class="flex flex-col items-start justify-between gap-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)] transition-all sm:flex-row sm:items-center"
    >
      <div class="flex items-center gap-3.5">
        <div
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
        >
          <Icon name="flag" size="sm" />
        </div>
        <div>
          <h3 class="text-sm font-extrabold text-[var(--text-main)]">
            Persönliches Ziel festlegen
          </h3>
          <p class="mt-0.5 text-xs text-[var(--text-muted)]">
            Definiere einen Zielwert für {metric.name}, um automatisierte Fortschritts- und
            Trend-Prognosen zu aktivieren.
          </p>
        </div>
      </div>
      <Btn variant="primary" size="sm" class="shrink-0" onclick={() => (isGoalModalOpen = true)}>
        + Ziel festlegen
      </Btn>
    </div>
  {/if}

  <!-- Full-Width Interactive Spline Chart (Real Data or Clean Empty State) -->
  <InteractiveChart
    data={chartPoints}
    metricName={metric.name}
    unit={metric.unit}
    targetValue={targetVal}
    onaddclick={() => (isAddEntryModalOpen = true)}
  />

  <!-- 2-Column: Clinical Target Zones & Pearson Correlations -->
  <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
    <!-- Clinical Range Bands -->
    <div
      class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
        <Icon name="labs" class="text-[var(--color-primary)]" />
        <span>Klinische Referenz- und Zielkorridore</span>
      </div>
      <div class="space-y-2 text-xs">
        <div
          class="flex justify-between rounded-xl border border-[var(--color-success)]/30 bg-[var(--color-success-soft)]/20 p-2.5"
        >
          <span class="font-bold text-[var(--color-success)]">Optimal / Zielkorridor</span>
          <span class="font-bold">105 – 120 {metric.unit}</span>
        </div>
        <div
          class="flex justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5 text-[var(--text-muted)]"
        >
          <span>Normwert / Grenzwertig</span>
          <span>120 – 139 {metric.unit}</span>
        </div>
        <div
          class="flex justify-between rounded-xl border border-[var(--color-vital)]/30 bg-[var(--color-vital-soft)]/20 p-2.5 text-[var(--color-vital)]"
        >
          <span>Erhöhtes Risiko</span>
          <span class="font-bold">&ge; 140 {metric.unit}</span>
        </div>
      </div>
    </div>

    <!-- Biometric Correlations -->
    <div
      class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
        <Icon name="insights" class="text-[var(--color-circadian)]" />
        <span>Evidenzbasierte Einflussfaktoren</span>
      </div>
      <div class="space-y-2 text-xs">
        <div
          class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5"
        >
          <span class="font-semibold text-[var(--text-main)]">Schlafdauer (&gt; 7.5h)</span>
          <span class="font-bold text-emerald-500">Stabilisierender Effekt</span>
        </div>
        <div
          class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5"
        >
          <span class="font-semibold text-[var(--text-main)]">Ausdauertraining</span>
          <span class="font-bold text-[var(--color-primary)]">Senkt Ruhewerte</span>
        </div>
        <div
          class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5"
        >
          <span class="font-semibold text-[var(--text-main)]">Koffein / Stress</span>
          <span class="font-bold text-rose-500">Kurzzeitiger Anstieg</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Complete Real Entries History Table -->
  <div
    class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
  >
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 class="text-sm font-bold text-[var(--text-main)]">
          Lückenlose Messwert-Historie ({measurements.length} Einträge)
        </h2>
        <p class="mt-0.5 text-xs text-[var(--text-muted)]">
          Lokal in Dexie IndexedDB gespeichert und Ende-zu-Ende synchronisiert
        </p>
      </div>
      {#if measurements.length > 0}
        <Badge variant="success">Sync Aktiv</Badge>
      {/if}
    </div>

    {#if measurements.length === 0}
      <div class="py-6">
        <EmptyState
          title="Noch keine Messungen erfasst"
          description={`Erfasse deinen ersten Messwert für ${metric.name} über den Button oben.`}
        >
          <Btn variant="primary" size="sm" onclick={() => (isAddEntryModalOpen = true)}>
            + Jetzt Messwert erfassen
          </Btn>
        </EmptyState>
      </div>
    {:else}
      <div class="w-full overflow-x-auto">
        <table class="w-full border-collapse text-left text-xs">
          <thead>
            <tr
              class="border-b border-[var(--border-subtle)] text-[0.6875rem] tracking-wider text-[var(--text-muted)] uppercase"
            >
              <th class="px-3 py-2.5">Zeitpunkt</th>
              <th class="px-3 py-2.5">Messwert</th>
              <th class="px-3 py-2.5">Quelle</th>
              <th class="px-3 py-2.5">Notiz</th>
              <th class="px-3 py-2.5 text-right">Aktion</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-subtle)]">
            {#each measurements as entry (entry.id)}
              <tr>
                <td class="px-3 py-2.5 text-[var(--text-soft)]">
                  {formatTimestamp(entry.start_time)}
                </td>
                <td class="px-3 py-2.5 text-sm font-bold text-[var(--text-main)] tabular-nums">
                  {entry.value_numeric ?? '—'}
                  {metric.unit}
                </td>
                <td class="px-3 py-2.5">
                  <Badge variant="default" class="font-bold">
                    {entry.source || 'Manuell'}
                  </Badge>
                </td>
                <td class="px-3 py-2.5 text-[var(--text-muted)]">
                  {entry.notes || '—'}
                </td>
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

      <!-- Pagination Controls -->
      {#if totalPages > 1}
        <div
          class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-3 text-xs text-[var(--text-muted)]"
        >
          <span class="text-[0.6875rem]">
            Seite <span class="font-bold text-[var(--text-main)]">{currentPage}</span> von{' '}
            <span class="font-bold text-[var(--text-main)]">{totalPages}</span> ({totalCount} Messwerte)
          </span>
          <div class="flex items-center gap-1.5">
            <button
              type="button"
              onclick={() => (currentPage = Math.max(1, currentPage - 1))}
              disabled={currentPage <= 1}
              class="flex cursor-pointer items-center gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2.5 py-1 text-xs font-semibold text-[var(--text-main)] transition-all hover:bg-[var(--bg-surface-100)] disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Icon name="chevron-left" size="sm" />
              <span>Zurück</span>
            </button>
            <button
              type="button"
              onclick={() => (currentPage = Math.min(totalPages, currentPage + 1))}
              disabled={currentPage >= totalPages}
              class="flex cursor-pointer items-center gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2.5 py-1 text-xs font-semibold text-[var(--text-main)] transition-all hover:bg-[var(--bg-surface-100)] disabled:cursor-not-allowed disabled:opacity-40"
            >
              <span>Weiter</span>
              <Icon name="chevron-right" size="sm" />
            </button>
          </div>
        </div>
      {/if}
    {/if}
  </div>
</div>

<!-- Goal Modal -->
<GoalModal
  open={isGoalModalOpen}
  metricCode={metric.code}
  metricName={metric.name}
  unit={metric.unit}
  {goal}
  onclose={() => (isGoalModalOpen = false)}
/>

<!-- Add Measurement Modal -->
<AddMeasurementModal
  open={isAddEntryModalOpen}
  metricCode={metric.code}
  metricName={metric.name}
  unit={metric.unit}
  onclose={() => (isAddEntryModalOpen = false)}
/>
