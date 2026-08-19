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

  const glucoseQuery = useQuery(
    async () => {
      const dayStart = date + 'T00:00:00';
      const dayEnd = date + 'T23:59:59.999';

      const measurements = await db.measurement
        .where('start_time')
        .between(dayStart, dayEnd)
        .toArray();

      const valid = measurements.filter((m) => !m.deleted_at);
      const val = valid.find(
        (m) => m.metric_code === 'blood_glucose' || m.metric_code === 'glucose'
      )?.value_numeric;

      return val ?? null;
    },
    () => date
  );

  const liveGlucose = $derived(glucoseQuery.value);
  const glucose = $derived(liveGlucose !== null ? liveGlucose : preview ? 88 : null);
  const hasData = $derived(glucose !== null);

  const badgeText = $derived(
    !hasData
      ? 'Kein Eintrag'
      : glucose! >= 70 && glucose! <= 100
        ? 'Optimal Nüchtern'
        : glucose! <= 140
          ? 'Normal Postprandial'
          : 'Erhöht'
  );

  const badgeVariant = $derived(
    !hasData
      ? 'default'
      : glucose! >= 70 && glucose! <= 100
        ? 'success'
        : glucose! <= 140
          ? 'primary'
          : 'warning'
  );
</script>

<WidgetCard
  title="Blutzucker"
  subtitle="Nüchtern / Glukoseprofil"
  icon="science"
  iconColor="var(--color-vital)"
  {badgeText}
  {badgeVariant}
  empty={!hasData}
  emptyText="Kein Glukosewert für dieses Datum erfasst"
>
  <div class="space-y-3 pt-1">
    <div class="flex items-baseline gap-2">
      <span class="text-4xl font-extrabold tracking-tight text-text-main tabular-nums">
        {glucose}
      </span>
      <span class="text-xs font-bold text-text-muted">mg/dL</span>
    </div>

    <!-- Glucose range bar -->
    <div class="flex items-center gap-2 pt-2 text-xs">
      <div class="flex h-2 flex-1 overflow-hidden rounded-full bg-surface-200">
        <div
          class="h-full rounded-full transition-all duration-500 {glucose! <= 100
            ? 'bg-emerald-500'
            : glucose! <= 140
              ? 'bg-cyan-500'
              : 'bg-amber-500'}"
          style="width: {Math.min(100, Math.max(10, ((glucose! - 50) / (200 - 50)) * 100))}%;"
        ></div>
      </div>
      <span class="font-mono text-[0.625rem] text-text-muted">70–100 Ziel</span>
    </div>
  </div>

  {#snippet footer()}
    <span>Kapillare Blutzuckermessung / CGM-Sensor</span>
  {/snippet}
</WidgetCard>
