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

  // 7-Day Resting Heart Rate History
  const rhrHistory = [68, 66, 65, 65, 64, 64, 64];

  // ESC 2024 Blood Pressure Category determination
  let bpCategory = $derived(
    systolic < 120 && diastolic < 80 ? 'Optimal' :
    systolic < 130 && diastolic < 85 ? 'Normal' :
    systolic < 140 && diastolic < 90 ? 'Hochnormal' : 'Hypertonie Grad 1'
  );

  // Position on the ESC pressure bar (0% = 90mmHg, 100% = 160mmHg)
  let pressurePercent = $derived(
    Math.min(100, Math.max(0, ((systolic - 90) / (160 - 90)) * 100))
  );
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 sm:p-6 shadow-[var(--shadow-card)] space-y-5">
  <!-- Widget Header -->
  <div class="flex items-center justify-between flex-wrap gap-2">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-2xl bg-rose-500/10 text-rose-500 flex items-center justify-center font-bold shrink-0">
        <Icon name="labs" size={20} />
      </div>
      <div>
        <h2 class="text-sm font-extrabold text-[var(--text-main)]">Kardiovaskuläres Vitalprofil</h2>
        <p class="text-xs text-[var(--text-muted)]">Hämodynamik, Ruhepuls-Trend und Sauerstoffsättigung</p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="success" class="font-bold">{bpCategory} (ESC 2024)</Badge>
    </div>
  </div>

  <!-- Interactive Dual-Card Visual Layout -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
    
    <!-- Left Hero (7-Col): Blood Pressure Arterial Gauge & Zone Scale -->
    <div class="lg:col-span-7 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 sm:p-5 flex flex-col justify-between space-y-4">
      <div class="flex items-start justify-between">
        <div>
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase tracking-wider block">
            Arterieller Blutdruck
          </span>
          <div class="flex items-baseline gap-2 mt-1">
            <span class="text-3xl sm:text-4xl font-extrabold text-[var(--text-main)] tabular-nums tracking-tight">
              {systolic}
            </span>
            <span class="text-xl sm:text-2xl font-bold text-[var(--text-muted)] tabular-nums">
              / {diastolic}
            </span>
            <span class="text-xs font-semibold text-[var(--text-soft)] ml-0.5">mmHg</span>
          </div>
        </div>

        <!-- Pulse Pressure Indicator -->
        <div class="text-right">
          <span class="text-[0.6875rem] text-[var(--text-soft)] block font-semibold">Pulsdruck</span>
          <span class="text-sm font-bold text-[var(--text-main)] tabular-nums">{systolic - diastolic} mmHg</span>
          <span class="text-[0.625rem] text-emerald-500 font-semibold block">Geringe Gefäßsteifigkeit</span>
        </div>
      </div>

      <!-- Multi-Zone ESC 2024 Bar Gauge -->
      <div class="space-y-1.5 pt-1">
        <div class="relative h-2.5 rounded-full overflow-hidden flex bg-[var(--border-subtle)]">
          <!-- Zone 1: Optimal (<120) -->
          <div class="h-full bg-emerald-500 w-[42%]"></div>
          <!-- Zone 2: Normal (120-129) -->
          <div class="h-full bg-teal-400 w-[15%]"></div>
          <!-- Zone 3: Hochnormal (130-139) -->
          <div class="h-full bg-amber-400 w-[15%]"></div>
          <!-- Zone 4: Hypertonie (>=140) -->
          <div class="h-full bg-rose-500 flex-1"></div>

          <!-- Current Pressure Indicator Marker -->
          <div
            class="absolute top-0 bottom-0 w-2 bg-white rounded-full shadow-md border-2 border-slate-900 -translate-x-1/2 transition-all duration-500"
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

    <!-- Right Hero (5-Col): RHR Sparkline & VO2 Max Dial -->
    <div class="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-3">
      
      <!-- RHR Sparkline Card -->
      <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4 flex items-center justify-between">
        <div>
          <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase tracking-wider block">
            Ruhepuls (7T-Trend)
          </span>
          <div class="flex items-baseline gap-1 mt-0.5">
            <span class="text-2xl font-extrabold text-[var(--text-main)] tabular-nums">{restingHr}</span>
            <span class="text-xs text-[var(--text-soft)]">bpm</span>
          </div>
          <span class="text-[0.625rem] text-emerald-500 font-semibold block mt-0.5">↘ -3 bpm vs. Vormonat</span>
        </div>

        <!-- 7-Day Sparkline SVG -->
        <div class="w-24 h-10">
          <svg class="w-full h-full overflow-visible" viewBox="0 0 100 40">
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
        <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-3 text-center flex flex-col justify-between">
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase">SpO2 Sättigung</span>
          <div class="text-xl font-extrabold text-cyan-500 tabular-nums my-1">{spo2}%</div>
          <div class="w-full bg-[var(--border-subtle)] h-1 rounded-full overflow-hidden">
            <div class="bg-cyan-500 h-full rounded-full" style="width: {spo2}%;"></div>
          </div>
        </div>

        <!-- VO2 Max -->
        <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-3 text-center flex flex-col justify-between">
          <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase">VO2 Max Fitness</span>
          <div class="text-xl font-extrabold text-[var(--color-primary)] tabular-nums my-1">{vo2max}</div>
          <span class="text-[0.625rem] text-[var(--color-primary)] font-bold">Top 5% Altersgruppe</span>
        </div>
      </div>

    </div>

  </div>
</div>
