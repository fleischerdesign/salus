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

  const rhrQuery = useQuery(
    async () => {
      const dayStart = date + 'T00:00:00';
      const dayEnd = date + 'T23:59:59.999';

      const measurements = await db.measurement
        .where('start_time')
        .between(dayStart, dayEnd)
        .toArray();

      const valid = measurements.filter((m) => !m.deleted_at);
      const rhrVal = valid.find(
        (m) => m.metric_code === 'heart_rate_resting' || m.metric_code === 'heart_rate'
      )?.value_numeric;

      return rhrVal ?? null;
    },
    () => date
  );

  const liveRhr = $derived(rhrQuery.value);
  const rhr = $derived(liveRhr !== null ? liveRhr : preview ? 64 : null);
  const hasData = $derived(rhr !== null);

  const badgeText = $derived(
    !hasData ? 'Kein Eintrag' : rhr! <= 60 ? 'Athletisch' : rhr! <= 75 ? 'Optimal' : 'Erhöht'
  );

  const badgeVariant = $derived(
    !hasData ? 'default' : rhr! <= 60 ? 'success' : rhr! <= 75 ? 'primary' : 'warning'
  );
</script>

<WidgetCard
  title="Ruhepuls (RHR)"
  subtitle="Schlaf- & Ruhemessung"
  icon="ecg-heart"
  iconColor="var(--color-vital)"
  {badgeText}
  {badgeVariant}
  empty={!hasData}
  emptyText="Kein Ruhepuls für dieses Datum erfasst"
>
  <div class="space-y-3 pt-1">
    <div class="flex items-baseline gap-2">
      <span class="text-4xl font-extrabold tracking-tight text-text-main tabular-nums">
        {rhr}
      </span>
      <span class="text-xs font-bold text-text-muted">bpm</span>
    </div>

    <!-- Heart rate zone visual indicator -->
    <div class="flex items-center gap-2 pt-2 text-xs">
      <div class="flex h-2 flex-1 overflow-hidden rounded-full bg-surface-200">
        <div
          class="h-full rounded-full transition-all duration-500 {rhr! <= 60
            ? 'bg-emerald-500'
            : rhr! <= 75
              ? 'bg-cyan-500'
              : 'bg-amber-500'}"
          style="width: {Math.min(100, Math.max(10, ((rhr! - 40) / (100 - 40)) * 100))}%;"
        ></div>
      </div>
      <span class="font-mono text-[0.625rem] text-text-muted">Ziel &lt; 65</span>
    </div>
  </div>

  {#snippet footer()}
    <span>Gemessen während der tiefsten Erholungsphase der Nacht</span>
  {/snippet}
</WidgetCard>
