<script lang="ts">
  import WidgetCard from '../WidgetCard.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';

  interface Props {
    date?: string;
    config?: Record<string, unknown>;
    preview?: boolean;
    onopen?: (route: string) => void;
  }

  let { date = todayString(), preview = false }: Props = $props();

  const spo2Query = useQuery(
    async () => {
      const dayStart = date + 'T00:00:00';
      const dayEnd = date + 'T23:59:59.999';

      const measurements = await db.measurement
        .where('start_time')
        .between(dayStart, dayEnd)
        .toArray();

      const valid = measurements.filter((m) => !m.deleted_at);
      const val = valid.find((m) => m.metric_code === 'spo2')?.value_numeric;

      return val ?? null;
    },
    () => date
  );

  const liveSpo2 = $derived(spo2Query.value);
  const spo2 = $derived(liveSpo2 !== null ? liveSpo2 : preview ? 98 : null);
  const hasData = $derived(spo2 !== null);

  const badgeText = $derived(
    !hasData ? 'Kein Eintrag' : spo2! >= 95 ? 'Normal (>=95%)' : 'Niedrig'
  );

  const badgeVariant = $derived(!hasData ? 'default' : spo2! >= 95 ? 'success' : 'error');
</script>

<WidgetCard
  title="Blutsauerstoff (SpO2)"
  subtitle="Pulsoxymetrie"
  icon="vital-signs"
  iconColor="var(--color-vital)"
  {badgeText}
  {badgeVariant}
  empty={!hasData}
  emptyText="Kein SpO2-Wert für dieses Datum erfasst"
>
  <div class="space-y-3 pt-1">
    <div class="flex items-baseline gap-2">
      <span class="text-4xl font-extrabold tracking-tight text-text-main tabular-nums">
        {spo2}
      </span>
      <span class="text-xs font-bold text-text-muted">%</span>
    </div>

    <!-- SpO2 indicator bar -->
    <div class="flex items-center gap-2 pt-2 text-xs">
      <div class="flex h-2 flex-1 overflow-hidden rounded-full bg-surface-200">
        <div
          class="h-full rounded-full transition-all duration-500 {spo2! >= 95
            ? 'bg-emerald-500'
            : 'bg-rose-500'}"
          style="width: {Math.min(100, Math.max(10, ((spo2! - 85) / (100 - 85)) * 100))}%;"
        ></div>
      </div>
      <span class="font-mono text-[0.625rem] text-text-muted">Ziel &ge; 95%</span>
    </div>
  </div>

  {#snippet footer()}
    <span>Nächtliche arterielle Sauerstoffsättigung</span>
  {/snippet}
</WidgetCard>
