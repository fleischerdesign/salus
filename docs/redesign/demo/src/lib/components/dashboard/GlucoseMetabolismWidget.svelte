<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    fastingGlucose = 84,
    timeInRange = 96,
    fastingHours = 16.5,
    estimatedHomaIr = 0.8
  } = $props<{
    fastingGlucose?: number;
    timeInRange?: number;
    fastingHours?: number;
    estimatedHomaIr?: number;
  }>();
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 sm:p-6 shadow-[var(--shadow-card)] space-y-5">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-2">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-2xl bg-amber-500/10 text-amber-500 flex items-center justify-center font-bold shrink-0">
        <Icon name="sun" size={20} />
      </div>
      <div>
        <h2 class="text-sm font-extrabold text-[var(--text-main)]">Glukosestoffwechsel und Insulinsensitivität</h2>
        <p class="text-xs text-[var(--text-muted)]">Kontinuierliche Glukosekurve (CGM), Time in Range und Autophagie</p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="success" class="font-bold">HOMA-IR {estimatedHomaIr} • Sehr sensitiv</Badge>
    </div>
  </div>

  <!-- Main CGM Curve Canvas & Stats Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
    
    <!-- Left Hero (8-Col): 24h Glycemic Wave with Target Corridor -->
    <div class="lg:col-span-8 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 sm:p-5 flex flex-col justify-between space-y-3">
      <div class="flex items-start justify-between flex-wrap gap-2">
        <div>
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase tracking-wider block">
            Aktueller Gewebszucker
          </span>
          <div class="flex items-baseline gap-2 mt-0.5">
            <span class="text-3xl sm:text-4xl font-extrabold text-[var(--text-main)] tabular-nums tracking-tight">
              {fastingGlucose}
            </span>
            <span class="text-xs font-semibold text-[var(--text-soft)]">mg/dL</span>
            <span class="text-xs font-bold text-emerald-500 flex items-center gap-0.5 ml-1">
              &rarr; Stabil (4.7 mmol/L)
            </span>
          </div>
        </div>

        <div class="flex items-center gap-3 text-xs">
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span class="text-[var(--text-muted)]">Zielbereich: 70–140 mg/dL</span>
          </div>
        </div>
      </div>

      <!-- CGM Continuous Spline Wave SVG -->
      <div class="relative w-full h-24 pt-1">
        <svg class="w-full h-full overflow-visible" viewBox="0 0 500 80" preserveAspectRatio="none">
          <defs>
            <linearGradient id="cgmGlow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#10b981" stop-opacity="0.25" />
              <stop offset="100%" stop-color="#10b981" stop-opacity="0" />
            </linearGradient>
          </defs>

          <!-- 70-140 mg/dL Target Corridor Zone -->
          <rect x="0" y="15" width="500" height="50" fill="#10b981" fill-opacity="0.06" rx="6" />
          <line x1="0" y1="15" x2="500" y2="15" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="3 3" />
          <line x1="0" y1="65" x2="500" y2="65" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="3 3" />

          <!-- Continuous Glycemic Spline Path -->
          <path
            d="M 0 55 Q 80 50 140 30 T 260 52 T 380 48 T 460 54 L 500 52"
            fill="none"
            stroke="#10b981"
            stroke-width="2.5"
            stroke-linecap="round"
          />

          <!-- Gradient Area Under Curve -->
          <path
            d="M 0 55 Q 80 50 140 30 T 260 52 T 380 48 T 460 54 L 500 52 L 500 80 L 0 80 Z"
            fill="url(#cgmGlow)"
          />

          <!-- Live Reading Node -->
          <circle cx="500" cy="52" r="4.5" fill="#10b981" />
          <circle cx="500" cy="52" r="9" fill="#10b981" fill-opacity="0.2" class="animate-ping" />
        </svg>

        <div class="flex justify-between text-[0.625rem] text-[var(--text-soft)] font-semibold mt-1 px-1">
          <span>00:00 (Nacht)</span>
          <span>08:00 (Frühstück Peak: 112)</span>
          <span>12:30 (Mittag)</span>
          <span>Jetzt ({fastingGlucose} mg/dL)</span>
        </div>
      </div>
    </div>

    <!-- Right Hero (4-Col): Time in Range & Fasting Transition -->
    <div class="lg:col-span-4 flex flex-col justify-between space-y-3">
      
      <!-- Time in Range Pill Card -->
      <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 flex flex-col justify-between flex-1">
        <div class="flex justify-between items-center">
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Time in Range</span>
          <span class="text-xs font-bold text-emerald-500">{timeInRange}% TIR</span>
        </div>
        <div class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums my-1">
          23h 02m <span class="text-xs font-normal text-[var(--text-soft)]">im Zielbereich</span>
        </div>
        <div class="w-full bg-[var(--border-subtle)] h-2 rounded-full overflow-hidden flex">
          <div class="bg-emerald-500 h-full" style="width: {timeInRange}%;"></div>
          <div class="bg-amber-400 h-full flex-1"></div>
        </div>
      </div>

      <!-- Autophagy Metabolic Transition Card -->
      <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 flex flex-col justify-between flex-1">
        <div class="flex justify-between items-center">
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Fasten-Metabolismus</span>
          <span class="text-xs font-bold text-[var(--color-primary)]">{fastingHours}h Aktiv</span>
        </div>
        <div class="text-xs font-bold text-[var(--text-main)] my-1">
          Tief-Autophagie & Ketogenese
        </div>
        <div class="w-full bg-[var(--border-subtle)] h-1.5 rounded-full overflow-hidden">
          <div class="bg-[var(--color-primary)] h-full rounded-full" style="width: 85%;"></div>
        </div>
      </div>

    </div>

  </div>
</div>
