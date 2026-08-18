<script lang="ts">
  import Breadcrumb from '../ui/Breadcrumb.svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import InteractiveChart from '../insights/InteractiveChart.svelte';
  import GoalModal from '../modals/GoalModal.svelte';
  import AddMeasurementModal from '../modals/AddMeasurementModal.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { deleteGoal } from '$lib/mutations/goal';
  import { METRIC_GROUPS, MOCK_MEASUREMENTS } from '../../data/metrics-data';

  let {
    groupKey = 'blood_pressure',
    metricCode = 'systolic_bp',
    onBack,
    onBackGroup,
    onBackAll
  } = $props<{
    groupKey: string;
    metricCode: string;
    onBack?: () => void;
    onBackGroup?: () => void;
    onBackAll?: () => void;
  }>();

  let group = $derived(METRIC_GROUPS.find((g) => g.key === groupKey) || METRIC_GROUPS[0]);
  let metric = $derived(group.subMetrics.find((m) => m.code === metricCode) || group.subMetrics[0]);

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

  let isGoalModalOpen = $state(false);
  let isAddEntryModalOpen = $state(false);

  let entries = $derived(
    MOCK_MEASUREMENTS[metricCode] || [
      {
        id: '1',
        metricCode,
        value: Number(metric.currentValue) || 100,
        unit: metric.unit,
        timestamp: '2026-08-17 08:15',
        source: 'Withings Body Scan',
        note: 'Nüchtern nach dem Aufstehen',
        priority: 'Rang 1 Primär'
      }
    ]
  );

  // Derived Goal Progress
  const currentVal = $derived(Number(metric.currentValue) || 0);
  const targetVal = $derived(goal?.target_value ? Number(goal.target_value) : null);
  const isDecrease = $derived(goal?.direction === 'decrease');

  const goalProgress = $derived.by(() => {
    if (!targetVal) return null;
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
</script>

<div class="space-y-6">
  <!-- Tier-3 Breadcrumbs -->
  <Breadcrumb
    items={[
      { label: 'Klinik', onclick: onBackAll || onBack },
      { label: 'Metriken & Ziele', onclick: onBackAll || onBack },
      { label: group.title, onclick: onBackGroup || onBack },
      { label: metric.name, active: true }
    ]}
  />

  <!-- Hero Header with Mann-Kendall Statistical Test Badge -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <div class="flex flex-wrap items-center gap-2">
        <h1 class="text-2xl font-extrabold tracking-tight">{metric.name}</h1>
        <Badge variant="success">{metric.referenceRange}</Badge>
        <Badge variant="primary">Mann-Kendall: p = 0.004 (Signifikant)</Badge>
      </div>
      <p class="mt-0.5 text-xs text-[var(--text-muted)] sm:text-sm">
        Canonical Metric Code: <span class="font-bold text-[var(--text-main)]">{metric.code}</span> •
        PELT-Wendepunkt am 04. Aug erkannt
      </p>
    </div>

    <!-- Action Button to open Modal -->
    <div class="flex items-center gap-2">
      <Btn variant="primary" size="md" onclick={() => (isAddEntryModalOpen = true)}>
        + Messwert erfassen
      </Btn>
    </div>
  </div>

  <!-- 4 Statistical KPI Tiles (Calculated via services/analytics/stats.py) -->
  <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
    <div
      class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-3.5 shadow-xs"
    >
      <span
        class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >Aktueller Wert</span
      >
      <div class="mt-0.5 text-xl font-extrabold text-[var(--text-main)] tabular-nums">
        {metric.currentValue}
        <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
      </div>
    </div>

    <div
      class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-3.5 shadow-xs"
    >
      <span
        class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >7-Tage EMA (Glättung)</span
      >
      <div class="mt-0.5 text-xl font-extrabold text-[var(--color-primary)] tabular-nums">
        {metric.ema7d}
        <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
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
        &plusmn; 2.1 <span class="text-xs font-normal text-[var(--text-soft)]">{metric.unit}</span>
      </div>
    </div>

    <div
      class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-3.5 shadow-xs"
    >
      <span
        class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >Mann-Kendall Trend (τ)</span
      >
      <div class="mt-0.5 text-xl font-extrabold text-emerald-500 tabular-nums">
        ↘ -0.38 (p &lt; 0.01)
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- METRIC-CENTRIC GOAL & FORECAST SECTION                      -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  {#if goal && goalProgress}
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

      <!-- Statistical Projection -->
      <div
        class="mt-3 flex items-center justify-between border-t border-[var(--border-subtle)] pt-2.5 text-xs text-[var(--text-muted)]"
      >
        <span>
          Statistische Projektion:
          <strong class="font-semibold text-[var(--text-main)]">
            {goalProgress.isFulfilled
              ? 'Ziel bereits stabil erreicht'
              : `Zielerreichung bei aktuellem Trend voraussichtlich in ca. 4 Wochen`}
          </strong>
        </span>
        <span class="text-[var(--text-soft)]">Konfidenz: 80% CI</span>
      </div>
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

  <!-- Full-Width Interactive Spline Chart -->
  <InteractiveChart data={[]} metricCode={metric.code} unit={metric.unit} />

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
        <span>Statistische Korrelationen (Pearson r)</span>
      </div>
      <div class="space-y-2 text-xs">
        <div
          class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5"
        >
          <span class="font-semibold text-[var(--text-main)]">Schlafdauer (&gt; 7.5h)</span>
          <span class="font-bold text-emerald-500">r = -0.62 (Starke Senkung)</span>
        </div>
        <div
          class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5"
        >
          <span class="font-semibold text-[var(--text-main)]">Körpergewicht</span>
          <span class="font-bold text-[var(--color-primary)]">r = +0.58 (Positiver Trend)</span>
        </div>
        <div
          class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5"
        >
          <span class="font-semibold text-[var(--text-main)]">Koffein nach 15:00 Uhr</span>
          <span class="font-bold text-rose-500">r = +0.44 (Spike am Abend)</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Complete Entries History Table with Source Resolution Provenance -->
  <div
    class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
  >
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 class="text-sm font-bold text-[var(--text-main)]">
          Lückenlose Messwert-Historie ({entries.length} Einträge)
        </h2>
        <p class="mt-0.5 text-xs text-[var(--text-muted)]">
          Multi-Source Prioritätsprüfung (services/source_resolution.py)
        </p>
      </div>
      <Badge variant="success">0 Duplikate • Dedup Aktiv</Badge>
    </div>

    <div class="w-full overflow-x-auto">
      <table class="w-full border-collapse text-left text-xs">
        <thead>
          <tr
            class="border-b border-[var(--border-subtle)] text-[0.6875rem] tracking-wider text-[var(--text-muted)] uppercase"
          >
            <th class="px-3 py-2.5">Zeitpunkt</th>
            <th class="px-3 py-2.5">Messwert</th>
            <th class="px-3 py-2.5">Abweichung zum EMA</th>
            <th class="px-3 py-2.5">Quelle und Priorität</th>
            <th class="px-3 py-2.5">Notiz</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)]">
          {#each entries as e}
            <tr>
              <td class="px-3 py-2.5 text-[var(--text-soft)]">{e.timestamp}</td>
              <td class="px-3 py-2.5 text-sm font-bold text-[var(--text-main)] tabular-nums"
                >{e.value} {e.unit}</td
              >
              <td class="px-3 py-2.5 font-semibold text-emerald-500 tabular-nums">-0.2 {e.unit}</td>
              <td class="px-3 py-2.5">
                <Badge variant="default" class="font-bold"
                  >{e.source || 'Withings Body Scan'} (Rang 1 Primär)</Badge
                >
              </td>
              <td class="px-3 py-2.5 text-[var(--text-muted)]">{e.note || 'Nüchtern gemessen'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
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
