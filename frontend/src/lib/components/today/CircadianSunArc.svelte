<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { calculateSolarTimes } from '$lib/analytics/views/circadian';
  import { todayString } from '$lib/utils/datetime';

  let now = $state(new Date());

  $effect(() => {
    const timer = setInterval(() => {
      now = new Date();
    }, 60000);
    return () => clearInterval(timer);
  });

  const today = todayString();
  const solar = calculateSolarTimes(today, 52.52, 13.405, -new Date().getTimezoneOffset() / 60);

  let currentMins = $derived(now.getHours() * 60 + now.getMinutes());
  let sunPositionPercent = $derived(Math.max(5, Math.min(95, (currentMins / (24 * 60)) * 100)));

  let normX = $derived(sunPositionPercent / 100);
  let sunHeightPercent = $derived(Math.max(12, Math.min(75, 75 - 60 * Math.sin(normX * Math.PI))));

  let activePhase = $derived.by(() => {
    const h = now.getHours();
    if (h >= 6 && h < 9) return 'Cortisol-Peak & Morgenlicht';
    if (h >= 9 && h < 12) return 'Kognitiver Vormittags-Fokus';
    if (h >= 12 && h < 14) return 'Postprandiales Tal / Erholung';
    if (h >= 14 && h < 18) return 'Kognitiver Nachmittags-Fokus';
    if (h >= 18 && h < 21) return 'Maximale Muskelkraft & Koordination';
    if (h >= 21 && h < 23) return 'Melatonin-Ausschüttung & Wind-Down';
    return 'Tiefer Erholungsschlaf';
  });

  let alignmentScore = 94;
  let showWindows = $state(false);
</script>

<div
  class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)] transition-all"
