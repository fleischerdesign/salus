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

<div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-card">
  <div class="flex items-start justify-between gap-3">
    <div class="flex min-w-0 items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
        style="background-color: color-mix(in srgb, var(--color-sleep) 12%, transparent); color: var(--color-sleep);"
      >
        <Icon name="bedtime" size="md" />
      </div>
      <div class="min-w-0">
        <h3 class="truncate text-sm font-extrabold tracking-tight text-text-main">
          Schlafarchitektur und Erholung
        </h3>
        <p class="truncate text-xs text-text-muted">
          {hasSleepData ? 'Schlaf-Tracking aktiv' : 'Noch keine Schlafaufzeichnung für diese Nacht'}
        </p>
      </div>
    </div>
    <div class="flex shrink-0 items-center gap-2">
      {#if hasSleepData}
        {#if hrv !== null}<Badge variant="success" class="text-[0.625rem] font-bold"
            >HRV: {hrv} ms</Badge
          >{/if}
        <Badge variant="primary" class="text-[0.625rem] font-bold"
          >{duration} ({score}% Score)</Badge
        >
      {:else}
        <Badge variant="default" class="text-[0.625rem] font-bold">Keine Schlafdaten</Badge>
      {/if}
    </div>
  </div>

  {#if hasSleepData}
    <!-- Hypnogram Stage Wave Canvas -->
    <div class="rounded-xl border border-border-subtle bg-surface-50 p-3.5">
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
      <div class="mt-1.5 flex justify-between px-1 text-[0.6875rem] font-semibold text-text-soft">
        <span>23:00 Einschlafen</span>
        <span>01:30 (Tief)</span>
        <span>03:45 (REM)</span>
        <span>05:30 (Tief)</span>
        <span>06:45 Aufwachen</span>
      </div>
    </div>

    <!-- Stages Grid -->
    <div class="grid grid-cols-2 gap-2 text-center text-xs sm:grid-cols-4">
      <div class="rounded-xl border border-border-subtle bg-surface-50 p-2">
        <span class="block text-[0.6875rem] text-text-soft">Tiefschlaf</span>
        <span class="font-bold text-text-main">{deepSleep || '—'}</span>
      </div>
      <div class="rounded-xl border border-border-subtle bg-surface-50 p-2">
        <span class="block text-[0.6875rem] text-text-soft">REM-Schlaf</span>
        <span class="font-bold text-text-main">{remSleep || '—'}</span>
      </div>
      <div class="rounded-xl border border-border-subtle bg-surface-50 p-2">
        <span class="block text-[0.6875rem] text-text-soft">Leichtschlaf</span>
        <span class="font-bold text-text-main">{lightSleep || '—'}</span>
      </div>
      <div class="rounded-xl border border-border-subtle bg-surface-50 p-2">
        <span class="block text-[0.6875rem] text-text-soft">Wachphasen</span>
        <span class="font-bold text-text-main">{awake || '—'}</span>
      </div>
    </div>
  {:else}
    <div
      class="rounded-xl border border-border-subtle bg-surface-50 py-6 text-center text-xs text-text-muted"
    >
      Keine Schlafphasen für diese Nacht vorhanden. Synchronisiere deine Smartwatch oder erfasse die
      Schlafdauer manuell.
    </div>
  {/if}

  <!-- Cumulative Sleep Debt Banner (from services/analytics/stats.py) -->
  <div
    class="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-border-subtle bg-surface-50 p-3 text-xs"
  >
    <div class="flex items-center gap-2">
      <span class="font-bold text-text-main">Schlafschuld:</span>
      <span class="font-bold text-primary">
        {sleepDebtHours !== 0
          ? sleepDebtHours > 0
            ? `+${sleepDebtHours}h Überschuss`
            : `${sleepDebtHours}h Defizit`
          : 'Ausgeglichen (0h)'}
      </span>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-[0.6875rem] text-text-muted">Biologische Baseline: {baselineHours}h</span>
      <Badge variant="default">Baseline</Badge>
    </div>
  </div>
</div>
