<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { sleepDebtCumulative } from '$lib/analytics/stats';
  import Icon from '$components/ui/Icon.svelte';

  const sleepDebtData = liveQuery(async () => {
    const recent = (
      await db.measurement.filter((m) => !m.deleted_at && m.data_type === 'sleep').toArray()
    ).sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());

    const durations: number[] = [];
    for (const m of recent.slice(0, 28)) {
      if (m.value_numeric != null) {
        durations.push(m.value_numeric);
      } else if (m.value_json) {
        try {
          const d = JSON.parse(m.value_json);
          const dur = (d.duration_seconds ?? 0) / 3600;
          if (dur > 0) durations.push(dur);
        } catch {
          /* skip */
        }
      }
    }

    if (durations.length < 3) return null;
    // Calculate cumulative debt (age default 30)
    const debt = sleepDebtCumulative(durations.reverse(), 30);
    const lastDebt = debt.debt[debt.debt.length - 1];
    return {
      cumulativeDebt: Math.round(lastDebt * 10) / 10,
      baselineH: debt.baseline_h
    };
  });

  // Calculate target sleep and wind-down tonight
  const coaching = $derived.by(() => {
    const data = $sleepDebtData;
    if (!data) return null;

    const baseSleep = data.baselineH;
    const debt = Math.max(0, data.cumulativeDebt);

    // Catch-up sleep: distribute debt over 5 days (max 2 hours extra per night)
    const catchUp = Math.min(2.0, debt / 5);
    const targetSleep = baseSleep + catchUp;

    // Wind-down calculation assuming 7:00 AM wakeup target
    const wakeHour = 7;
    // Subtract targetSleep hours from wakeHour
    let sleepTimeDecimal = wakeHour - targetSleep;
    if (sleepTimeDecimal < 0) sleepTimeDecimal += 24;

    const sleepHour = Math.floor(sleepTimeDecimal);
    const sleepMinute = Math.round((sleepTimeDecimal - sleepHour) * 60);

    // Wind-down starts 1.5 hours before sleep time
    let windDownDecimal = sleepTimeDecimal - 1.5;
    if (windDownDecimal < 0) windDownDecimal += 24;

    const windDownHour = Math.floor(windDownDecimal);
    const windDownMinute = Math.round((windDownDecimal - windDownHour) * 60);

    const pad = (n: number) => String(n).padStart(2, '0');

    let advice = 'Your sleep schedule is on track. Keep up the consistent bedtime!';
    if (debt > 5) {
      advice =
        'High sleep debt. Prioritize going to bed early tonight. Avoid screens 1h before sleep.';
    } else if (debt > 2) {
      advice =
        'Moderate sleep debt. A brief 20-minute afternoon nap or 30-min earlier sleep tonight will help.';
    }

    return {
      targetSleep: Math.round(targetSleep * 10) / 10,
      sleepTime: `${pad(sleepHour)}:${pad(sleepMinute)}`,
      windDownTime: `${pad(windDownHour)}:${pad(windDownMinute)}`,
      advice
    };
  });
</script>

<div class="flex flex-col gap-4">
  {#if !$sleepDebtData}
    <div class="flex flex-col items-center justify-center py-6 text-center">
      <Icon name="bedtime" size="2xl" class="text-surface-300" />
      <p class="mt-2 text-xs text-surface-500">
        Requires at least 3 logged nights of sleep to calculate sleep debt.
      </p>
    </div>
  {:else}
    {@const debt = $sleepDebtData.cumulativeDebt}
    <div class="xs:grid-cols-2 grid grid-cols-1 gap-4">
      <!-- Sleep Debt Status Card -->
      <div
        class="flex flex-col justify-between rounded-lg bg-surface-50 p-3 ring-1 ring-surface-100"
      >
        <span class="text-xs font-semibold text-surface-500">Sleep Debt</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span
            class="text-3xl font-extrabold"
            class:text-success-500={debt <= 1.0}
            class:text-warning-500={debt > 1.0 && debt <= 4.0}
            class:text-error-500={debt > 4.0}
          >
            {debt > 0 ? `+${debt}` : debt}
          </span>
          <span class="text-xs text-surface-400">hours</span>
        </div>
        <div class="mt-3 flex items-center gap-1">
          {#if debt <= 1.0}
            <span class="inline-block h-2 w-2 rounded-full bg-success-500"></span>
            <span class="text-[10px] font-bold text-success-600">Optimal Rest</span>
          {:else if debt <= 4.0}
            <span class="inline-block h-2 w-2 rounded-full bg-warning-500"></span>
            <span class="text-[10px] font-bold text-warning-600">Mild Deficit</span>
          {:else}
            <span class="inline-block h-2 w-2 rounded-full bg-error-500"></span>
            <span class="text-[10px] font-bold text-error-600">Sleep Deprived</span>
          {/if}
        </div>
      </div>

      <!-- Optimal Wind Down Card -->
      {#if coaching}
        <div
          class="flex flex-col justify-between rounded-lg bg-surface-50 p-3 ring-1 ring-surface-100"
        >
          <span class="text-xs font-semibold text-surface-500">Optimal Wind-down</span>
          <div class="mt-2 flex items-baseline gap-1 text-primary-600">
            <span class="text-3xl font-extrabold">{coaching.windDownTime}</span>
            <span class="text-xs font-medium text-surface-400">PM</span>
          </div>
          <span class="mt-3 text-[10px] text-surface-400">
            Target sleep: {coaching.targetSleep}h (at {coaching.sleepTime})
          </span>
        </div>
      {/if}
    </div>

    <!-- Personalized Sleep Advice -->
    {#if coaching}
      <div
        class="flex gap-2.5 rounded-lg bg-primary-50/50 p-3 text-xs text-primary-700 ring-1 ring-primary-100/50"
      >
        <div class="mt-0.5">
          <Icon name="info" size="sm" />
        </div>
        <p class="leading-relaxed">
          {coaching.advice}
        </p>
      </div>
    {/if}
  {/if}
</div>
