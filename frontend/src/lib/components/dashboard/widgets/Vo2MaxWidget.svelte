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

  const vo2Query = useQuery(
    async () => {
      const dayStart = date + 'T00:00:00';
      const dayEnd = date + 'T23:59:59.999';

      const measurements = await db.measurement
        .where('start_time')
        .between(dayStart, dayEnd)
        .toArray();

      const valid = measurements.filter((m) => !m.deleted_at);
      const val = valid.find(
        (m) => m.metric_code === 'vo2_max' || m.metric_code === 'vo2max'
      )?.value_numeric;

      return val ?? null;
    },
    () => date
  );

  const liveVo2 = $derived(vo2Query.value);
  const vo2max = $derived(liveVo2 !== null ? liveVo2 : preview ? 48.5 : null);
  const hasData = $derived(vo2max !== null);

  const badgeText = $derived(
    !hasData ? 'Kein Eintrag' : vo2max! >= 50 ? 'Exzellent' : vo2max! >= 42 ? 'Gut' : 'Moderat'
  );

  const badgeVariant = $derived(
    !hasData ? 'default' : vo2max! >= 50 ? 'success' : vo2max! >= 42 ? 'primary' : 'warning'
  );
</script>

<WidgetCard
  title="Kardiorespiratorische Fitness (VO2max)"
  subtitle="Maximale Sauerstoffaufnahme"
  icon="directions-run"
  iconColor="var(--color-activity)"
  {badgeText}
  {badgeVariant}
  empty={!hasData}
  emptyText="Kein VO2max-Wert für dieses Datum erfasst"
>
  <div class="space-y-3 pt-1">
    <div class="flex items-baseline gap-2">
      <span class="text-4xl font-extrabold tracking-tight text-text-main tabular-nums">
        {vo2max}
      </span>
      <span class="text-xs font-bold text-text-muted">mL/kg/min</span>
    </div>

    <div class="flex items-center gap-2 pt-2 text-xs">
      <div class="flex h-2 flex-1 overflow-hidden rounded-full bg-surface-200">
        <div
          class="h-full rounded-full transition-all duration-500 {vo2max! >= 50
            ? 'bg-emerald-500'
            : vo2max! >= 42
              ? 'bg-cyan-500'
              : 'bg-amber-500'}"
          style="width: {Math.min(100, Math.max(10, ((vo2max! - 30) / (65 - 30)) * 100))}%;"
        ></div>
      </div>
      <span class="font-mono text-[0.625rem] text-text-muted">Perzentil &gt; 85%</span>
    </div>
  </div>

  {#snippet footer()}
    <span>Schätzung basierend auf GPS-Laufaktivitäten &amp; Herzfrequenz</span>
  {/snippet}
</WidgetCard>
