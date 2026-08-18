<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    steps = 10420,
    stepTarget = 12000,
    activeKcal = 640,
    bmrKcal = 1840,
    exerciseMinutes = 45,
    floors = 14
  } = $props<{
    steps?: number;
    stepTarget?: number;
    activeKcal?: number;
    bmrKcal?: number;
    exerciseMinutes?: number;
    floors?: number;
  }>();

  let stepPercent = $derived(Math.min(100, Math.round((steps / stepTarget) * 100)));
  let totalTdee = $derived(activeKcal + bmrKcal);
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 sm:p-6 shadow-[var(--shadow-card)] space-y-5">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-2">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-2xl bg-orange-500/10 text-orange-500 flex items-center justify-center font-bold shrink-0">
        <Icon name="sun" size={20} />
      </div>
      <div>
        <h2 class="text-sm font-extrabold text-[var(--text-main)]">Aktivität und Energieumsatz</h2>
        <p class="text-xs text-[var(--text-muted)]">Diurnale Schrittverteilung, aktiver Kalorienverbrauch und TDEE</p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="activity" class="font-bold">{stepPercent}% des Tagesziels</Badge>
    </div>
  </div>

  <!-- Main Grid: Hourly Activity Histogram + Energy Expenditure -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
    
    <!-- Left Hero (7-Col): Diurnal Hourly Step Histogram -->
    <div class="lg:col-span-7 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 sm:p-5 flex flex-col justify-between space-y-3">
      <div class="flex items-start justify-between">
        <div>
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase tracking-wider block">
            Tages-Schritte & Distanz
          </span>
          <div class="flex items-baseline gap-2 mt-0.5">
            <span class="text-3xl sm:text-4xl font-extrabold text-[var(--text-main)] tabular-nums tracking-tight">
              {steps.toLocaleString('de-DE')}
            </span>
            <span class="text-xs font-semibold text-[var(--text-soft)]">/ {stepTarget.toLocaleString('de-DE')}</span>
            <span class="text-xs font-bold text-orange-500 ml-1">
              8.2 km
            </span>
          </div>
        </div>

        <div class="text-right">
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] block">Krafttraining</span>
          <span class="text-xs font-bold text-[var(--color-primary)]">{exerciseMinutes} Min Push A</span>
        </div>
      </div>

      <!-- Diurnal Hourly Activity Histogram Bar Chart -->
      <div class="space-y-1 pt-1">
        <div class="h-16 flex items-end justify-between gap-1 sm:gap-1.5 px-1">
          {#each [
            { h: '06', val: 15 },
            { h: '07', val: 85, peak: true },
            { h: '08', val: 40 },
            { h: '09', val: 20 },
            { h: '10', val: 30 },
            { h: '11', val: 25 },
            { h: '12', val: 65, peak: true },
            { h: '13', val: 35 },
            { h: '14', val: 20 },
            { h: '15', val: 30 },
            { h: '16', val: 45 },
            { h: '17', val: 95, workout: true },
            { h: '18', val: 60 }
          ] as bar}
            <div class="flex-1 flex flex-col items-center gap-1 group relative">
              <!-- Tooltip on hover -->
              <div class="absolute -top-7 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-[0.625rem] py-0.5 px-1.5 rounded pointer-events-none whitespace-nowrap z-20">
                {bar.h}:00 • {bar.val * 15} Schritte
              </div>
              
              <div
                class="w-full rounded-t-sm transition-all duration-300 {bar.workout ? 'bg-[var(--color-primary)]' : bar.peak ? 'bg-orange-500' : 'bg-orange-500/35 group-hover:bg-orange-500/70'}"
                style="height: {bar.val}%;"
              ></div>
            </div>
          {/each}
        </div>
        <div class="flex justify-between text-[0.625rem] text-[var(--text-soft)] font-semibold px-1">
          <span>06:00 (Morgenlauf)</span>
          <span>12:00 (Spaziergang)</span>
          <span>17:00 (Workout)</span>
          <span>Jetzt</span>
        </div>
      </div>
    </div>

    <!-- Right Hero (5-Col): Energy Expenditure Split & Elevation -->
    <div class="lg:col-span-5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 sm:p-5 flex flex-col justify-between space-y-4">
      
      <!-- Energy Expenditure Split -->
      <div>
        <div class="flex justify-between items-center text-xs mb-1">
          <span class="font-bold text-[var(--text-muted)] uppercase text-[0.625rem]">Gesamtumsatz (TDEE)</span>
          <span class="font-bold text-orange-500">{totalTdee.toLocaleString('de-DE')} kcal</span>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums">{activeKcal}</span>
          <span class="text-xs text-[var(--text-soft)]">kcal Aktiv + {bmrKcal} kcal Grundumsatz</span>
        </div>
        <!-- Progress Bar -->
        <div class="w-full h-2 rounded-full overflow-hidden flex bg-[var(--border-subtle)] mt-2">
          <div class="bg-orange-500 h-full w-[26%] rounded-l-full" title="Aktive Kalorien"></div>
          <div class="bg-cyan-500 h-full flex-1 rounded-r-full" title="Grundumsatz BMR"></div>
        </div>
      </div>

      <!-- Floors & Elevation Metrics -->
      <div class="grid grid-cols-2 gap-2 pt-2 border-t border-[var(--border-subtle)] text-center">
        <div>
          <span class="text-[0.625rem] text-[var(--text-muted)] uppercase font-bold block">Stockwerke</span>
          <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums">{floors} Etagen</span>
        </div>
        <div>
          <span class="text-[0.625rem] text-[var(--text-muted)] uppercase font-bold block">Höhenmeter</span>
          <span class="text-sm font-extrabold text-emerald-500 tabular-nums">140 m Aufstieg</span>
        </div>
      </div>

    </div>

  </div>
</div>
