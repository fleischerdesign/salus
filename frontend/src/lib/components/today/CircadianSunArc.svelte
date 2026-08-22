<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { calculateSolarTimes } from '$lib/analytics/views/circadian';
  import { todayString } from '$lib/utils/datetime';
  import { userTimezone, getTimezoneOffsetHours } from '$lib/utils/timezone';

  interface Props {
    date?: string;
  }

  let { date = todayString() }: Props = $props();

  let now = $state(new Date());

  $effect(() => {
    const timer = setInterval(() => {
      now = new Date();
    }, 30000);
    return () => clearInterval(timer);
  });

  const tz = $derived(userTimezone());
  const tzOffset = $derived(getTimezoneOffsetHours(tz, new Date(date + 'T12:00:00Z')));
  const solar = $derived(calculateSolarTimes(date, 52.52, 13.405, tzOffset));

  let currentMins = $derived(now.getHours() * 60 + now.getMinutes());

  // Day vs Night Mode (Model B: Dynamic Day/Night Cycle)
  let isDay = $derived(currentMins >= solar.sunrise_mins && currentMins <= solar.sunset_mins);

  let cycleProgress = $derived.by(() => {
    if (isDay) {
      const dayDuration = Math.max(1, solar.sunset_mins - solar.sunrise_mins);
      return Math.max(0, Math.min(1, (currentMins - solar.sunrise_mins) / dayDuration));
    } else {
      const nightDuration = Math.max(1, 1440 - solar.sunset_mins + solar.sunrise_mins);
      const elapsed =
        currentMins >= solar.sunset_mins
          ? currentMins - solar.sunset_mins
          : 1440 - solar.sunset_mins + currentMins;
      return Math.max(0, Math.min(1, elapsed / nightDuration));
    }
  });

  // Strictly maps 0% (cycle start) -> 5% and 100% (cycle end) -> 95%
  let sunPositionPercent = $derived(5 + cycleProgress * 90);

  // Height: 75% at horizon (progress 0 & 1) down to 15% at apex (progress 0.5)
  let sunHeightPercent = $derived(
    Math.max(12, Math.min(75, 75 - 60 * Math.sin(cycleProgress * Math.PI)))
  );

  let activePhase = $derived.by(() => {
    if (isDay) {
      const dayElapsedMins = currentMins - solar.sunrise_mins;
      if (dayElapsedMins < 45) return 'Cortisol-Peak & Morgenlicht';
      if (currentMins < 720) return 'Kognitiver Vormittags-Fokus';
      if (currentMins < 840) return 'Postprandiales Tal / Erholung';
      if (currentMins < 1080) return 'Kognitiver Nachmittags-Fokus';
      if (currentMins < solar.sunset_mins) return 'Maximale Muskelkraft & Koordination';
      return 'Dämmerung & Tagesausklang';
    } else {
      const nightElapsedMins =
        currentMins >= solar.sunset_mins
          ? currentMins - solar.sunset_mins
          : 1440 - solar.sunset_mins + currentMins;
      if (nightElapsedMins < 90) return 'Blaulicht-Reduktion & Wind-Down';
      if (nightElapsedMins < 180) return 'Melatonin-Anstieg & Einschlaffenster';
      if (currentMins >= 120 && currentMins < 300) return 'Tiefschlaf & Zelluläre Regeneration';
      return 'Aufwach- & Übergangsphase';
    }
  });

  // Segment interface
  interface ArcSegment {
    id: string;
    name: string;
    shortName: string;
    startMins: number;
    endMins: number;
    tStart: number; // 0.0 to 1.0
    tEnd: number; // 0.0 to 1.0
    pathData: string;
    colorVar: string;
    textClass: string;
    timeText: string;
    centerPercent: number;
    isActive: boolean;
  }

  function formatMins(m: number): string {
    const norm = ((Math.round(m) % 1440) + 1440) % 1440;
    const hh = String(Math.floor(norm / 60)).padStart(2, '0');
    const mm = String(norm % 60).padStart(2, '0');
    return `${hh}:${mm}`;
  }

  // De Casteljau subdivision for exact quadratic Bezier arc segments
  function getSubBezierPath(
    p0: { x: number; y: number },
    p1: { x: number; y: number },
    p2: { x: number; y: number },
    ta: number,
    tb: number
  ): string {
    const q0 = { x: (1 - ta) * p0.x + ta * p1.x, y: (1 - ta) * p0.y + ta * p1.y };
    const q1 = { x: (1 - ta) * p1.x + ta * p2.x, y: (1 - ta) * p1.y + ta * p2.y };
    const s0 = { x: (1 - ta) * q0.x + ta * q1.x, y: (1 - ta) * q0.y + ta * q1.y };

    const r0 = { x: (1 - tb) * p0.x + tb * p1.x, y: (1 - tb) * p0.y + tb * p1.y };
    const r1 = { x: (1 - tb) * p1.x + tb * p2.x, y: (1 - tb) * p1.y + tb * p2.y };
    const s2 = { x: (1 - tb) * r0.x + tb * r1.x, y: (1 - tb) * r0.y + tb * r1.y };

    const s1 = { x: (1 - ta) * r0.x + ta * r1.x, y: (1 - ta) * r0.y + ta * r1.y };

    return `M ${s0.x.toFixed(1)} ${s0.y.toFixed(1)} Q ${s1.x.toFixed(1)} ${s1.y.toFixed(1)} ${s2.x.toFixed(1)} ${s2.y.toFixed(1)}`;
  }

  const ARC_P0 = { x: 50, y: 85 };
  const ARC_P1 = { x: 500, y: 0 };
  const ARC_P2 = { x: 950, y: 85 };

  // Calculate segment progress limits & geometry
  let segments = $derived.by(() => {
    if (isDay) {
      const dayDuration = Math.max(1, solar.sunset_mins - solar.sunrise_mins);
      const z1End = Math.min(solar.sunrise_mins + 150, solar.solar_noon_mins - 60);
      const z2End = Math.max(z1End + 60, solar.solar_noon_mins + 60);
      const z3End = Math.max(z2End + 60, solar.sunset_mins - 60);

      const raw = [
        {
          id: 'morning_light',
          name: 'Morgenlicht',
          shortName: 'Licht',
          startMins: solar.sunrise_mins,
          endMins: z1End,
          colorVar: 'var(--color-circadian)',
          textClass: 'text-circadian',
          timeText: `${solar.sunrise} – ${formatMins(z1End)}`
        },
        {
          id: 'peak_focus',
          name: 'Peak Fokus',
          shortName: 'Fokus',
          startMins: z1End,
          endMins: z2End,
          colorVar: 'var(--color-primary)',
          textClass: 'text-primary',
          timeText: `${formatMins(z1End)} – ${formatMins(z2End)}`
        },
        {
          id: 'caffeine_recovery',
          name: 'Koffein-Cutoff',
          shortName: 'Cutoff',
          startMins: z2End,
          endMins: z3End,
          colorVar: 'var(--color-activity)',
          textClass: 'text-activity',
          timeText: `${formatMins(z2End)} – ${formatMins(z3End)}`
        },
        {
          id: 'dusk',
          name: 'Dämmerung',
          shortName: 'Dämmerung',
          startMins: z3End,
          endMins: solar.sunset_mins,
          colorVar: 'var(--color-sleep)',
          textClass: 'text-sleep',
          timeText: `${formatMins(z3End)} – ${solar.sunset}`
        }
      ];

      return raw.map((item) => {
        const tStart = Math.max(
          0,
          Math.min(1, (item.startMins - solar.sunrise_mins) / dayDuration)
        );
        const tEnd = Math.max(0, Math.min(1, (item.endMins - solar.sunrise_mins) / dayDuration));
        const pathData = getSubBezierPath(ARC_P0, ARC_P1, ARC_P2, tStart, tEnd);
        const tCenter = (tStart + tEnd) / 2;
        const centerPercent = 5 + tCenter * 90;
        const isActive = currentMins >= item.startMins && currentMins < item.endMins;

        return {
          ...item,
          tStart,
          tEnd,
          pathData,
          centerPercent,
          isActive
        } satisfies ArcSegment;
      });
    } else {
      const nightDuration = Math.max(1, 1440 - solar.sunset_mins + solar.sunrise_mins);
      const z1End = solar.sunset_mins + 90;
      const z2End = solar.sunset_mins + 190;
      const z3End = (solar.sunrise_mins - 60 + 1440) % 1440;

      const raw = [
        {
          id: 'blue_blocker',
          name: 'Blaulichtfilter',
          shortName: 'Filter',
          startMins: solar.sunset_mins,
          endMins: z1End,
          colorVar: 'var(--color-sleep)',
          textClass: 'text-sleep',
          timeText: `${solar.sunset} – ${formatMins(z1End)}`
        },
        {
          id: 'sleep_window',
          name: 'Einschlafen',
          shortName: 'Schlaf',
          startMins: z1End,
          endMins: z2End,
          colorVar: 'var(--color-fasting)',
          textClass: 'text-fasting',
          timeText: `${formatMins(z1End)} – ${formatMins(z2End)}`
        },
        {
          id: 'deep_sleep_nadir',
          name: 'Tiefschlaf (Nadir)',
          shortName: 'Tiefschlaf',
          startMins: z2End,
          endMins: z3End,
          colorVar: 'var(--color-primary)',
          textClass: 'text-primary',
          timeText: `${formatMins(z2End)} – ${formatMins(z3End)}`
        },
        {
          id: 'wake_prep',
          name: 'Aufwachfenster',
          shortName: 'Aufwachen',
          startMins: z3End,
          endMins: solar.sunrise_mins,
          colorVar: 'var(--color-circadian)',
          textClass: 'text-circadian',
          timeText: `${formatMins(z3End)} – ${solar.sunrise}`
        }
      ];

      return raw.map((item) => {
        const getElapsed = (m: number) =>
          m >= solar.sunset_mins ? m - solar.sunset_mins : 1440 - solar.sunset_mins + m;
        const tStart = Math.max(0, Math.min(1, getElapsed(item.startMins) / nightDuration));
        const tEnd = Math.max(0, Math.min(1, getElapsed(item.endMins) / nightDuration));
        const pathData = getSubBezierPath(ARC_P0, ARC_P1, ARC_P2, tStart, tEnd);
        const tCenter = (tStart + tEnd) / 2;
        const centerPercent = 5 + tCenter * 90;

        let isActive = false;
        if (item.startMins <= item.endMins) {
          isActive = currentMins >= item.startMins && currentMins < item.endMins;
        } else {
          isActive = currentMins >= item.startMins || currentMins < item.endMins;
        }

        return {
          ...item,
          tStart,
          tEnd,
          pathData,
          centerPercent,
          isActive
        } satisfies ArcSegment;
      });
    }
  });

  let alignmentScore = 94;
  let showWindows = $state(false);
