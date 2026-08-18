<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    systolic = 118,
    diastolic = 76,
    restingHr = 64,
    spo2 = 98,
    vo2max = 52
  } = $props<{
    systolic?: number;
    diastolic?: number;
    restingHr?: number;
    spo2?: number;
    vo2max?: number;
  }>();

  // ESC 2024 Blood Pressure Category determination
  let bpCategory = $derived(
    systolic < 120 && diastolic < 80
      ? 'Optimal'
      : systolic < 130 && diastolic < 85
        ? 'Normal'
        : systolic < 140 && diastolic < 90
          ? 'Hochnormal'
          : 'Hypertonie Grad 1'
  );

  // Position on the ESC pressure bar (0% = 90mmHg, 100% = 160mmHg)
  let pressurePercent = $derived(Math.min(100, Math.max(0, ((systolic - 90) / (160 - 90)) * 100)));
</script>

<div
  class="space-y-5 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)] sm:p-6"
>
  <!-- Widget Header -->
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-3">
      <div
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-rose-500/10 font-bold text-rose-500"
      >
        <Icon name="labs" size={20} />
      </div>
      <div>
        <h2 class="text-sm font-extrabold text-[var(--text-main)]">Kardiovaskuläres Vitalprofil</h2>
        <p class="text-xs text-[var(--text-muted)]">
          Hämodynamik, Ruhepuls-Trend und Sauerstoffsättigung
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="success" class="font-bold">{bpCategory} (ESC 2024)</Badge>
    </div>
  </div>

  <!-- Interactive Dual-Card Visual Layout -->
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-12">
    <!-- Left Hero (7-Col): Blood Pressure Arterial Gauge & Zone Scale -->
    <div
      class="flex flex-col justify-between space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 sm:p-5 lg:col-span-7"
    >
      <div class="flex items-start justify-between">
        <div>
          <span
            class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
          >
            Arterieller Blutdruck
          </span>
          <div class="mt-1 flex items-baseline gap-2">
            <span
              class="text-3xl font-extrabold tracking-tight text-[var(--text-main)] tabular-nums sm:text-4xl"
            >
              {systolic}
            </span>
            <span class="text-xl font-bold text-[var(--text-muted)] tabular-nums sm:text-2xl">
              / {diastolic}
            </span>
            <span class="ml-0.5 text-xs font-semibold text-[var(--text-soft)]">mmHg</span>
          </div>
        </div>

        <!-- Pulse Pressure Indicator -->
        <div class="text-right">
          <span class="block text-[0.6875rem] font-semibold text-[var(--text-soft)]">Pulsdruck</span
          >
          <span class="text-sm font-bold text-[var(--text-main)] tabular-nums"
            >{systolic - diastolic} mmHg</span
          >
          <span class="block text-[0.625rem] font-semibold text-emerald-500"
            >Geringe Gefäßsteifigkeit</span
          >
        </div>
      </div>

      <!-- Multi-Zone ESC 2024 Bar Gauge -->
      <div class="space-y-1.5 pt-1">
        <div class="relative flex h-2.5 overflow-hidden rounded-full bg-[var(--border-subtle)]">
          <!-- Zone 1: Optimal (<120) -->
          <div class="h-full w-[42%] bg-emerald-500"></div>
          <!-- Zone 2: Normal (120-129) -->
          <div class="h-full w-[15%] bg-teal-400"></div>
          <!-- Zone 3: Hochnormal (130-139) -->
          <div class="h-full w-[15%] bg-amber-400"></div>
          <!-- Zone 4: Hypertonie (>=140) -->
          <div class="h-full flex-1 bg-rose-500"></div>

          <!-- Current Pressure Indicator Marker -->
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
    </div>

    <!-- Right Hero (5-Col): RHR Sparkline & VO2 Max Dial -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:col-span-5 lg:grid-cols-1">
      <!-- RHR Sparkline Card -->
      <div
        class="flex items-center justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4"
      >
        <div>
          <span
            class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
          >
            Ruhepuls (7T-Trend)
          </span>
          <div class="mt-0.5 flex items-baseline gap-1">
            <span class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums"
              >{restingHr}</span
            >
            <span class="text-xs text-[var(--text-soft)]">bpm</span>
          </div>
          <span class="mt-0.5 block text-[0.625rem] font-semibold text-emerald-500"
            >↘ -3 bpm vs. Vormonat</span
          >
        </div>

        <!-- 7-Day Sparkline SVG -->
        <div class="h-10 w-24">
          <svg class="h-full w-full overflow-visible" viewBox="0 0 100 40">
            <path
              d="M 0 35 L 16 28 L 33 22 L 50 22 L 66 16 L 83 16 L 100 16"
              fill="none"
              stroke="#059669"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <circle cx="100" cy="16" r="3.5" fill="#059669" />
          </svg>
        </div>
      </div>

      <!-- SpO2 & VO2 Max Dual Micro-Tiles -->
      <div class="grid grid-cols-2 gap-2">
        <!-- SpO2 -->
        <div
          class="flex flex-col justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-center"
        >
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >SpO2 Sättigung</span
          >
          <div class="my-1 text-xl font-extrabold text-cyan-500 tabular-nums">{spo2}%</div>
          <div class="h-1 w-full overflow-hidden rounded-full bg-[var(--border-subtle)]">
            <div class="h-full rounded-full bg-cyan-500" style="width: {spo2}%;"></div>
          </div>
        </div>

        <!-- VO2 Max -->
        <div
          class="flex flex-col justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-center"
        >
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase"
            >VO2 Max Fitness</span
          >
          <div class="my-1 text-xl font-extrabold text-[var(--color-primary)] tabular-nums">
            {vo2max}
          </div>
          <span class="text-[0.625rem] font-bold text-[var(--color-primary)]"
            >Top 5% Altersgruppe</span
          >
        </div>
      </div>
    </div>
  </div>
</div>
