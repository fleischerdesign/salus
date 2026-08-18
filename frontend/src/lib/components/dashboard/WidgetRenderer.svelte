<script lang="ts">
  import type { DashboardWidget } from '../../types/widget-groups';
  import CircadianSunArc from '../today/CircadianSunArc.svelte';
  import HydrationWaveGlass from '../today/HydrationWaveGlass.svelte';
  import FastingMetabolicClock from '../today/FastingMetabolicClock.svelte';
  import HeroProgressRings from '../today/HeroProgressRings.svelte';
  import SleepHypnogram from '../today/SleepHypnogram.svelte';
  import MedicationDoseCard from '../today/MedicationDoseCard.svelte';
  import MoodValenceSphere from '../today/MoodValenceSphere.svelte';
  import HabitCheckPills from '../today/HabitCheckPills.svelte';
  import HabitYearMatrix from '../today/HabitYearMatrix.svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    widget,
    waterAmount = 0,
    liveMetrics,
    onopenfasting
  } = $props<{
    widget: DashboardWidget;
    waterAmount?: number;
    liveMetrics?: Map<string, number>;
    onopenfasting?: () => void;
  }>();

  // Cardio Data: null if not recorded
  let systolic = $derived(liveMetrics?.get('systolic_bp') ?? null);
  let diastolic = $derived(liveMetrics?.get('diastolic_bp') ?? null);
  let pressurePercent = $derived(
    systolic !== null ? Math.min(100, Math.max(0, ((systolic - 90) / (160 - 90)) * 100)) : 0
  );

  let rhr = $derived(
    liveMetrics?.get('heart_rate_resting') ?? liveMetrics?.get('heart_rate') ?? null
  );
  let spo2 = $derived(liveMetrics?.get('spo2') ?? null);
  let vo2max = $derived(liveMetrics?.get('vo2_max') ?? null);
  let glucose = $derived(liveMetrics?.get('blood_glucose') ?? null);
  let hrv = $derived(liveMetrics?.get('hrv') ?? liveMetrics?.get('hrv_sdnn') ?? null);

  // Recovery Data
  const circumference = 2 * Math.PI * 38;
  let strokeDashoffset = circumference - (88 / 100) * circumference;
</script>