</script>

<div
  class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-card transition-all"
>
  <!-- Header with Alignment Score, Phase & Expandable Windows Toggle -->
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
        style="background-color: var({isDay
          ? '--color-circadian-soft'
          : '--color-sleep-soft'}); color: var({isDay ? '--color-circadian' : '--color-sleep'});"
      >
        <Icon name={isDay ? 'wb-sunny' : 'bedtime'} size="md" />
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h3 class="text-sm font-extrabold tracking-tight text-text-main">
            {isDay ? 'Zirkadianer 24h-Sonnenbogen' : 'Zirkadianer Nacht- & Regenerationsbogen'}
          </h3>
          <Badge
            variant="success"
            class="!bg-emerald-500/10 text-[0.625rem] font-bold !text-emerald-500"
          >
            {alignmentScore}% Alignment
          </Badge>
        </div>
        <p class="mt-0.5 text-xs text-text-muted">
          {#if isDay}
            Sonnenaufgang {solar.sunrise} &bull; Sonnenuntergang {solar.sunset}
          {:else}
            Sonnenuntergang {solar.sunset} &bull; Sonnenaufgang {solar.sunrise}
          {/if}
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Badge variant={isDay ? 'circadian' : 'sleep'} class="text-[0.625rem] font-bold">
        {activePhase}
      </Badge>
      <button
        type="button"
        onclick={() => (showWindows = !showWindows)}
        class="ml-1 flex cursor-pointer items-center gap-1 text-xs font-bold text-primary hover:underline"
      >
        <span>{showWindows ? 'Schließen' : 'Physiologische Zeitfenster'}</span>
        <Icon
          name="expand-more"
          size={14}
          class="transition-transform {showWindows ? 'rotate-180' : ''}"
        />
      </button>
    </div>
  </div>

  <!-- Collapsible Physiological Time Windows (Rich Science Cards) -->
  {#if showWindows}
    <div
      class="grid animate-[fadeIn_0.15s_ease-out] grid-cols-1 gap-2.5 rounded-2xl border border-border-subtle bg-surface-50 p-3 text-xs sm:grid-cols-2 md:grid-cols-4"
    >
      {#if isDay}
        <!-- 1. Morgenlicht -->
        <div class="space-y-1 rounded-xl border border-border-subtle bg-surface-0 p-2.5">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5 font-bold text-text-main">
              <Icon name="wb-sunny" size="sm" class="text-circadian" /> Morgenlicht
            </span>
            <span class="font-bold text-circadian">{solar.sunrise} – 08:30</span>
          </div>
          <p class="text-[0.6875rem] leading-tight text-text-muted">
            10.000+ Lux Tageslicht unterdrückt Rest-Melatonin und startet den 14h-Wach-Timer.
          </p>
        </div>

        <!-- 2. Essensfenster -->
        <div class="space-y-1 rounded-xl border border-border-subtle bg-surface-0 p-2.5">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5 font-bold text-text-main">
              <Icon name="restaurant" size="sm" class="text-primary" /> Essensfenster
            </span>
            <span class="font-bold text-primary">08:00 – 18:30</span>
          </div>
          <p class="text-[0.6875rem] leading-tight text-text-muted">
            Ende 4h vor Schlaf schont die zelluläre Autophagie und Schlafarchitektur.
          </p>
        </div>

        <!-- 3. Koffein-Cutoff -->
        <div class="space-y-1 rounded-xl border border-border-subtle bg-surface-0 p-2.5">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5 font-bold text-text-main">
              <Icon name="coffee" size="sm" class="text-activity" /> Koffein-Cutoff
            </span>
            <span class="font-bold text-activity">14:30</span>
          </div>
          <p class="text-[0.6875rem] leading-tight text-text-muted">
            5.5h Halbwertszeit zur Vermeidung von Adenosin-Rezeptor Blockaden im Tiefschlaf.
          </p>
        </div>

        <!-- 4. Melatonin-Onset -->
        <div class="space-y-1 rounded-xl border border-border-subtle bg-surface-0 p-2.5">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5 font-bold text-text-main">
              <Icon name="bedtime" size="sm" class="text-vital" /> Melatonin Onset
            </span>
            <span class="font-bold text-vital">{solar.sunset}</span>
          </div>
          <p class="text-[0.6875rem] leading-tight text-text-muted">
            Natürlicher Peak nach Sonnenuntergang. Blaulichtfilter ab 21:00 empfohlen.
          </p>
        </div>
      {:else}
        <!-- 1. Blaulicht-Filter -->
        <div class="space-y-1 rounded-xl border border-border-subtle bg-surface-0 p-2.5">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5 font-bold text-text-main">
              <Icon name="nightlight" size="sm" class="text-sleep" /> Blaulichtfilter
            </span>
            <span class="font-bold text-sleep">{solar.sunset} – 22:00</span>
          </div>
          <p class="text-[0.6875rem] leading-tight text-text-muted">
            Bildschirme dimmen und warmes Licht nutzen, um Melatonin nicht zu unterdrücken.
          </p>
        </div>

        <!-- 2. Einschlaffenster -->
        <div class="space-y-1 rounded-xl border border-border-subtle bg-surface-0 p-2.5">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5 font-bold text-text-main">
              <Icon name="bedtime" size="sm" class="text-primary" /> Einschlaffenster
            </span>
            <span class="font-bold text-primary">22:00 – 23:30</span>
          </div>
          <p class="text-[0.6875rem] leading-tight text-text-muted">
            Optimale Phase zum Einschlafen bei sinkender Körperkerntemperatur.
          </p>
        </div>

        <!-- 3. Tiefschlaf & Nadir -->
        <div class="space-y-1 rounded-xl border border-border-subtle bg-surface-0 p-2.5">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5 font-bold text-text-main">
              <Icon name="dark_mode" size="sm" class="text-fasting" /> Tiefschlaf (Nadir)
            </span>
            <span class="font-bold text-fasting">02:00 – 04:30</span>
          </div>
          <p class="text-[0.6875rem] leading-tight text-text-muted">
            Körperliches Temperaturminimum und zelluläre Regeneration im Tiefschlaf.
          </p>
        </div>

        <!-- 4. Aufwachfenster -->
        <div class="space-y-1 rounded-xl border border-border-subtle bg-surface-0 p-2.5">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5 font-bold text-text-main">
              <Icon name="wb-sunny" size="sm" class="text-circadian" /> Aufwachfenster
            </span>
            <span class="font-bold text-circadian">{solar.sunrise}</span>
          </div>
          <p class="text-[0.6875rem] leading-tight text-text-muted">
            Cortisol steigt an und bereitet den Körper auf natürliches Erwachen vor.
          </p>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Responsive Arc Stage (Segmented Arc with Direct Phase Mapping) -->
  <div class="relative w-full pt-1 pb-1 select-none">
    <!-- SVG Canvas with Segmented Arc Curves -->
    <div class="relative h-[95px] w-full sm:h-[110px]">
      <svg class="h-full w-full overflow-visible" viewBox="0 0 1000 100" preserveAspectRatio="none">
        <defs>
          <!-- Subtle Base Fill Gradient -->
          <linearGradient id="arcBaseFill" x1="0" y1="0" x2="0" y2="1">
            <stop
              offset="0%"
              stop-color={isDay ? 'var(--color-circadian)' : 'var(--color-sleep)'}
              stop-opacity="0.12"
            />
            <stop
              offset="100%"
              stop-color={isDay ? 'var(--color-circadian)' : 'var(--color-sleep)'}
              stop-opacity="0"
            />
          </linearGradient>
        </defs>

        <!-- Horizon Baseline (0 Altitude) -->
        <line
          x1="25"
          y1="85"
          x2="975"
          y2="85"
          stroke="var(--border-subtle)"
          stroke-width="1.5"
          stroke-dasharray="6 6"
        />

        <!-- Subtle Ambient Fill under Full Arc -->
        <path d="M 50 85 Q 500 0 950 85 Z" fill="url(#arcBaseFill)" />

        <!-- Base Arc Guide Track (Subtle Neutral) -->
        <path
          d="M 50 85 Q 500 0 950 85"
          fill="none"
          stroke="var(--border-strong)"
          stroke-width="2"
          stroke-linecap="round"
          opacity="0.25"
        />

        <!-- INDIVIDUAL COLORED ARC SEGMENTS -->
        {#each segments as seg (seg.id)}
          <!-- Segment Active Glow Aura -->
          {#if seg.isActive}
            <path
              d={seg.pathData}
              fill="none"
              stroke={seg.colorVar}
              stroke-width="10"
              stroke-linecap="round"
              opacity="0.3"
            />
          {/if}

          <!-- Solid Segment Stroke -->
          <path
            d={seg.pathData}
            fill="none"
            stroke={seg.colorVar}
            stroke-width={seg.isActive ? '4.5' : '3.5'}
            stroke-linecap="round"
            class="transition-all duration-300"
          />
        {/each}
      </svg>

      <!-- PERFECT CIRCULAR SUN/MOON NODE (Travels Along the Segmented Arc) -->
      <div
        class="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-1/2 transition-all duration-500"
        style="left: {sunPositionPercent}%; top: {sunHeightPercent}%;"
      >
        <div class="relative flex items-center justify-center">
          {#if isDay}
            <div class="absolute h-10 w-10 animate-ping rounded-full bg-circadian opacity-25"></div>
            <div class="h-7 w-7 rounded-full bg-circadian opacity-35 blur-xs"></div>
            <div
              class="absolute h-3.5 w-3.5 rounded-full border-2 border-circadian bg-white shadow-sm"
            ></div>
          {:else}
            <div class="absolute h-10 w-10 animate-ping rounded-full bg-sleep opacity-25"></div>
            <div class="h-7 w-7 rounded-full bg-sleep opacity-35 blur-xs"></div>
            <div
              class="absolute h-3.5 w-3.5 rounded-full border-2 border-sleep bg-white shadow-sm"
            ></div>
          {/if}
        </div>
      </div>
    </div>

    <!-- DIRECT PHASE SEGMENT LABELS (Centered Under Each Arc Segment) -->
    <div class="relative mt-2 h-8 w-full">
      {#each segments as seg (seg.id)}
        <div
          class="absolute top-0 flex -translate-x-1/2 flex-col items-center text-center"
          style="left: {seg.centerPercent}%;"
        >
          <!-- Phase Name -->
          <div class="text-[0.6875rem] leading-tight font-bold whitespace-nowrap {seg.textClass}">
            <span class="hidden sm:inline">{seg.name}</span>
            <span class="sm:hidden">{seg.shortName}</span>
          </div>

          <!-- Phase Time Range -->
          <div class="text-[0.625rem] leading-tight font-medium whitespace-nowrap text-text-muted">
            {seg.timeText}
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>
