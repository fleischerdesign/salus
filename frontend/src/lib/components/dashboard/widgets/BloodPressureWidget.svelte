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

  const bpQuery = useQuery(
    async () => {
      const dayStart = date + 'T00:00:00';
      const dayEnd = date + 'T23:59:59.999';

      const measurements = await db.measurement
        .where('start_time')
        .between(dayStart, dayEnd)
        .toArray();

      const valid = measurements.filter((m) => !m.deleted_at);
      const sys = valid.find((m) => m.metric_code === 'systolic_bp')?.value_numeric ?? null;
      const dia = valid.find((m) => m.metric_code === 'diastolic_bp')?.value_numeric ?? null;

      return { sys, dia };
    },
    () => date
  );

  const bp = $derived(bpQuery.value);
  const liveSys = $derived(bp?.sys ?? null);
  const liveDia = $derived(bp?.dia ?? null);

  const systolic = $derived(liveSys !== null ? liveSys : preview ? 118 : null);
  const diastolic = $derived(liveDia !== null ? liveDia : preview ? 76 : null);
  const hasData = $derived(systolic !== null && diastolic !== null);

  const pressurePercent = $derived(
    systolic !== null ? Math.min(100, Math.max(0, ((systolic - 90) / (160 - 90)) * 100)) : 0
  );

  const badgeText = $derived(
    !hasData
      ? 'Kein Eintrag'
      : systolic! <= 120 && diastolic! <= 80
        ? 'Optimal (ESC 2024)'
        : systolic! <= 130
          ? 'Normal'
          : 'Erhöht'
  );

  const badgeVariant = $derived(
    !hasData
      ? 'default'
      : systolic! <= 120 && diastolic! <= 80
        ? 'success'
        : systolic! <= 130
          ? 'primary'
          : 'vital'
  );
</script>

<WidgetCard
  title="Arterieller Blutdruck"
  subtitle="Systolisch / Diastolisch"
  icon="vital-signs"
  iconColor="var(--color-vital)"
  {badgeText}
  {badgeVariant}
  empty={!hasData}
  emptyText="Kein Blutdruckeintrag für dieses Datum"
>
  <div class="space-y-4 pt-1">
    <div class="flex items-baseline gap-2">
      <span class="text-3xl font-extrabold tracking-tight text-[var(--text-main)] tabular-nums">
        {systolic}
      </span>
      <span class="text-xl font-bold text-[var(--text-muted)] tabular-nums">
        / {diastolic}
      </span>
      <span class="text-xs font-semibold text-[var(--text-muted)]">mmHg</span>
    </div>

    <div class="space-y-1.5 pt-1">
      <div class="relative flex h-2.5 overflow-hidden rounded-full bg-[var(--bg-surface-200)]">
        <div class="h-full w-[42%] bg-emerald-500"></div>
        <div class="h-full w-[15%] bg-teal-400"></div>
        <div class="h-full w-[15%] bg-amber-400"></div>
        <div class="h-full flex-1 bg-rose-500"></div>
        <div
          class="absolute top-0 bottom-0 w-2.5 -translate-x-1/2 rounded-full border-2 border-slate-900 bg-white shadow-md transition-all duration-500"
          style="left: {pressurePercent}%;"
        ></div>
      </div>
      <div
        class="flex justify-between px-0.5 text-[0.625rem] font-semibold text-[var(--text-muted)]"
      >
        <span>90</span>
        <span class="font-bold text-emerald-500">120 (Optimal)</span>
        <span class="font-bold text-amber-500">130</span>
        <span class="font-bold text-rose-500">160+</span>
      </div>
    </div>
  </div>

  {#snippet footer()}
    <span>Zuletzt gemessen in Ruhehaltung &bull; Leitlinie ESC/ESH 2024</span>
  {/snippet}
</WidgetCard>
