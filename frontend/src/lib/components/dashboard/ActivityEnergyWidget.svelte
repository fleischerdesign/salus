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

<div
  class="space-y-5 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)] sm:p-6"
>
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-3">
      <div
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-orange-500/10 font-bold text-orange-500"
      >
        <Icon name="wb-sunny" size={20} />
      </div>
      <div>
        <h2 class="text-sm font-extrabold text-[var(--text-main)]">Aktivität und Energieumsatz</h2>
        <p class="text-xs text-[var(--text-muted)]">
          Diurnale Schrittverteilung, aktiver Kalorienverbrauch und TDEE
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="activity" class="font-bold">{stepPercent}% des Tagesziels</Badge>
    </div>
  </div>

  <!-- Main Grid: Hourly Activity Histogram + Energy Expenditure -->
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-12">
    <!-- Left Hero (7-Col): Diurnal Hourly Step Histogram -->
    <div
      class="flex flex-col justify-between space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 sm:p-5 lg:col-span-7"
    >
      <div class="flex items-start justify-between">
        <div>
          <span
            class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
          >
            Tages-Schritte & Distanz
          </span>
          <div class="mt-0.5 flex items-baseline gap-2">
            <span
              class="text-3xl font-extrabold tracking-tight text-[var(--text-main)] tabular-nums sm:text-4xl"
            >
              {steps.toLocaleString('de-DE')}
            </span>
            <span class="text-xs font-semibold text-[var(--text-soft)]"
              >/ {stepTarget.toLocaleString('de-DE')}</span
            >
            <span class="ml-1 text-xs font-bold text-orange-500"> 8.2 km </span>
          </div>
        </div>

        <div class="text-right">
          <span class="block text-[0.6875rem] font-bold text-[var(--text-muted)]"
            >Krafttraining</span
          >
          <span class="text-xs font-bold text-[var(--color-primary)]"
            >{exerciseMinutes} Min Push A</span
          >
        </div>
      </div>

      <!-- Diurnal Hourly Activity Histogram Bar Chart -->
      <div class="space-y-1 pt-1">
        <div class="flex h-16 items-end justify-between gap-1 px-1 sm:gap-1.5">
          {#each [{ h: '06', val: 15 }, { h: '07', val: 85, peak: true }, { h: '08', val: 40 }, { h: '09', val: 20 }, { h: '10', val: 30 }, { h: '11', val: 25 }, { h: '12', val: 65, peak: true }, { h: '13', val: 35 }, { h: '14', val: 20 }, { h: '15', val: 30 }, { h: '16', val: 45 }, { h: '17', val: 95, workout: true }, { h: '18', val: 60 }] as bar}
            <div class="group relative flex flex-1 flex-col items-center gap-1">
              <!-- Tooltip on hover -->
              <div
                class="pointer-events-none absolute -top-7 z-20 rounded bg-slate-900 px-1.5 py-0.5 text-[0.625rem] whitespace-nowrap text-white opacity-0 transition-opacity group-hover:opacity-100"
              >
                {bar.h}:00 • {bar.val * 15} Schritte
              </div>

              <div
                class="w-full rounded-t-sm transition-all duration-300 {bar.workout
                  ? 'bg-[var(--color-primary)]'
                  : bar.peak
                    ? 'bg-orange-500'
                    : 'bg-orange-500/35 group-hover:bg-orange-500/70'}"
                style="height: {bar.val}%;"
              ></div>
            </div>
          {/each}
        </div>
        <div
          class="flex justify-between px-1 text-[0.625rem] font-semibold text-[var(--text-soft)]"
        >
          <span>06:00 (Morgenlauf)</span>
          <span>12:00 (Spaziergang)</span>
          <span>17:00 (Workout)</span>
          <span>Jetzt</span>
        </div>
      </div>
    </div>

    <!-- Right Hero (5-Col): Energy Expenditure Split & Elevation -->
    <div
      class="flex flex-col justify-between space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 sm:p-5 lg:col-span-5"
    >
      <!-- Energy Expenditure Split -->
      <div>
        <div class="mb-1 flex items-center justify-between text-xs">
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >Gesamtumsatz (TDEE)</span
          >
          <span class="font-bold text-orange-500">{totalTdee.toLocaleString('de-DE')} kcal</span>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums"
            >{activeKcal}</span
          >
          <span class="text-xs text-[var(--text-soft)]"
            >kcal Aktiv + {bmrKcal} kcal Grundumsatz</span
          >
        </div>
        <!-- Progress Bar -->
        <div class="mt-2 flex h-2 w-full overflow-hidden rounded-full bg-[var(--border-subtle)]">
          <div class="h-full w-[26%] rounded-l-full bg-orange-500" title="Aktive Kalorien"></div>
          <div class="h-full flex-1 rounded-r-full bg-cyan-500" title="Grundumsatz BMR"></div>
        </div>
      </div>

      <!-- Floors & Elevation Metrics -->
      <div class="grid grid-cols-2 gap-2 border-t border-[var(--border-subtle)] pt-2 text-center">
        <div>
          <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >Stockwerke</span
          >
          <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums"
            >{floors} Etagen</span
          >
        </div>
        <div>
          <span class="block text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >Höhenmeter</span
          >
          <span class="text-sm font-extrabold text-emerald-500 tabular-nums">140 m Aufstieg</span>
        </div>
      </div>
    </div>
  </div>
</div>