>
  <!-- Standardized Header -->
  <div class="flex items-start justify-between gap-3">
    <div class="flex min-w-0 items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
        style="background-color: color-mix(in srgb, var(--color-circadian) 12%, transparent); color: var(--color-circadian);"
      >
        <Icon name="wb-sunny" size="md" />
      </div>
      <div class="min-w-0">
        <h3 class="truncate text-sm font-extrabold tracking-tight text-[var(--text-main)]">
          Zirkadianer 24h-Sonnenbogen
        </h3>
        <p class="truncate text-xs text-[var(--text-muted)]">
          Aufgang {solar.sunrise} &bull; Untergang {solar.sunset} &bull; {alignmentScore}% Alignment
        </p>
      </div>
    </div>

    <div class="flex shrink-0 items-center gap-2">
      <Badge
        variant="fasting"
        class="hidden text-[0.625rem] font-bold !text-[var(--color-circadian)] sm:inline-flex"
      >
        {activePhase}
      </Badge>
      <button
        type="button"
        onclick={() => (showWindows = !showWindows)}
        class="cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2.5 py-1 text-[0.6875rem] font-bold text-[var(--text-main)] transition-all hover:bg-[var(--bg-surface-100)]"
      >
        {showWindows ? 'Schließen' : 'Zeitfenster'}
      </button>
    </div>
  </div>

  <!-- Collapsible Physiological Time Windows (from services/circadian.py) -->
  {#if showWindows}
    <div
      class="grid animate-[fadeIn_0.15s_ease-out] grid-cols-1 gap-2.5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3 text-xs sm:grid-cols-2 md:grid-cols-4"
    >
      <!-- 1. Morgenlicht -->
      <div
        class="space-y-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2.5"
      >
        <div class="flex items-center justify-between">
          <span class="flex items-center gap-1.5 font-bold text-[var(--text-main)]">
            <Icon name="wb-sunny" size="sm" class="text-[var(--color-circadian)]" /> Morgenlicht
          </span>
          <span class="font-bold text-[var(--color-circadian)]">{solar.sunrise}</span>
        </div>
        <p class="text-[0.6875rem] leading-tight text-[var(--text-muted)]">
          10–15 Min. direktes Sonnenlicht stoppt Melatonin und startet den 14h-Timer.
        </p>
      </div>

      <!-- 2. Peak Fokus -->
      <div
        class="space-y-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2.5"
      >
        <div class="flex items-center justify-between">
          <span class="flex items-center gap-1.5 font-bold text-[var(--text-main)]">
            <Icon name="psychology" size="sm" class="text-[var(--color-primary)]" /> Fokus-Fenster
          </span>
          <span class="font-bold text-[var(--color-primary)]">10:00–12:30</span>
        </div>
        <p class="text-[0.6875rem] leading-tight text-[var(--text-muted)]">
          Cortisol-Plateau &amp; maximale neuronale Signalübertragung für Tiefenarbeit.
        </p>
      </div>

      <!-- 3. Koffein-Cutoff -->
      <div
        class="space-y-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2.5"
      >
        <div class="flex items-center justify-between">
          <span class="flex items-center gap-1.5 font-bold text-[var(--text-main)]">
            <Icon name="coffee" size="sm" class="text-[var(--color-activity)]" /> Koffein-Cutoff
          </span>
          <span class="font-bold text-[var(--color-activity)]">14:30</span>
        </div>
        <p class="text-[0.6875rem] leading-tight text-[var(--text-muted)]">
          5.5h Halbwertszeit zur Vermeidung von Rezeptorblockaden im Tiefschlaf.
        </p>
      </div>

      <!-- 4. Melatonin-Onset -->
      <div
        class="space-y-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2.5"
      >
        <div class="flex items-center justify-between">
          <span class="flex items-center gap-1.5 font-bold text-[var(--text-main)]">
            <Icon name="bedtime" size="sm" class="text-[var(--color-vital)]" /> Melatonin Onset
          </span>
          <span class="font-bold text-[var(--color-vital)]">{solar.sunset}</span>
        </div>
        <p class="text-[0.6875rem] leading-tight text-[var(--text-muted)]">
          Natürlicher Peak nach Sonnenuntergang. Blaulichtreduktion ab 21:00 empfohlen.
        </p>
      </div>
    </div>
  {/if}

  <!-- Responsive Arc Stage (Zero SVG Distortion, Mobile Optimized) -->
  <div class="relative h-[110px] w-full pt-1 select-none sm:h-[125px]">
    <!-- Background SVG Curve -->
    <svg
      class="h-[75px] w-full overflow-visible sm:h-[85px]"
      viewBox="0 0 1000 100"
      preserveAspectRatio="none"
    >
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
        x1="20"
        y1="85"
        x2="980"
        y2="85"
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
        opacity="0.4"
      />

      <!-- Daylight Area Fill under Curve -->
      <path d="M 60 85 Q 500 0 940 85 Z" fill="url(#circadianDayGlow)" />

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
      class="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-1/2 transition-all duration-500"
      style="left: {sunPositionPercent}%; top: {sunHeightPercent}%;"
    >
      <div class="relative flex items-center justify-center">
        <div
          class="absolute h-9 w-9 animate-ping rounded-full bg-[var(--color-circadian)] opacity-25"
        ></div>
        <div class="h-6 w-6 rounded-full bg-[var(--color-circadian)] opacity-35 blur-xs"></div>
        <div
          class="absolute h-3.5 w-3.5 rounded-full border-2 border-[var(--color-circadian)] bg-white shadow-sm"
        ></div>
      </div>
    </div>

    <!-- RESPONSIVE TYPOGRAPHIC LABELS (Never Overflows) -->
    <div
      class="absolute inset-x-0 bottom-0 flex items-end justify-between px-1 text-xs font-semibold select-none"
    >
      <!-- Sunrise (Left-aligned) -->
      <div class="flex flex-col items-start text-left">
        <span class="mb-1 h-1.5 w-1.5 rounded-full bg-[var(--border-strong)]"></span>
        <span class="text-[0.625rem] font-medium text-[var(--text-muted)] sm:text-[0.6875rem]">
          {solar.sunrise} <span class="hidden sm:inline">Morgenlicht</span>
        </span>
      </div>

      <!-- Peak Focus (Center) -->
      <div class="hidden flex-col items-center sm:flex">
        <span class="mb-1 h-1.5 w-1.5 rounded-full bg-[var(--color-circadian)]"></span>
        <span class="text-[0.6875rem] font-bold text-[var(--color-circadian)]">
          10:00 Peak Fokus
        </span>
      </div>

      <!-- Caffeine Cutoff (Center-Right) -->
      <div class="flex flex-col items-center">
        <span class="mb-1 h-1.5 w-1.5 rounded-full bg-[var(--color-activity)]"></span>
        <span class="text-[0.625rem] font-bold text-[var(--color-activity)] sm:text-[0.6875rem]">
          14:30 <span class="hidden sm:inline">Koffein-Stop</span>
        </span>
      </div>

      <!-- Sunset (Right-aligned, zero translation) -->
      <div class="flex flex-col items-end text-right">
        <span class="mb-1 h-1.5 w-1.5 rounded-full bg-[var(--border-strong)]"></span>
        <span class="text-[0.625rem] font-medium text-[var(--text-muted)] sm:text-[0.6875rem]">
          {solar.sunset} <span class="hidden sm:inline">Sonnenuntergang</span>
        </span>
      </div>
    </div>
  </div>
</div>
