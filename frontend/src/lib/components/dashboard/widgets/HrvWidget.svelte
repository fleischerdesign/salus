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

  const hrvQuery = useQuery(
    async () => {
      const dayStart = date + 'T00:00:00';
      const dayEnd = date + 'T23:59:59.999';

      const measurements = await db.measurement
        .where('start_time')
        .between(dayStart, dayEnd)
        .toArray();

      const valid = measurements.filter((m) => !m.deleted_at);
      const val = valid.find(
        (m) =>
          m.metric_code === 'hrv' || m.metric_code === 'hrv_sdnn' || m.metric_code === 'hrv_rmssd'
      )?.value_numeric;

      return val ?? null;
    },
    () => date
  );

  const liveHrv = $derived(hrvQuery.value);
  const hrv = $derived(liveHrv !== null ? liveHrv : preview ? 62 : null);
  const hasData = $derived(hrv !== null);

  const badgeText = $derived(
    !hasData
      ? 'Kein Eintrag'
      : hrv! >= 60
        ? 'Ausgeglichen (Vagus)'
        : hrv! >= 40
          ? 'Normal'
          : 'Belastet'
  );

  const badgeVariant = $derived(
    !hasData ? 'default' : hrv! >= 60 ? 'success' : hrv! >= 40 ? 'primary' : 'warning'
  );
</script>

<WidgetCard
  title="Herzfrequenzvariabilität (HRV)"
  subtitle="Autonomes Nervensystem / Erholung"
  icon="monitoring"
  iconColor="var(--color-vital)"
  {badgeText}
  {badgeVariant}
  empty={!hasData}
  emptyText="Kein HRV-Wert für dieses Datum erfasst"
>
  <div class="space-y-3 pt-1">
    <div class="flex items-baseline gap-2">
      <span class="text-4xl font-extrabold tracking-tight text-[var(--text-main)] tabular-nums">
        {hrv}
      </span>
      <span class="text-xs font-bold text-[var(--text-muted)]">ms (rMSSD)</span>
    </div>

    <div class="flex items-center gap-2 pt-2 text-xs">
      <div class="flex h-2 flex-1 overflow-hidden rounded-full bg-[var(--bg-surface-200)]">
        <div
          class="h-full rounded-full transition-all duration-500 {hrv! >= 60
            ? 'bg-emerald-500'
            : hrv! >= 40
              ? 'bg-cyan-500'
              : 'bg-amber-500'}"
          style="width: {Math.min(100, Math.max(10, ((hrv! - 20) / (100 - 20)) * 100))}%;"
        ></div>
      </div>
      <span class="font-mono text-[0.625rem] text-[var(--text-muted)]">7-Tage-Baseline: 62 ms</span>
    </div>
  </div>

  {#snippet footer()}
    <span>Nächtliche Schwankung der R-R-Intervalle des Herzschlags</span>
  {/snippet}
</WidgetCard>
