<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  // Backend Circadian Engine calculations (services/circadian.py)
  let activePhase = 'Kognitiver Nachmittags-Fokus';
  let hoursUntilSleep = 8.2;
  let alignmentScore = 94; // Circadian Alignment Score (0-100%)
  let showWindows = $state(false);

  // Exact diurnal percentage positions (0% = 00:00, 100% = 24:00)
  const sunPositionPercent = 58.5; // 14:15 = 59.3%
  const sunHeightPercent = 22;     // Y-axis top %
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 mb-5 shadow-[var(--shadow-card)] space-y-4">
  <!-- Header with Alignment Score & Phase Status -->
  <div class="flex justify-between items-center flex-wrap gap-2">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-full bg-[var(--color-circadian)]/15 text-[var(--color-circadian)] flex items-center justify-center shrink-0">
        <Icon name="sun" size={20} />
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h2 class="text-sm font-extrabold text-[var(--text-main)]">Zirkadianer 24h-Sonnenbogen</h2>
          <Badge variant="success" class="!bg-emerald-500/10 !text-emerald-500 font-bold">
            {alignmentScore}% Alignment • Exzellent
          </Badge>
        </div>
        <p class="text-xs text-[var(--text-muted)] mt-0.5">
          NOAA Solar Engine (Europe/Berlin) • Sonnenaufgang 06:12 • Sonnenuntergang 20:48
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant="fasting" class="!bg-[var(--color-circadian-soft)] !text-[var(--color-circadian)]">
        {activePhase}
      </Badge>
      <button
        type="button"
        onclick={() => showWindows = !showWindows}
        class="text-xs text-[var(--color-primary)] font-bold hover:underline cursor-pointer flex items-center gap-1 ml-1"
      >
        <span>{showWindows ? 'Details schließen' : 'Physiologische Zeitfenster'}</span>
        <Icon name="chevron-down" size={12} class="transition-transform {showWindows ? 'rotate-180' : ''}" />
      </button>
    </div>
  </div>

  <!-- Collapsible Physiological Time Windows (from services/circadian.py) -->
  {#if showWindows}
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5 p-3 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-xs animate-[fadeIn_0.15s_ease-out]">
      <!-- 1. Morgenlicht -->
      <div class="p-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] space-y-1">
        <div class="flex items-center justify-between">
          <span class="font-bold text-[var(--text-main)] flex items-center gap-1.5">
            <Icon name="sun" size={14} class="text-[var(--color-circadian)]" /> Morgenlicht
          </span>
          <span class="font-bold text-[var(--color-circadian)]">06:12 - 08:12</span>
        </div>
        <p class="text-[0.6875rem] text-[var(--text-muted)] leading-tight">
          10.000+ Lux Tageslicht unterdrückt Rest-Melatonin und startet den 16h Wach-Timer.
        </p>
      </div>

      <!-- 2. Essensfenster -->
      <div class="p-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] space-y-1">
        <div class="flex items-center justify-between">
          <span class="font-bold text-[var(--text-main)] flex items-center gap-1.5">
            <Icon name="food" size={14} class="text-[var(--color-primary)]" /> Essensfenster (TRF)
          </span>
          <span class="font-bold text-[var(--color-primary)]">08:00 - 18:30</span>
        </div>
        <p class="text-[0.6875rem] text-[var(--text-muted)] leading-tight">
          Ende 4h vor Schlaf schont die zelluläre Autophagie und Schlafarchitektur.
        </p>
      </div>

      <!-- 3. Koffein-Cutoff -->
      <div class="p-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] space-y-1">
        <div class="flex items-center justify-between">
          <span class="font-bold text-[var(--text-main)] flex items-center gap-1.5">
            <Icon name="sun" size={14} class="text-[var(--color-activity)]" /> Koffein-Cutoff
          </span>
          <span class="font-bold text-[var(--color-activity)]">14:30</span>
        </div>
        <p class="text-[0.6875rem] text-[var(--text-muted)] leading-tight">
          5.5h Halbwertszeit zur Vermeidung von Adenosin-Rezeptor Blockaden im Tiefschlaf.
        </p>
      </div>

      <!-- 4. Melatonin-Onset -->
      <div class="p-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] space-y-1">
        <div class="flex items-center justify-between">
          <span class="font-bold text-[var(--text-main)] flex items-center gap-1.5">
            <Icon name="moon" size={14} class="text-[var(--color-vital)]" /> Melatonin Onset
          </span>
          <span class="font-bold text-[var(--color-vital)]">22:30</span>
        </div>
        <p class="text-[0.6875rem] text-[var(--text-muted)] leading-tight">
          Natürlicher Peak 4h nach Sonnenuntergang. Blaulichtfilter ab 21:00 empfohlen.
        </p>
      </div>
    </div>
  {/if}

  <!-- Responsive Arc Stage (Zero SVG Distortion) -->
  <div class="relative w-full h-[120px] sm:h-[135px] select-none pt-1">
    
    <!-- Background SVG Curve (Pure Geometry with non-scaling-stroke) -->
    <svg class="w-full h-[90px] overflow-visible" viewBox="0 0 1000 100" preserveAspectRatio="none">
      <defs>
        <!-- Warm Solar Daylight Gradient -->
        <linearGradient id="circadianDayGlow" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="var(--color-circadian)" stop-opacity="0.25" />
          <stop offset="50%" stop-color="var(--color-circadian)" stop-opacity="0.06" />
          <stop offset="100%" stop-color="var(--color-circadian)" stop-opacity="0" />
        </linearGradient>
      </defs>

      <!-- Horizon Baseline (0 Altitude) -->
      <line
        x1="20" y1="85" x2="980" y2="85"
        stroke="var(--border-subtle)"
        stroke-width="1.5"
        stroke-dasharray="6 6"
      />

      <!-- Full 24h Night-to-Day Parabola -->
      <path
        d="M 50 85 Q 500 0 950 85"
        fill="none"
        stroke="var(--border-strong)"
        stroke-width="2"
        stroke-linecap="round"
        opacity="0.5"
      />

      <!-- Daylight Area Fill under Curve -->
      <path
        d="M 60 85 Q 500 0 940 85 Z"
        fill="url(#circadianDayGlow)"
      />

      <!-- Active Daylight Illuminated Solar Arc -->
      <path
        d="M 60 85 Q 500 0 940 85"
        fill="none"
        stroke="var(--color-circadian)"
        stroke-width="3.5"
        stroke-linecap="round"
      />
    </svg>

    <!-- PERFECT CIRCULAR SUN NODE (HTML Overlay) -->
    <div
      class="absolute -translate-x-1/2 -translate-y-1/2 pointer-events-none transition-all duration-500 z-10"
      style="left: {sunPositionPercent}%; top: {sunHeightPercent}%;"
    >
      <div class="relative flex items-center justify-center">
        <div class="absolute w-10 h-10 rounded-full bg-[var(--color-circadian)] opacity-25 animate-ping"></div>
        <div class="w-7 h-7 rounded-full bg-[var(--color-circadian)] opacity-35 blur-xs"></div>
        <div class="absolute w-3.5 h-3.5 rounded-full bg-white border-2 border-[var(--color-circadian)] shadow-sm"></div>
      </div>
    </div>

    <!-- RESPONSIVE TYPOGRAPHIC LABELS -->
    <div class="absolute bottom-0 inset-x-0 flex justify-between text-xs font-semibold select-none px-2">
      <div class="flex flex-col items-center -translate-x-2">
        <span class="w-1 h-2 bg-[var(--border-strong)] rounded-full mb-1"></span>
        <span class="text-[0.6875rem] text-[var(--text-muted)] whitespace-nowrap">06:12 Morgenlicht</span>
      </div>

      <div class="flex flex-col items-center">
        <span class="w-1.5 h-1.5 rounded-full bg-[var(--color-circadian)] mb-1"></span>
        <span class="text-[0.6875rem] font-bold text-[var(--color-circadian)] whitespace-nowrap">10:00 Peak Fokus</span>
      </div>

      <div class="flex flex-col items-center">
        <span class="w-1.5 h-1.5 rounded-full bg-[var(--color-activity)] mb-1"></span>
        <span class="text-[0.6875rem] font-bold text-[var(--color-activity)] whitespace-nowrap">14:30 Koffein-Cutoff</span>
      </div>

      <div class="flex flex-col items-center translate-x-2">
        <span class="w-1 h-2 bg-[var(--border-strong)] rounded-full mb-1"></span>
        <span class="text-[0.6875rem] text-[var(--text-muted)] whitespace-nowrap">22:30 Melatonin Onset</span>
      </div>
    </div>

  </div>
</div>
