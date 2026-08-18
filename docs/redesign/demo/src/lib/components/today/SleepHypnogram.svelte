<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    score = 92,
    duration = '7h 45m',
    deepSleep = '1h 35m (20%)',
    remSleep = '2h 05m (27%)',
    lightSleep = '3h 40m (48%)',
    awake = '0h 25m (5%)',
    hrv = 64,
    sleepDebtHours = -1.2, // From services/analytics/stats.py: sleep_debt_cumulative()
    baselineHours = 8.0
  } = $props<{
    score?: number;
    duration?: string;
    deepSleep?: string;
    remSleep?: string;
    lightSleep?: string;
    awake?: string;
    hrv?: number;
    sleepDebtHours?: number;
    baselineHours?: number;
  }>();
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] space-y-3.5">
  <div class="flex items-center justify-between flex-wrap gap-2">
    <div class="text-sm font-bold flex items-center gap-2 text-[var(--text-main)]">
      <div class="w-8 h-8 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center">
        <Icon name="moon" size={16} />
      </div>
      <div>
        <span class="block">Schlafarchitektur und Erholung</span>
        <span class="text-xs text-[var(--text-muted)] font-normal">Oura Ring Gen 3 • Schlafeffizienz: 94%</span>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">HRV: {hrv} ms</Badge>
      <Badge variant="primary">{duration} ({score}% Score)</Badge>
    </div>
  </div>

  <!-- Hypnogram Stage Wave Canvas -->
  <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3.5">
    <svg class="w-full h-24" viewBox="0 0 600 100" preserveAspectRatio="none">
      <!-- Grid guide lines -->
      <line x1="0" y1="20" x2="600" y2="20" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="2 2" />
      <line x1="0" y1="45" x2="600" y2="45" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="2 2" />
      <line x1="0" y1="70" x2="600" y2="70" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="2 2" />
      <line x1="0" y1="95" x2="600" y2="95" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="2 2" />

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
    <div class="flex justify-between text-[0.6875rem] text-[var(--text-soft)] font-semibold mt-1.5 px-1">
      <span>23:00 Einschlafen</span>
      <span>01:30 (Tief)</span>
      <span>03:45 (REM)</span>
      <span>05:30 (Tief)</span>
      <span>06:45 Aufwachen</span>
    </div>
  </div>

  <!-- Stages Grid -->
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] p-2 rounded-xl">
      <span class="text-[0.6875rem] text-[var(--text-soft)] block">Tiefschlaf</span>
      <span class="font-bold text-[var(--text-main)]">{deepSleep}</span>
    </div>
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] p-2 rounded-xl">
      <span class="text-[0.6875rem] text-[var(--text-soft)] block">REM-Schlaf</span>
      <span class="font-bold text-[var(--text-main)]">{remSleep}</span>
    </div>
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] p-2 rounded-xl">
      <span class="text-[0.6875rem] text-[var(--text-soft)] block">Leichtschlaf</span>
      <span class="font-bold text-[var(--text-main)]">{lightSleep}</span>
    </div>
    <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] p-2 rounded-xl">
      <span class="text-[0.6875rem] text-[var(--text-soft)] block">Wachphasen</span>
      <span class="font-bold text-[var(--text-main)]">{awake}</span>
    </div>
  </div>

  <!-- Cumulative Sleep Debt Banner (from services/analytics/stats.py) -->
  <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl flex items-center justify-between text-xs flex-wrap gap-2">
    <div class="flex items-center gap-2">
      <span class="font-bold text-[var(--text-main)]">30-Tage Schlafschuld (Stats-Engine):</span>
      <span class="font-bold text-[var(--color-primary)]">{sleepDebtHours > 0 ? `+${sleepDebtHours}h Überschuss` : `${sleepDebtHours}h Defizit`}</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-[0.6875rem] text-[var(--text-muted)]">Biologische Baseline: {baselineHours}h</span>
      <Badge variant="success">Erholung Stabil</Badge>
    </div>
  </div>
</div>