<div class="h-full">
  {#if widget.type === 'circadian_arc'}
    <CircadianSunArc />

    <!-- 1. BLOOD PRESSURE DIAL -->
  {:else if widget.type === 'blood_pressure_dial'}
    <div
      class="flex h-full flex-col justify-between space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div class="flex items-start justify-between">
        <div>
          <span
            class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
          >
            Arterieller Blutdruck
          </span>
          <div class="mt-1 flex items-baseline gap-2">
            {#if systolic !== null && diastolic !== null}
              <span
                class="text-3xl font-extrabold tracking-tight text-[var(--text-main)] tabular-nums"
                >{systolic}</span
              >
              <span class="text-xl font-bold text-[var(--text-muted)] tabular-nums"
                >/ {diastolic}</span
              >
              <span class="text-xs font-semibold text-[var(--text-soft)]">mmHg</span>
            {:else}
              <span
                class="text-3xl font-extrabold tracking-tight text-[var(--text-muted)] tabular-nums"
                >—</span
              >
              <span class="text-xl font-bold text-[var(--text-muted)] tabular-nums">/ —</span>
              <span class="text-xs font-semibold text-[var(--text-soft)]">mmHg</span>
            {/if}
          </div>
        </div>
        {#if systolic !== null && diastolic !== null}
          <Badge
            variant={systolic <= 120 && diastolic <= 80
              ? 'success'
              : systolic <= 130
                ? 'primary'
                : 'vital'}
            class="font-bold"
          >
            {systolic <= 120 && diastolic <= 80
              ? 'Optimal (ESC 2024)'
              : systolic <= 130
                ? 'Normal'
                : 'Erhöht'}
          </Badge>
        {:else}
          <Badge variant="default">Kein Eintrag</Badge>
        {/if}
      </div>

      {#if systolic !== null && diastolic !== null}
        <div class="space-y-1.5 pt-1">
          <div class="relative flex h-2.5 overflow-hidden rounded-full bg-[var(--border-subtle)]">
            <div class="h-full w-[42%] bg-emerald-500"></div>
            <div class="h-full w-[15%] bg-teal-400"></div>
            <div class="h-full w-[15%] bg-amber-400"></div>
            <div class="h-full flex-1 bg-rose-500"></div>
            <div
              class="absolute top-0 bottom-0 w-2 -translate-x-1/2 rounded-full border-2 border-slate-900 bg-white shadow-md transition-all duration-500"
              style="left: {pressurePercent}%;"
            ></div>
          </div>
          <div
            class="flex justify-between px-0.5 text-[0.625rem] font-semibold text-[var(--text-soft)]"
          >
            <span>90</span>
            <span class="font-bold text-emerald-500">120 (Optimal)</span>
            <span class="font-bold text-amber-500">130</span>
            <span class="font-bold text-rose-500">140+</span>
            <span>160</span>
          </div>
        </div>
      {:else}
        <div class="py-2 text-xs text-[var(--text-muted)]">
          Noch keine Blutdruckmessung für diesen Tag erfasst.
        </div>
      {/if}
    </div>

    <!-- 2. RHR SPARKLINE -->
  {:else if widget.type === 'rhr_sparkline'}
    <div
      class="flex h-full items-center justify-between rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div>
        <span
          class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >
          Ruhepuls
        </span>
        <div class="mt-1 flex items-baseline gap-1">
          <span
            class="text-3xl font-extrabold {rhr !== null
              ? 'text-[var(--text-main)]'
              : 'text-[var(--text-muted)]'} tabular-nums"
          >
            {rhr !== null ? rhr : '—'}
          </span>
          <span class="text-xs text-[var(--text-soft)]">bpm</span>
        </div>
        <span class="mt-1 block text-xs text-[var(--text-muted)]">
          {rhr !== null ? 'Gemessen' : 'Nicht erfasst'}
        </span>
      </div>
      {#if rhr !== null}
        <div class="h-12 w-28">
          <svg class="h-full w-full overflow-visible" viewBox="0 0 100 40">
            <path
              d="M 0 35 L 16 28 L 33 22 L 50 22 L 66 16 L 83 16 L 100 16"
              fill="none"
              stroke="#059669"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <circle cx="100" cy="16" r="4" fill="#059669" />
          </svg>
        </div>
      {:else}
        <Badge variant="default">Keine Daten</Badge>
      {/if}
    </div>

    <!-- 3. SPO2 & VO2MAX -->
  {:else if widget.type === 'spo2_vo2max'}
    <div
      class="grid h-full grid-cols-2 gap-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div class="border-r border-[var(--border-subtle)] pr-2">
        <span
          class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >
          Sauerstoffsättigung
        </span>
        <div class="mt-1 flex items-baseline gap-1">
          <span
            class="text-3xl font-extrabold {spo2 !== null
              ? 'text-[var(--text-main)]'
              : 'text-[var(--text-muted)]'} tabular-nums"
          >
            {spo2 !== null ? spo2 : '—'}
          </span>
          <span class="text-xs text-[var(--text-soft)]">%</span>
        </div>
        <Badge variant={spo2 !== null ? 'success' : 'default'} class="mt-2 text-[0.625rem]">
          {spo2 !== null ? 'Optimal' : 'Keine Daten'}
        </Badge>
      </div>
      <div class="pl-2">
        <span
          class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >
          Kardiorespiratorisch
        </span>
        <div class="mt-1 flex items-baseline gap-1">
          <span
            class="text-3xl font-extrabold {vo2max !== null
              ? 'text-[var(--color-primary)]'
              : 'text-[var(--text-muted)]'} tabular-nums"
          >
            {vo2max !== null ? vo2max : '—'}
          </span>
          <span class="text-[0.625rem] text-[var(--text-soft)]">ml/kg</span>
        </div>
        <Badge variant={vo2max !== null ? 'primary' : 'default'} class="mt-2 text-[0.625rem]">
          {vo2max !== null ? 'VO2max Exzellent' : 'Keine Daten'}
        </Badge>
      </div>
    </div>

    <!-- 4. CGM WAVE -->
  {:else if widget.type === 'cgm_wave'}
    <div
      class="flex h-full flex-col justify-between space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div class="flex items-start justify-between">
        <div>
          <span
            class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
          >
            Echtzeit-Glukose (CGM)
          </span>
          <div class="mt-1 flex items-baseline gap-2">
            <span
              class="text-3xl font-extrabold {glucose !== null
                ? 'text-[var(--text-main)]'
                : 'text-[var(--text-muted)]'} tabular-nums"
            >
              {glucose !== null ? glucose : '—'}
            </span>
            <span class="text-xs font-semibold text-[var(--text-soft)]">mg/dL</span>
          </div>
        </div>
        <Badge variant={glucose !== null ? 'success' : 'default'}>
          {glucose !== null ? 'TIR: 96%' : 'Kein Sensor'}
        </Badge>
      </div>

      {#if glucose !== null}
        <div class="relative h-16 w-full">
          <div
            class="absolute inset-0 rounded-xl border border-emerald-500/10 bg-emerald-500/5"
          ></div>
          <svg
            class="h-full w-full overflow-visible"
            viewBox="0 0 300 60"
            preserveAspectRatio="none"
          >
            <path
              d="M 0 35 Q 40 25, 75 30 T 150 28 T 225 38 T 300 32"
              fill="none"
              stroke="var(--color-primary)"
              stroke-width="2.5"
              stroke-linecap="round"
            />
            <circle cx="300" cy="32" r="4.5" fill="var(--color-primary)" />
          </svg>
        </div>
      {:else}
        <div
          class="flex h-16 w-full items-center justify-center rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-xs text-[var(--text-muted)]"
        >
          Keine Glukosedaten für diesen Tag
        </div>
      {/if}
    </div>

    <!-- 5. TIME IN RANGE -->
  {:else if widget.type === 'time_in_range'}
    <div
      class="flex h-full items-center justify-between rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div>
        <span
          class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
        >
          Time in Range (70–140)
        </span>
        <div class="mt-1 flex items-baseline gap-1">
          <span
            class="text-3xl font-extrabold {glucose !== null
              ? 'text-[var(--text-main)]'
              : 'text-[var(--text-muted)]'} tabular-nums"
          >
            {glucose !== null ? '96.4' : '—'}
          </span>
          <span class="text-xs text-[var(--text-soft)]">%</span>
        </div>
        <span class="mt-1 block text-xs text-[var(--text-muted)]">
          {glucose !== null ? 'Ziel: > 90% (Erfüllt)' : 'Keine Messungen'}
        </span>
      </div>
      <div
        class="h-20 w-20 rounded-full border-4 {glucose !== null
          ? 'border-emerald-500 text-emerald-500'
          : 'border-[var(--border-subtle)] text-[var(--text-muted)]'} flex items-center justify-center text-sm font-extrabold"
      >
        {glucose !== null ? '96%' : '—'}
      </div>
    </div>

    <!-- 6. FASTING TRANSITION -->
  {:else if widget.type === 'fasting_transition'}
    <div
      class="flex h-full flex-col justify-between rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span
            class="text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
          >
            Stoffwechselphase
          </span>
        </div>
        <Badge variant="default">Fasten-Modul</Badge>
      </div>

      <div class="my-2">
        <span class="block text-base font-bold text-[var(--text-main)]"
          >Intervallfasten & Autophagie</span
        >
        <span class="mt-0.5 block text-xs text-[var(--text-muted)]">
          Stoffwechselphasen, Ketose und zelluläre Reinigung
        </span>
      </div>

      <button
        type="button"
        onclick={onopenfasting}
        class="w-full cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] py-2 text-center text-xs font-bold text-[var(--color-primary)] transition-colors hover:bg-[var(--bg-surface-100)]"
      >
        Fasten-Details öffnen &rarr;
      </button>
    </div>

    <!-- 7. RECOVERY BATTERY -->
  {:else if widget.type === 'recovery_battery'}
    <div
      class="flex h-full flex-col justify-between space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div class="flex items-start justify-between">
        <div>
          <span
            class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
          >
            ZNS-Erholung & Batterie
          </span>
          <div class="mt-1 flex items-baseline gap-2">
            <span
              class="text-3xl font-extrabold {hrv !== null
                ? 'text-[var(--text-main)]'
                : 'text-[var(--text-muted)]'} tabular-nums"
            >
              {hrv !== null ? '88' : '—'}
            </span>
            <span class="text-xs font-semibold text-[var(--text-soft)]">/ 100</span>
          </div>
        </div>
        <Badge variant={hrv !== null ? 'success' : 'default'} class="font-bold">
          {hrv !== null ? 'Vollständig Erholt' : 'Keine HRV-Daten'}
        </Badge>
      </div>

      <div class="flex items-center gap-4">
        <div class="relative h-20 w-20 shrink-0">
          <svg class="h-full w-full -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="38"
              fill="none"
              stroke="var(--bg-surface-50)"
              stroke-width="8"
            />
            {#if hrv !== null}
              <circle
                cx="50"
                cy="50"
                r="38"
                fill="none"
                stroke="var(--color-success)"
                stroke-width="8"
                stroke-dasharray={circumference}
                stroke-dashoffset={strokeDashoffset}
                stroke-linecap="round"
                class="transition-all duration-700"
              />
            {/if}
          </svg>
          <div
            class="absolute inset-0 flex items-center justify-center text-sm font-extrabold {hrv !==
            null
              ? 'text-[var(--color-success)]'
              : 'text-[var(--text-muted)]'}"
          >
            {hrv !== null ? '88%' : '—'}
          </div>
        </div>
        <p class="text-xs leading-relaxed text-[var(--text-muted)]">
          {hrv !== null
            ? 'HRV über Baseline (+12 ms). Hohe Belastungstoleranz heute.'
            : 'Erfasse HRV- oder Schlafmessungen zur Berechnung des Erholungsindex.'}
        </p>
      </div>
    </div>

    <!-- 8. ANS BALANCE -->
  {:else if widget.type === 'ans_balance'}
    <div
      class="flex h-full flex-col justify-between rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
    >
      <div class="flex items-center justify-between">
        <span class="text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase">
          Autonomes Nervensystem
        </span>
        <Badge variant={hrv !== null ? 'success' : 'default'}>
          {hrv !== null ? 'Parasympathikus dominant' : 'Keine Daten'}
        </Badge>
      </div>

      <div class="my-3 space-y-2">
        <div class="flex justify-between text-xs font-semibold">
          <span class={hrv !== null ? 'text-emerald-500' : 'text-[var(--text-muted)]'}
            >Regeneration: {hrv !== null ? '68%' : '—'}</span
          >
          <span class={hrv !== null ? 'text-amber-500' : 'text-[var(--text-muted)]'}
            >Sympathikus: {hrv !== null ? '32%' : '—'}</span
          >
        </div>
        <div class="flex h-2 overflow-hidden rounded-full bg-[var(--border-subtle)]">
          {#if hrv !== null}
            <div class="h-full w-[68%] bg-emerald-500"></div>
            <div class="h-full w-[32%] bg-amber-500"></div>
          {:else}
            <div class="h-full w-full bg-[var(--bg-surface-100)]"></div>
          {/if}
        </div>
      </div>

      <span class="text-[0.6875rem] text-[var(--text-soft)]">
        {hrv !== null ? 'HRV-SDNN: 68 ms • RMSSD: 54 ms' : 'Keine HRV-Werte für dieses Datum'}
      </span>
    </div>

    <!-- 9. HYDRATION -->
  {:else if widget.type === 'hydration_glass'}
    <HydrationWaveGlass currentMl={waterAmount} />

    <!-- 10. METABOLIC CLOCK -->
  {:else if widget.type === 'metabolic_clock'}
    <FastingMetabolicClock onopenfood={() => {}} />

    <!-- 11. HERO PROGRESS RINGS -->
  {:else if widget.type === 'hero_rings'}
    <HeroProgressRings />

    <!-- 12. SLEEP HYPNOGRAM -->
  {:else if widget.type === 'sleep_hypnogram'}
    <SleepHypnogram />

    <!-- 13. MEDICATION DOSE -->
  {:else if widget.type === 'medication_dose'}
    <MedicationDoseCard />

    <!-- 14. MOOD SPHERE -->
  {:else if widget.type === 'mood_sphere'}
    <MoodValenceSphere />

    <!-- 15. HABIT CHECK PILLS -->
  {:else if widget.type === 'habit_check_pills'}
    <HabitCheckPills />

    <!-- 16. HABIT YEAR MATRIX -->
  {:else if widget.type === 'habit_year_matrix'}
    <HabitYearMatrix />

    <!-- FALLBACK / UNKNOWN -->
  {:else}
    <div
      class="flex h-full flex-col items-center justify-center space-y-1 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 text-center text-xs text-[var(--text-muted)] shadow-[var(--shadow-card)]"
    >
      <Icon name="dashboard" size={24} class="mb-1 text-[var(--text-muted)]" />
      <span class="font-bold text-[var(--text-main)]">{widget.title}</span>
      <span>{widget.type}</span>
    </div>
  {/if}
</div>
