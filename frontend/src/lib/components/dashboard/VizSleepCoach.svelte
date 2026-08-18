<script lang="ts">
  import Dexie from 'dexie';
  import { db } from '$lib/db/database';
  import { sleepDebtCumulative, extractSleepDurations } from '$lib/analytics/stats';
  import Icon from '$components/ui/Icon.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';

  const sleepDebtDataQuery = useQuery(async () => {
    const recent = await db.measurement
      .where('[metric_code+start_time]')
      .between(['sleep', Dexie.minKey], ['sleep', Dexie.maxKey])
      .filter((m) => !m.deleted_at)
      .reverse()
      .limit(28)
      .toArray();

    const durations = extractSleepDurations(recent);

    if (durations.length < 3) return null;
    // Calculate cumulative debt (age default 30)
    const debt = sleepDebtCumulative(durations.reverse(), 30);
    const lastDebt = debt.debt[debt.debt.length - 1];
    return {
      cumulativeDebt: Math.round(lastDebt * 10) / 10,
      baselineH: debt.baseline_h
    };
  });
  const sleepDebtData = $derived(sleepDebtDataQuery.value);

  // Calculate target sleep and wind-down tonight
  const coaching = $derived.by(() => {
    const data = sleepDebtData;
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

<div class="flex flex-col gap-3 text-xs">
  {#if !sleepDebtData}
    <div class="flex flex-col items-center justify-center py-6 text-center">
      <Icon name="bedtime" size="2xl" class="text-[var(--text-soft)]" />
      <p class="mt-2 text-xs text-[var(--text-muted)]">
        Benötigt mindestens 3 erfasste Schlafeinträge zur Berechnung der Schlafschuld.
      </p>
    </div>
  {:else}
    {@const debt = sleepDebtData.cumulativeDebt}
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <!-- Sleep Debt Status Card -->
      <div
        class="flex flex-col justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5"
      >
        <span class="text-xs font-bold text-[var(--text-muted)]">Schlafschuld</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span
            class="text-2xl font-black tabular-nums {debt <= 1.0
              ? 'text-[var(--color-success)]'
              : debt <= 4.0
                ? 'text-amber-500'
                : 'text-rose-500'}"
          >
            {debt > 0 ? `+${debt}` : debt}
          </span>
          <span class="text-xs font-medium text-[var(--text-soft)]">Std.</span>
        </div>
        <div class="mt-3 flex items-center gap-1.5">
          {#if debt <= 1.0}
            <span class="inline-block h-2 w-2 rounded-full bg-[var(--color-success)]"></span>
            <span class="text-[0.6875rem] font-bold text-[var(--color-success)]"
              >Optimal erholt</span
            >
          {:else if debt <= 4.0}
            <span class="inline-block h-2 w-2 rounded-full bg-amber-500"></span>
            <span class="text-[0.6875rem] font-bold text-amber-500">Leichtes Defizit</span>
          {:else}
            <span class="inline-block h-2 w-2 rounded-full bg-rose-500"></span>
            <span class="text-[0.6875rem] font-bold text-rose-500">Schlafmangel</span>
          {/if}
        </div>
      </div>

      <!-- Optimal Wind Down Card -->
      {#if coaching}
        <div
          class="flex flex-col justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5"
        >
          <span class="text-xs font-bold text-[var(--text-muted)]">Optimale Ruhephase</span>
          <div class="mt-2 flex items-baseline gap-1 text-[var(--color-primary)]">
            <span class="text-2xl font-black tabular-nums">{coaching.windDownTime}</span>
            <span class="text-xs font-bold text-[var(--text-soft)]">Uhr</span>
          </div>
          <span class="mt-3 text-[0.6875rem] text-[var(--text-soft)]">
            Ziel: {coaching.targetSleep}h (ab {coaching.sleepTime} Uhr)
          </span>
        </div>
      {/if}
    </div>

    <!-- Personalized Sleep Advice -->
    {#if coaching}
      <div
        class="flex gap-2.5 rounded-2xl border border-[var(--color-primary)]/20 bg-[var(--color-primary)]/10 p-3.5 text-xs text-[var(--text-main)]"
      >
        <Icon
          name="tips_and_updates"
          size="sm"
          class="mt-0.5 shrink-0 text-[var(--color-primary)]"
        />
        <div class="space-y-1">
          <span class="block font-bold text-[var(--color-primary)]">Schlaf-Empfehlung</span>
          <p class="text-xs leading-relaxed text-[var(--text-muted)]">{coaching.advice}</p>
        </div>
      </div>
    {/if}
  {/if}
</div>
