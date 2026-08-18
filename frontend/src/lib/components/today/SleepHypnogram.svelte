<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    score = null,
    duration = null,
    deepSleep = null,
    remSleep = null,
    lightSleep = null,
    awake = null,
    hrv = null,
    sleepDebtHours = 0,
    baselineHours = 8.0
  } = $props<{
    score?: number | null;
    duration?: string | null;
    deepSleep?: string | null;
    remSleep?: string | null;
    lightSleep?: string | null;
    awake?: string | null;
    hrv?: number | null;
    sleepDebtHours?: number;
    baselineHours?: number;
  }>();

  let hasSleepData = $derived(duration !== null && score !== null);
</script>

<div
  class="space-y-3.5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
>
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-2 text-sm font-bold text-[var(--text-main)]">
      <div
        class="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)]"
      >
        <Icon name="bedtime" size={16} />
      </div>
      <div>
        <span class="block">Schlafarchitektur und Erholung</span>
        <span class="text-xs font-normal text-[var(--text-muted)]">
          {hasSleepData ? 'Schlaf-Tracking aktiv' : 'Noch keine Schlafaufzeichnung für diese Nacht'}
        </span>
      </div>
    </div>
    <div class="flex items-center gap-2">
      {#if hasSleepData}
        {#if hrv !== null}<Badge variant="success">HRV: {hrv} ms</Badge>{/if}
        <Badge variant="primary">{duration} ({score}% Score)</Badge>
      {:else}
        <Badge variant="default">Keine Schlafdaten</Badge>
      {/if}
    </div>
  </div>

  {#if hasSleepData}
    <!-- Hypnogram Stage Wave Canvas -->
    <div class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5">
      <svg class="h-24 w-full" viewBox="0 0 600 100" preserveAspectRatio="none">
        <!-- Grid guide lines -->
        <line
          x1="0"
          y1="20"
          x2="600"
          y2="20"
          stroke="var(--border-subtle)"
          stroke-width="1"
          stroke-dasharray="2 2"
        />
        <line
          x1="0"
          y1="45"
          x2="600"
          y2="45"
          stroke="var(--border-subtle)"
          stroke-width="1"
          stroke-dasharray="2 2"
        />
        <line
          x1="0"
          y1="70"
          x2="600"
          y2="70"
          stroke="var(--border-subtle)"
          stroke-width="1"
          stroke-dasharray="2 2"
        />
        <line
          x1="0"
          y1="95"
          x2="600"
          y2="95"
          stroke="var(--border-subtle)"
          stroke-width="1"
          stroke-dasharray="2 2"
        />

        <!-- Hypnogram Stepped Curve -->
        <path
          d="M 0 45 L 30 70 L 60 95 L 140 95 L 170 45 L 210 20 L 250 45 L 310 95 L 360 95 L 390 20 L 440 45 L 480 70 L 530 95 L 570 45 L 600 20"
          fill="none"
          stroke="var(--color-primary)"
          stroke-width="2.5"
        />
        <!-- Fill Area -->
        <path
          d="M 0 45 L 30 70 L 60 95 L 140 95 L 170 45 L 210 20 L 250 45 L 310 95 L 360 95 L 390 20 L 440 45 L 480 70 L 530 95 L 570 45 L 600 20 L 600 100 L 0 100 Z"
          fill="var(--color-primary-soft)"
        />
      </svg>
      <div
        class="mt-1.5 flex justify-between px-1 text-[0.6875rem] font-semibold text-[var(--text-soft)]"
      >
        <span>23:00 Einschlafen</span>
        <span>01:30 (Tief)</span>
        <span>03:45 (REM)</span>
        <span>05:30 (Tief)</span>
        <span>06:45 Aufwachen</span>
      </div>
    </div>

    <!-- Stages Grid -->
    <div class="grid grid-cols-2 gap-2 text-center text-xs sm:grid-cols-4">
      <div class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2">
        <span class="block text-[0.6875rem] text-[var(--text-soft)]">Tiefschlaf</span>
        <span class="font-bold text-[var(--text-main)]">{deepSleep || '—'}</span>
      </div>
      <div class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2">
        <span class="block text-[0.6875rem] text-[var(--text-soft)]">REM-Schlaf</span>
        <span class="font-bold text-[var(--text-main)]">{remSleep || '—'}</span>
      </div>
      <div class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2">
        <span class="block text-[0.6875rem] text-[var(--text-soft)]">Leichtschlaf</span>
        <span class="font-bold text-[var(--text-main)]">{lightSleep || '—'}</span>
      </div>
      <div class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2">
        <span class="block text-[0.6875rem] text-[var(--text-soft)]">Wachphasen</span>
        <span class="font-bold text-[var(--text-main)]">{awake || '—'}</span>
      </div>
    </div>
  {:else}
    <div
      class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] py-6 text-center text-xs text-[var(--text-muted)]"
    >
      Keine Schlafphasen für diese Nacht vorhanden. Synchronisiere deine Smartwatch oder erfasse die
      Schlafdauer manuell.
    </div>
  {/if}

  <!-- Cumulative Sleep Debt Banner (from services/analytics/stats.py) -->
  <div
    class="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-xs"
  >
    <div class="flex items-center gap-2">
      <span class="font-bold text-[var(--text-main)]">Schlafschuld:</span>
      <span class="font-bold text-[var(--color-primary)]">
        {sleepDebtHours !== 0
          ? sleepDebtHours > 0
            ? `+${sleepDebtHours}h Überschuss`
            : `${sleepDebtHours}h Defizit`
          : 'Ausgeglichen (0h)'}
      </span>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-[0.6875rem] text-[var(--text-muted)]"
        >Biologische Baseline: {baselineHours}h</span
      >
      <Badge variant="default">Baseline</Badge>
    </div>
  </div>
</div>
