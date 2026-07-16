<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { createMeasurement } from '$lib/mutations/measurement';

  // Query water metric and today's measurements
  const waterData = liveQuery(async () => {
    const metric = await db.metric_definition.where('source_data_type').equals('water').first();
    if (!metric) return { total: 0, goal: 2500, metricCode: '' };

    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
    const todayEnd = new Date();
    todayEnd.setHours(23, 59, 59, 999);

    const measurements = await db.measurement.where('metric_code').equals(metric.code).toArray();

    const todayMeasurements = measurements.filter((m) => {
      if (m.deleted_at) return false;
      const t = new Date(m.start_time).getTime();
      return t >= todayStart.getTime() && t <= todayEnd.getTime();
    });

    const total = todayMeasurements.reduce((sum, m) => sum + (m.value_numeric ?? 0), 0);
    const goal = await db.goal.where('metric_code').equals(metric.code).first();

    return {
      total,
      goal: goal?.target_value ?? 2500,
      metricCode: metric.code
    };
  });

  let total = $derived($waterData?.total ?? 0);
  let goal = $derived($waterData?.goal ?? 2500);
  let metricCode = $derived($waterData?.metricCode ?? '');

  let percent = $derived(Math.min(100, Math.round((total / goal) * 100)));

  let logging = $state(false);

  async function logWater(amount: number) {
    if (!metricCode || logging) return;
    logging = true;
    try {
      await createMeasurement(metricCode, {
        value_numeric: amount,
        data_type: 'water',
        start_time: new Date().toISOString()
      });
    } catch (err) {
      console.error('Failed to log water intake:', err);
    } finally {
      logging = false;
    }
  }
</script>

<div class="flex h-full flex-col items-center justify-between gap-4 p-2">
  <!-- Visual Glass Display -->
  <div
    class="relative flex h-32 w-full max-w-[140px] flex-col items-center justify-center select-none"
  >
    <!-- Water level cup mask -->
    <div
      class="relative flex h-28 w-20 flex-col justify-end overflow-hidden rounded-b-2xl border-4 border-t-0 border-surface-200 bg-surface-50/50 shadow-inner"
    >
      <!-- Water liquid filling -->
      <div
        class="relative flex w-full items-center justify-center bg-gradient-to-t from-cyan-500 to-cyan-400 transition-all duration-500 ease-out"
        style="height: {percent}%"
      >
        <!-- Subtle wave wave-top overlay -->
        {#if percent > 0 && percent < 100}
          <div class="absolute -top-1 right-0 left-0 h-1 bg-cyan-300 opacity-55 blur-[0.5px]"></div>
        {/if}
        <!-- Percentage text displayed inside water if high enough, else above -->
        {#if percent >= 25}
          <span class="text-xs font-bold text-white drop-shadow-md select-none">{percent}%</span>
        {/if}
      </div>
    </div>
    {#if percent < 25}
      <span class="absolute text-xs font-bold text-surface-600 select-none">{percent}%</span>
    {/if}
  </div>

  <!-- Quick log controls -->
  <div class="flex w-full flex-col gap-1.5">
    <div class="flex items-center justify-between px-1 text-xs text-surface-500">
      <span class="font-medium text-surface-700">{total} ml</span>
      <span>Goal: {goal} ml</span>
    </div>
    <div class="grid grid-cols-3 gap-1">
      <button
        type="button"
        disabled={logging || !metricCode}
        class="duration-micro rounded-lg border border-surface-200 bg-surface-50 py-1.5 text-xs font-semibold text-cyan-600 transition-all hover:border-cyan-200 hover:bg-cyan-50 active:scale-95 disabled:opacity-50"
        onclick={() => logWater(250)}
      >
        +250ml
      </button>
      <button
        type="button"
        disabled={logging || !metricCode}
        class="duration-micro rounded-lg border border-surface-200 bg-surface-50 py-1.5 text-xs font-semibold text-cyan-600 transition-all hover:border-cyan-200 hover:bg-cyan-50 active:scale-95 disabled:opacity-50"
        onclick={() => logWater(500)}
      >
        +500ml
      </button>
      <button
        type="button"
        disabled={logging || !metricCode}
        class="duration-micro rounded-lg border border-surface-200 bg-surface-50 py-1.5 text-xs font-semibold text-cyan-600 transition-all hover:border-cyan-200 hover:bg-cyan-50 active:scale-95 disabled:opacity-50"
        onclick={() => logWater(750)}
      >
        +750ml
      </button>
    </div>
  </div>
</div>
