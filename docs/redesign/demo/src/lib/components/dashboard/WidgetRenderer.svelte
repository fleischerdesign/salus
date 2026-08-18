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
    waterAmount = 2250,
    onopenfasting
  } = $props<{
    widget: DashboardWidget;
    waterAmount?: number;
    onopenfasting?: () => void;
  }>();

  // Cardio Data
  let systolic = 118;
  let diastolic = 76;
  let pressurePercent = Math.min(100, Math.max(0, ((systolic - 90) / (160 - 90)) * 100));

  // Recovery Data
  const circumference = 2 * Math.PI * 38;
  let strokeDashoffset = circumference - (88 / 100) * circumference;
</script>

<div class="h-full">
  {#if widget.type === 'circadian_arc'}
    <CircadianSunArc />

  <!-- 1. BLOOD PRESSURE DIAL -->
  {:else if widget.type === 'blood_pressure_dial'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex flex-col justify-between space-y-4">
      <div class="flex items-start justify-between">
        <div>
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase tracking-wider block">
            Arterieller Blutdruck
          </span>
          <div class="flex items-baseline gap-2 mt-1">
            <span class="text-3xl font-extrabold text-[var(--text-main)] tabular-nums tracking-tight">118</span>
            <span class="text-xl font-bold text-[var(--text-muted)] tabular-nums">/ 76</span>
            <span class="text-xs font-semibold text-[var(--text-soft)]">mmHg</span>
          </div>
        </div>
        <Badge variant="success" class="font-bold">Optimal (ESC 2024)</Badge>
      </div>

      <div class="space-y-1.5 pt-1">
        <div class="relative h-2.5 rounded-full overflow-hidden flex bg-[var(--border-subtle)]">
          <div class="h-full bg-emerald-500 w-[42%]"></div>
          <div class="h-full bg-teal-400 w-[15%]"></div>
          <div class="h-full bg-amber-400 w-[15%]"></div>
          <div class="h-full bg-rose-500 flex-1"></div>
          <div
            class="absolute top-0 bottom-0 w-2 bg-white rounded-full shadow-md border-2 border-slate-900 -translate-x-1/2"
            style="left: {pressurePercent}%;"
          ></div>
        </div>
        <div class="flex justify-between text-[0.625rem] text-[var(--text-soft)] font-semibold px-0.5">
          <span>90</span>
          <span class="text-emerald-500 font-bold">120 (Optimal)</span>
          <span class="text-amber-500 font-bold">130</span>
          <span class="text-rose-500 font-bold">140+</span>
          <span>160</span>
        </div>
      </div>
    </div>

  <!-- 2. RHR SPARKLINE -->
  {:else if widget.type === 'rhr_sparkline'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex items-center justify-between">
      <div>
        <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase tracking-wider block">
          Ruhepuls (7T-Trend)
        </span>
        <div class="flex items-baseline gap-1 mt-1">
          <span class="text-3xl font-extrabold text-[var(--text-main)] tabular-nums">64</span>
          <span class="text-xs text-[var(--text-soft)]">bpm</span>
        </div>
        <span class="text-xs text-emerald-500 font-semibold block mt-1">↘ -3 bpm vs. Vormonat</span>
      </div>
      <div class="w-28 h-12">
        <svg class="w-full h-full overflow-visible" viewBox="0 0 100 40">
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
    </div>

  <!-- 3. SPO2 & VO2 MAX -->
  {:else if widget.type === 'spo2_vo2max'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full grid grid-cols-2 gap-3">
      <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-3 text-center flex flex-col justify-between">
        <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase">SpO2 Sättigung</span>
        <div class="text-2xl font-extrabold text-cyan-500 tabular-nums my-1">98%</div>
        <span class="text-[0.625rem] text-emerald-500 font-semibold">Normalbereich</span>
      </div>
      <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-3 text-center flex flex-col justify-between">
        <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase">VO2 Max Fitness</span>
        <div class="text-2xl font-extrabold text-[var(--color-primary)] tabular-nums my-1">52</div>
        <span class="text-[0.625rem] text-[var(--color-primary)] font-bold">Top 5% Altersgruppe</span>
      </div>
    </div>

  <!-- 4. CGM WAVE -->
  {:else if widget.type === 'cgm_wave'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex flex-col justify-between space-y-3">
      <div class="flex items-start justify-between">
        <div>
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase tracking-wider block">
            Kontinuierliche Glukose (CGM)
          </span>
          <div class="flex items-baseline gap-2 mt-0.5">
            <span class="text-3xl font-extrabold text-[var(--text-main)] tabular-nums">84</span>
            <span class="text-xs font-semibold text-[var(--text-soft)]">mg/dL</span>
            <span class="text-xs font-bold text-emerald-500 ml-1">&rarr; Stabil</span>
          </div>
        </div>
        <Badge variant="success">Korridor 70–140</Badge>
      </div>

      <div class="relative w-full h-16 pt-1">
        <svg class="w-full h-full overflow-visible" viewBox="0 0 500 80" preserveAspectRatio="none">
          <rect x="0" y="15" width="500" height="50" fill="#10b981" fill-opacity="0.06" rx="6" />
          <path
            d="M 0 55 Q 80 50 140 30 T 260 52 T 380 48 T 460 54 L 500 52"
            fill="none"
            stroke="#10b981"
            stroke-width="2.5"
            stroke-linecap="round"
          />
          <circle cx="500" cy="52" r="4.5" fill="#10b981" />
        </svg>
      </div>
    </div>

  <!-- 5. TIME IN RANGE -->
  {:else if widget.type === 'time_in_range'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex flex-col justify-between space-y-2">
      <div class="flex justify-between items-center">
        <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Time in Range</span>
        <span class="text-xs font-bold text-emerald-500">96% TIR</span>
      </div>
      <div class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums">
        23h 02m <span class="text-xs font-normal text-[var(--text-soft)]">im Zielbereich</span>
      </div>
      <div class="w-full bg-[var(--border-subtle)] h-2 rounded-full overflow-hidden flex">
        <div class="bg-emerald-500 h-full w-[96%]"></div>
        <div class="bg-amber-400 h-full flex-1"></div>
      </div>
    </div>

  <!-- 6. FASTING TRANSITION -->
  {:else if widget.type === 'fasting_transition'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex flex-col justify-between space-y-2">
      <div class="flex justify-between items-center">
        <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Fasten-Metabolismus</span>
        <span class="text-xs font-bold text-[var(--color-primary)]">16.5h Aktiv</span>
      </div>
      <div class="text-sm font-bold text-[var(--text-main)]">
        Tief-Autophagie und Ketogenese
      </div>
      <div class="w-full bg-[var(--border-subtle)] h-2 rounded-full overflow-hidden">
        <div class="bg-[var(--color-primary)] h-full rounded-full w-[85%]"></div>
      </div>
    </div>

  <!-- 7. RECOVERY BATTERY -->
  {:else if widget.type === 'recovery_battery'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex items-center justify-around gap-4">
      <div class="relative w-20 h-20 flex items-center justify-center shrink-0">
        <svg class="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="38" fill="none" stroke="var(--border-subtle)" stroke-width="8" />
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
          />
        </svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span class="text-xl font-extrabold text-[var(--text-main)] tabular-nums">88</span>
          <span class="text-[0.5625rem] font-bold text-[var(--text-muted)] uppercase">Score</span>
        </div>
      </div>
      <div>
        <span class="text-xs font-bold text-emerald-500 block">Exzellente Erholung</span>
        <span class="text-[0.6875rem] text-[var(--text-muted)] block mt-0.5">Empfohlener Strain: 14.0–17.5</span>
      </div>
    </div>

  <!-- 8. ANS BALANCE -->
  {:else if widget.type === 'ans_balance'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex flex-col justify-between space-y-3">
      <div class="flex justify-between items-center text-xs">
        <span class="text-[var(--color-primary)] font-bold">Parasympathikus (78%)</span>
        <span class="text-amber-500 font-bold">Sympathikus (22%)</span>
      </div>
      <div class="w-full h-2.5 rounded-full bg-[var(--border-subtle)] overflow-hidden flex">
        <div class="h-full bg-[var(--color-primary)] w-[78%] rounded-l-full"></div>
        <div class="h-full bg-amber-400 flex-1 rounded-r-full"></div>
      </div>
      <span class="text-[0.6875rem] text-[var(--text-muted)] block">Autonome Balance: Hohe Herzratenvariabilität (68 ms)</span>
    </div>

  <!-- 9. BIA SPECTRUM -->
  {:else if widget.type === 'bia_spectrum'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex flex-col justify-between space-y-3">
      <div class="flex justify-between items-center">
        <div>
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase block">Körperzusammensetzung</span>
          <div class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums mt-0.5">
            81.8 <span class="text-xs font-normal text-[var(--text-soft)]">kg (KFA 13.8%)</span>
          </div>
        </div>
        <Badge variant="success">Sportler</Badge>
      </div>
      <div class="w-full h-2.5 rounded-full overflow-hidden flex bg-[var(--border-subtle)]">
        <div class="h-full bg-[var(--color-primary)] w-[86.2%] rounded-l-full"></div>
        <div class="h-full bg-amber-400 w-[13.8%] rounded-r-full"></div>
      </div>
      <div class="flex justify-between text-[0.6875rem] font-semibold text-[var(--text-soft)]">
        <span>70.5 kg Muskeln</span>
        <span>11.3 kg Fett</span>
        <span>54.2 L Wasser</span>
      </div>
    </div>

  <!-- 10. WHTR GAUGE -->
  {:else if widget.type === 'whtr_gauge'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex flex-col justify-between space-y-2">
      <div class="flex justify-between items-center">
        <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Waist-to-Height Ratio</span>
        <span class="text-xs font-bold text-emerald-500">0.45 • Optimal</span>
      </div>
      <div class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums">
        82 <span class="text-xs font-normal text-[var(--text-soft)]">cm Taillenumfang</span>
      </div>
      <div class="w-full bg-[var(--border-subtle)] h-2 rounded-full overflow-hidden">
        <div class="bg-emerald-500 h-full rounded-full w-[45%]"></div>
      </div>
    </div>

  <!-- 11. ACTIVITY HISTOGRAM -->
  {:else if widget.type === 'activity_histogram'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex flex-col justify-between space-y-3">
      <div class="flex justify-between items-center">
        <div>
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase block">Schritte & Distanz</span>
          <div class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums mt-0.5">
            10.420 <span class="text-xs font-normal text-[var(--text-soft)]">/ 12.000 (8.2 km)</span>
          </div>
        </div>
        <Badge variant="activity">87% Ziel</Badge>
      </div>
      <div class="h-14 flex items-end justify-between gap-1 px-1">
        {#each [15, 85, 40, 20, 30, 25, 65, 35, 20, 30, 45, 95, 60] as val}
          <div
            class="flex-1 rounded-t-sm bg-orange-500/50 hover:bg-orange-500 transition-colors"
            style="height: {val}%;"
          ></div>
        {/each}
      </div>
    </div>

  <!-- 12. TDEE SPLIT -->
  {:else if widget.type === 'tdee_split'}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-[var(--shadow-card)] h-full flex flex-col justify-between space-y-2">
      <div class="flex justify-between items-center">
        <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">Gesamtenergie (TDEE)</span>
        <span class="text-xs font-bold text-orange-500">2.480 kcal</span>
      </div>
      <div class="text-sm font-semibold text-[var(--text-soft)]">
        640 kcal Aktiv + 1.840 kcal Grundumsatz
      </div>
      <div class="w-full h-2 rounded-full overflow-hidden flex bg-[var(--border-subtle)]">
        <div class="bg-orange-500 h-full w-[26%]"></div>
        <div class="bg-cyan-500 h-full flex-1"></div>
      </div>
    </div>

  <!-- EXISTING RICH WIDGETS -->
  {:else if widget.type === 'hydration_glass'}
    <HydrationWaveGlass bind:currentMl={waterAmount} />

  {:else if widget.type === 'fasting_clock'}
    <FastingMetabolicClock onopenfood={onopenfasting} />

  {:else if widget.type === 'hero_rings'}
    <HeroProgressRings hydration={{ current: waterAmount, target: 3000, percent: Math.round((waterAmount/3000)*100), label: 'Wasser' }} />

  {:else if widget.type === 'mood_sphere'}
    <MoodValenceSphere />

  {:else if widget.type === 'sleep_hypnogram'}
    <SleepHypnogram />

  {:else if widget.type === 'medication_dose'}
    <MedicationDoseCard />

  {:else if widget.type === 'habits_pills'}
    <HabitCheckPills />

  {:else if widget.type === 'habits_year'}
    <HabitYearMatrix />
  {/if}
</div>
