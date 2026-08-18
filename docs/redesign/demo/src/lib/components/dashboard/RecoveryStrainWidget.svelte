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

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 sm:p-6 shadow-[var(--shadow-card)] space-y-5">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-2">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center font-bold shrink-0">
        <Icon name="sun" size={20} />
      </div>
      <div>
        <h2 class="text-sm font-extrabold text-[var(--text-main)]">Erholungs- und Bereitschaftsstatus</h2>
        <p class="text-xs text-[var(--text-muted)]">Autonomes Nervensystem, HRV-Verteilung und Trainingsbereitschaft</p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="success" class="font-bold">Volle Belastbarkeit</Badge>
    </div>
  </div>

  <!-- Hero Grid: Circular Battery Ring + ANS Balance -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
    
    <!-- Left Hero (5-Col): Circular Recovery Battery -->
    <div class="lg:col-span-5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-5 flex items-center justify-around gap-4">
      <div class="relative w-24 h-24 sm:w-28 sm:h-28 flex items-center justify-center">
        <svg class="w-full h-full -rotate-90" viewBox="0 0 100 100">
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
          <span class="text-2xl sm:text-3xl font-extrabold text-[var(--text-main)] tabular-nums">{readiness}</span>
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase">Score</span>
        </div>
      </div>

      <div class="space-y-1">
        <span class="text-xs font-bold text-emerald-500 block">Exzellente Erholung</span>
        <p class="text-[0.6875rem] text-[var(--text-muted)] leading-tight">
          ZNS und Herzkreislauf sind vollständig regeneriert.
        </p>
        <div class="pt-1 text-[0.625rem] font-bold text-[var(--text-main)]">
          Empfohlener Strain: <span class="text-emerald-500">14.0–17.5</span>
        </div>
      </div>
    </div>

    <!-- Right Hero (7-Col): Autonomic Nervous System & HRV Distribution -->
    <div class="lg:col-span-7 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 sm:p-5 flex flex-col justify-between space-y-4">
      
      <!-- ANS Balance Bar (Sympathetic vs Parasympathetic) -->
      <div>
        <div class="flex justify-between items-center text-xs mb-1.5 font-semibold">
          <span class="text-[var(--color-primary)] font-bold">Parasympathikus (78%)</span>
          <span class="text-[var(--text-muted)] text-[0.6875rem]">Autonome Balance</span>
          <span class="text-amber-500 font-bold">Sympathikus (22%)</span>
        </div>
        <div class="w-full h-2 rounded-full bg-[var(--border-subtle)] overflow-hidden flex">
          <div class="h-full bg-[var(--color-primary)] w-[78%] rounded-l-full"></div>
          <div class="h-full bg-amber-400 flex-1 rounded-r-full"></div>
        </div>
      </div>

      <!-- HRV RMSSD vs 30-Day Range -->
      <div class="grid grid-cols-2 gap-3 pt-1 border-t border-[var(--border-subtle)]">
        <div>
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase block">HRV RMSSD</span>
          <div class="text-xl font-extrabold text-[var(--color-primary)] tabular-nums mt-0.5">
            {hrv} <span class="text-xs font-normal text-[var(--text-soft)]">ms</span>
          </div>
          <span class="text-[0.625rem] text-emerald-500 font-semibold block">+10 ms über 30T-Baseline</span>
        </div>

        <div>
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase block">Hauttemperatur-Abweichung</span>
          <div class="text-xl font-extrabold text-cyan-500 tabular-nums mt-0.5">
            {skinTempDelta > 0 ? `+${skinTempDelta}` : skinTempDelta} <span class="text-xs font-normal text-[var(--text-soft)]">°C</span>
          </div>
          <span class="text-[0.625rem] text-emerald-500 font-semibold block">Physiologische Homöostase</span>
        </div>
      </div>

    </div>

  </div>
</div>
