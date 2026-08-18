<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    readiness = 88,
    hrv = 68,
    stressIndex = 22,
    skinTempDelta = -0.2
  } = $props<{
    readiness?: number;
    hrv?: number;
    stressIndex?: number;
    skinTempDelta?: number;
  }>();

  // SVG Circular Dashoffset for 88% Ring (radius = 38, circumference = 238.76)
  const circumference = 2 * Math.PI * 38;
  let strokeDashoffset = $derived(circumference - (readiness / 100) * circumference);
</script>

<div
  class="space-y-5 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)] sm:p-6"
>
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-3">
      <div
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-emerald-500/10 font-bold text-emerald-500"
      >
        <Icon name="wb-sunny" size={20} />
      </div>
      <div>
        <h2 class="text-sm font-extrabold text-[var(--text-main)]">
          Erholungs- und Bereitschaftsstatus
        </h2>
        <p class="text-xs text-[var(--text-muted)]">
          Autonomes Nervensystem, HRV-Verteilung und Trainingsbereitschaft
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="success" class="font-bold">Volle Belastbarkeit</Badge>
    </div>
  </div>

  <!-- Hero Grid: Circular Battery Ring + ANS Balance -->
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-12">
    <!-- Left Hero (5-Col): Circular Recovery Battery -->
    <div
      class="flex items-center justify-around gap-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-5 lg:col-span-5"
    >
      <div class="relative flex h-24 w-24 items-center justify-center sm:h-28 sm:w-28">
        <svg class="h-full w-full -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="38"
            fill="none"
            stroke="var(--border-subtle)"
            stroke-width="8"
          />
          <circle
            cx="50"
            cy="50"
            r="38"
            fill="none"
            stroke="#10b981"
            stroke-width="8"
            stroke-linecap="round"
            stroke-dasharray={circumference}
            stroke-dashoffset={strokeDashoffset}
            class="transition-all duration-1000 ease-out"
          />
        </svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums sm:text-3xl"
            >{readiness}</span
          >
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase">Score</span>
        </div>
      </div>

      <div class="space-y-1">
        <span class="block text-xs font-bold text-emerald-500">Exzellente Erholung</span>
        <p class="text-[0.6875rem] leading-tight text-[var(--text-muted)]">
          ZNS und Herzkreislauf sind vollständig regeneriert.
        </p>
        <div class="pt-1 text-[0.625rem] font-bold text-[var(--text-main)]">
          Empfohlener Strain: <span class="text-emerald-500">14.0–17.5</span>
        </div>
      </div>
    </div>

    <!-- Right Hero (7-Col): Autonomic Nervous System & HRV Distribution -->
    <div
      class="flex flex-col justify-between space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 sm:p-5 lg:col-span-7"
    >
      <!-- ANS Balance Bar (Sympathetic vs Parasympathetic) -->
      <div>
        <div class="mb-1.5 flex items-center justify-between text-xs font-semibold">
          <span class="font-bold text-[var(--color-primary)]"
            >Parasympathikus ({100 - stressIndex}%)</span
          >
          <span class="text-[0.6875rem] text-[var(--text-muted)]">Autonome Balance</span>
          <span class="font-bold text-amber-500">Sympathikus ({stressIndex}%)</span>
        </div>
        <div class="flex h-2 w-full overflow-hidden rounded-full bg-[var(--border-subtle)]">
          <div
            class="h-full rounded-l-full bg-[var(--color-primary)]"
            style="width: {100 - stressIndex}%;"
          ></div>
          <div class="h-full flex-1 rounded-r-full bg-amber-400"></div>
        </div>
      </div>

      <!-- HRV RMSSD vs 30-Day Range -->
      <div class="grid grid-cols-2 gap-3 border-t border-[var(--border-subtle)] pt-1">
        <div>
          <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >HRV RMSSD</span
          >
          <div class="mt-0.5 text-xl font-extrabold text-[var(--color-primary)] tabular-nums">
            {hrv} <span class="text-xs font-normal text-[var(--text-soft)]">ms</span>
          </div>
          <span class="block text-[0.625rem] font-semibold text-emerald-500"
            >+10 ms über 30T-Baseline</span
          >
        </div>

        <div>
          <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >Hauttemperatur-Abweichung</span
          >
          <div class="mt-0.5 text-xl font-extrabold text-cyan-500 tabular-nums">
            {skinTempDelta > 0 ? `+${skinTempDelta}` : skinTempDelta}
            <span class="text-xs font-normal text-[var(--text-soft)]">°C</span>
          </div>
          <span class="block text-[0.625rem] font-semibold text-emerald-500"
            >Physiologische Homöostase</span
          >
        </div>
      </div>
    </div>
  </div>
</div>
