<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Modal from '../ui/Modal.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { fetchGoalViews } from '$lib/analytics/views/goal-views';
  import { createGoal } from '$lib/mutations/goal';
  import { db } from '$lib/db/database';

  // 1. Reactive Dexie Goal Views
  const goalsQuery = useQuery(() => fetchGoalViews());
  const goalViews = $derived(goalsQuery.value ?? []);
  const loading = $derived(goalsQuery.loading);

  const metricsQuery = useQuery(() => db.metric_definition.toArray());
  const metrics = $derived(metricsQuery.value ?? []);

  let isCreateOpen = $state(false);
  let selectedMetric = $state('weight');
  let targetVal = $state('80');
  let direction = $state<'decrease' | 'increase'>('decrease');
  let frequency = $state('daily');

  let metricOptions = $derived(
    metrics.map((m) => ({ value: m.code, label: `${m.name} (${m.unit || 'Wert'})` }))
  );

  async function handleCreate() {
    const val = parseFloat(targetVal);
    if (isNaN(val)) return;
    await createGoal(selectedMetric, val, direction, frequency);
    isCreateOpen = false;
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Gesundheitsziele und Prognosen</h1>
      <p class="mt-0.5 text-sm text-text-muted">
        Mathematische Zielverfolgung mit statistischen Prognosen bis zur Deadline
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Btn variant="primary" size="sm" onclick={() => (isCreateOpen = true)}>
        + Neues Ziel anlegen
      </Btn>
    </div>
  </div>

  <!-- Goals Grid -->
  {#if loading}
    <div class="py-12 text-center text-sm text-text-muted">Ziele werden geladen...</div>
  {:else if goalViews.length === 0}
    <div
      class="space-y-3 rounded-2xl border border-border-subtle bg-surface-0 p-8 text-center shadow-card"
    >
      <div
        class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary-soft text-primary"
      >
        <Icon name="flag" size="lg" />
      </div>
      <div>
        <h3 class="text-base font-bold text-text-main">Keine aktiven Ziele definiert</h3>
        <p class="mx-auto mt-1 max-w-sm text-xs text-text-muted">
          Setze dir messbare Gesundheitsziele für Körpergewicht, Blutdruck, Schritte oder Schlaf, um
          Fortschritt und Projektionen zu verfolgen.
        </p>
      </div>
      <Btn variant="primary" size="sm" onclick={() => (isCreateOpen = true)}>
        Jetzt erstes Ziel festlegen
      </Btn>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      {#each goalViews as g (g.id)}
        {@const status = g.progress.is_fulfilled
          ? 'achieved'
          : g.forecast?.on_track
            ? 'on_track'
            : 'off_track'}
        <div
          class="flex flex-col justify-between rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card"
        >
          <div>
            <div class="mb-3 flex items-start justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-soft/20 text-primary"
                >
                  <Icon name={g.metric_icon || 'flag'} size={18} />
                </div>
                <div>
                  <h2 class="text-sm font-bold text-text-main">{g.metric_name}</h2>
                  <span class="text-xs text-text-muted"
                    >{g.frequency} {g.deadline ? `• Frist: ${g.deadline}` : ''}</span
                  >
                </div>
              </div>

              <Badge
                variant={status === 'achieved'
                  ? 'success'
                  : status === 'on_track'
                    ? 'primary'
                    : 'vital'}
              >
                {status === 'achieved'
                  ? 'Erreicht'
                  : status === 'on_track'
                    ? 'Auf Kurs'
                    : 'Verzögert'}
              </Badge>
            </div>

            <!-- Progress Numbers -->
            <div class="my-2 flex items-baseline gap-2 font-mono">
              <span class="text-2xl font-extrabold text-text-main">
                {g.progress.current_value !== null ? g.progress.current_value : '—'}
              </span>
              <span class="text-xs text-text-muted">/ {g.target_value} {g.metric_unit}</span>
            </div>

            <!-- Progress Bar -->
            <div
              class="my-2 h-2 w-full overflow-hidden rounded-full border border-border-subtle bg-surface-50"
            >
              <div
                class="h-full rounded-full transition-all duration-500 {status === 'achieved'
                  ? 'bg-success'
                  : 'bg-primary'}"
                style="width: {g.progress.percent}%"
              ></div>
            </div>
          </div>

          <!-- Statistical Projection Footer -->
          {#if g.forecast}
            <div
              class="mt-4 flex items-center justify-between border-t border-border-subtle pt-3 font-mono text-xs text-text-soft"
            >
              <span
                >Projektion: <strong class="text-text-main"
                  >{g.forecast.predicted.toFixed(1)} {g.metric_unit}</strong
                ></span
              >
              <span>CI: [{g.forecast.ci_lower.toFixed(1)} – {g.forecast.ci_upper.toFixed(1)}]</span>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}

  <!-- Create Goal Modal -->
  <Modal
    open={isCreateOpen}
    title="Neues Ziel festlegen"
    subtitle="Definiere biometrische Meilensteine und Verlaufsziele"
    icon="flag"
    onclose={() => (isCreateOpen = false)}
  >
    <form
      onsubmit={(e) => {
        e.preventDefault();
        handleCreate();
      }}
      class="space-y-4"
    >
      <Select label="Metrik auswählen" options={metricOptions} bind:value={selectedMetric} />

      <Input
        label="Zielwert"
        type="number"
        bind:value={targetVal}
        placeholder="z. B. 75"
        required
      />

      <Select
        label="Richtung"
        options={[
          { value: 'decrease', label: 'Wert verringern (z. B. Gewicht, KFA, Blutdruck)' },
          { value: 'increase', label: 'Wert steigern (z. B. Schritte, Schlaf, Muskelmasse)' }
        ]}
        bind:value={direction}
      />

      <div class="flex justify-end gap-2 border-t border-border-subtle pt-3">
        <Btn variant="secondary" size="md" onclick={() => (isCreateOpen = false)}>Abbrechen</Btn>
        <Btn variant="primary" size="md" type="submit" disabled={!targetVal}>Ziel speichern</Btn>
      </div>
    </form>
  </Modal>
</div>
