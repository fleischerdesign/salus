<script lang="ts">
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { startFastingSession, endFastingSession } from '$lib/mutations/fasting';

  // 1. Reactive Dexie Query (Local-First)
  const sessionsQuery = useQuery(() => db.fasting_session.toArray());
  const allSessions = $derived(sessionsQuery.value ?? []);

  // 2. Active Session Resolution
  const activeSession = $derived(allSessions.find((s) => !s.ended_at && !s.deleted_at) ?? null);

  let currentTime = $state(Date.now());

  $effect(() => {
    const timer = setInterval(() => {
      currentTime = Date.now();
    }, 30000);
    return () => clearInterval(timer);
  });

  let isFastingActive = $derived(Boolean(activeSession));
  let targetHours = $derived(activeSession?.target_hours ?? 16);
  let protocol = $derived(
    activeSession?.fasting_type === 'intermittent'
      ? '16:8 Intervallfasten'
      : (activeSession?.fasting_type ?? '16:8 Intervallfasten')
  );

  let elapsedMinutes = $derived.by(() => {
    if (!activeSession) return 0;
    const start = new Date(activeSession.started_at).getTime();
    return Math.max(0, Math.floor((currentTime - start) / (1000 * 60)));
  });

  let elapsedHours = $derived(elapsedMinutes / 60);

  let elapsedDisplay = $derived.by(() => {
    if (!isFastingActive) return '0h 00m';
    const h = Math.floor(elapsedMinutes / 60);
    const m = elapsedMinutes % 60;
    return `${h}h ${String(m).padStart(2, '0')}m`;
  });

  let progressPercent = $derived(
    targetHours > 0 ? Math.min(100, Math.round((elapsedHours / targetHours) * 100)) : 0
  );

  let remainingMinutes = $derived(Math.max(0, targetHours * 60 - elapsedMinutes));
  let remainingDisplay = $derived.by(() => {
    if (remainingMinutes === 0) return 'Ziel erreicht!';
    const h = Math.floor(remainingMinutes / 60);
    const m = remainingMinutes % 60;
    if (h === 0) return `noch ${m} Minuten`;
    return `noch ${h}h ${m}m`;
  });

  // Dynamic Metabolic Stages from elapsed hours
  let metabolicStages = $derived([
    {
      title: 'Blutzucker & Insulin sinken',
      range: '0 – 4 Std',
      desc: 'Nahrungsaufnahme wird verarbeitet, Insulin fällt ab.',
      active: isFastingActive && elapsedHours < 4,
      passed: isFastingActive && elapsedHours >= 4
    },
    {
      title: 'Glykogen-Entleerung & Fettverbrennung',
      range: '4 – 12 Std',
      desc: 'Leberglykogen wird aufgebraucht, Glukagon steigt an.',
      active: isFastingActive && elapsedHours >= 4 && elapsedHours < 12,
      passed: isFastingActive && elapsedHours >= 12
    },
    {
      title: 'Metabolische Ketose (Ketonkörper)',
      range: '12 – 18 Std',
      desc: 'Leber synthetisiert Beta-Hydroxybutyrat zur neuronalen Energieversorgung.',
      active: isFastingActive && elapsedHours >= 12 && elapsedHours < 18,
      passed: isFastingActive && elapsedHours >= 18
    },
    {
      title: 'Autophagie (Zellreinigung)',
      range: '18 – 24 Std',
      desc: 'Geschädigte Zellorganellen und fehlgefaltete Proteine werden recycelt.',
      active: isFastingActive && elapsedHours >= 18 && elapsedHours < 24,
      passed: isFastingActive && elapsedHours >= 24
    },
    {
      title: 'Tiefe Autophagie & Stammzell-Reset',
      range: '24+ Std',
      desc: 'Immunzellregeneration und Seneszenz-Abbau.',
      active: isFastingActive && elapsedHours >= 24,
      passed: false
    }
  ]);

  // History derived from finished sessions
  let fastingHistory = $derived(
    allSessions
      .filter((s) => s.ended_at && !s.deleted_at)
      .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
      .map((s) => {
        const start = new Date(s.started_at);
        const end = new Date(s.ended_at!);
        const durMin = Math.max(0, Math.floor((end.getTime() - start.getTime()) / (1000 * 60)));
        const durHours = durMin / 60;
        const autoHours = Math.max(0, durHours - 16);
        const success = durHours >= (s.target_hours || 16);
        return {
          id: s.id,
          date: start.toLocaleDateString('de-DE', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
          }),
          duration: `${Math.floor(durMin / 60)}h ${durMin % 60}m`,
          target: `${s.target_hours || 16}h`,
          type: s.fasting_type || '16:8',
          success,
          autophagyHours: autoHours > 0 ? `${autoHours.toFixed(1)}h` : '0h'
        };
      })
  );

  async function handleStart() {
    await startFastingSession({
      target_hours: 16,
      fasting_type: '16:8',
      water_only: true
    });
  }

  async function handleEnd() {
    if (!activeSession) return;
    await endFastingSession(activeSession.id);
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Intervallfasten & Autophagie-Zentrale</h1>
      <p class="mt-0.5 text-sm text-text-muted">
        Protokolle, zelluläre Stoffwechselphasen & mitochondriale Regeneration
      </p>
    </div>
    <div class="flex items-center gap-2">
      {#if isFastingActive}
        <Btn variant="danger" size="sm" onclick={handleEnd}>Fasten beenden</Btn>
      {:else}
        <Btn variant="primary" size="sm" onclick={handleStart}>Fasten starten (16:8)</Btn>
      {/if}
    </div>
  </div>

  <!-- Active Fasting Hero Card -->
  <div class="grid grid-cols-1 gap-5 lg:grid-cols-12">
    <!-- Left: Clock & Timer (6-Col) -->
    <div
      class="flex flex-col justify-between rounded-2xl border border-border-subtle bg-surface-0 p-6 shadow-card lg:col-span-6"
    >
      <div>
        <div class="mb-4 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-sm font-bold text-text-main">
              {isFastingActive ? 'Aktives Fastenfenster' : 'Kein aktives Fasten'}
            </span>
            {#if isFastingActive}
              <Badge variant={elapsedHours >= 12 ? 'success' : 'primary'}>
                {elapsedHours >= 18
                  ? 'Autophagie aktiv'
                  : elapsedHours >= 12
                    ? 'Ketose aktiv'
                    : 'Fasten läuft'}
              </Badge>
            {:else}
              <Badge variant="default">Bereit</Badge>
            {/if}
          </div>
          <span class="font-mono text-xs text-text-muted">{protocol}</span>
        </div>

        <!-- Visual Ring / Metric Counter -->
        <div class="my-6 flex items-center gap-6">
          <div class="relative flex h-32 w-32 shrink-0 items-center justify-center">
            <svg class="h-full w-full -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                stroke="var(--bg-surface-50)"
                stroke-width="8"
              />
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                stroke="var(--color-primary)"
                stroke-width="8"
                stroke-dasharray="263.89"
                stroke-dashoffset={263.89 - (263.89 * progressPercent) / 100}
                stroke-linecap="round"
                class="transition-all duration-700"
              />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span class="font-mono text-xs text-text-soft">Fortschritt</span>
              <span class="font-mono text-lg font-extrabold text-primary">{progressPercent}%</span>
            </div>
          </div>

          <div>
            <span class="block font-mono text-xs text-text-muted uppercase">Vergangene Zeit:</span>
            <span class="font-mono text-3xl font-extrabold text-text-main">{elapsedDisplay}</span>
            <p class="mt-1 font-mono text-xs text-text-soft">
              Ziel: {targetHours}h ({remainingDisplay})
            </p>
          </div>
        </div>
      </div>

      <!-- Quick Fasting Actions -->
      <div class="flex items-center justify-between border-t border-border-subtle pt-4 text-xs">
        <span class="text-text-soft">
          {#if activeSession}
            Gestartet: {new Date(activeSession.started_at).toLocaleTimeString('de-DE', {
              hour: '2-digit',
              minute: '2-digit'
            })} Uhr
          {:else}
            Noch kein Fasten aktiv
          {/if}
        </span>
        {#if !isFastingActive}
          <button
            type="button"
            class="cursor-pointer font-semibold text-primary hover:underline"
            onclick={handleStart}
          >
            Jetzt starten (16:8) &rarr;
          </button>
        {/if}
      </div>
    </div>

    <!-- Right: Metabolic Stages Timeline (6-Col) -->
    <div class="rounded-2xl border border-border-subtle bg-surface-0 p-6 shadow-card lg:col-span-6">
      <h2 class="mb-3 text-sm font-bold text-text-main">Zelluläre Stoffwechselphasen</h2>
      <div class="space-y-3">
        {#each metabolicStages as stage}
          <div
            class="rounded-xl border p-3 transition-all {stage.active && !stage.passed
              ? 'border-primary bg-primary-soft/20 ring-1 ring-primary/30'
              : stage.passed
                ? 'border-border-subtle bg-surface-50 opacity-85'
                : 'border-border-subtle bg-surface-50 opacity-50'}"
          >
            <div class="mb-1 flex items-center justify-between">
              <span class="flex items-center gap-1.5 text-xs font-bold text-text-main">
                {#if stage.passed}
                  <span class="text-xs font-bold text-success">✓</span>
                {:else if stage.active}
                  <span class="h-2 w-2 animate-pulse rounded-full bg-primary"></span>
                {/if}
                <span>{stage.title}</span>
              </span>
              <Badge
                variant={stage.active && !stage.passed ? 'primary' : 'default'}
                class="font-mono text-[0.625rem]">{stage.range}</Badge
              >
            </div>
            <p class="text-[0.6875rem] leading-relaxed text-text-muted">{stage.desc}</p>
          </div>
        {/each}
      </div>
    </div>
  </div>

  <!-- Fasting History -->
  <div class="rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="text-base font-extrabold text-text-main">Fasten-Historie & Autophagie-Ausbeute</h2>
      {#if fastingHistory.length > 0}
        <Badge variant="success">{fastingHistory.length} Sessions</Badge>
      {/if}
    </div>
    {#if fastingHistory.length === 0}
      <div class="py-12 text-center text-sm text-text-muted">
        Noch keine abgeschlossenen Fasten-Sessions vorhanden. Klicke oben auf "Fasten starten", um
        dein erstes Zeitfenster zu protokollieren.
      </div>
    {:else}
      <div class="w-full overflow-x-auto">
        <table class="w-full border-collapse text-left text-xs">
          <thead>
            <tr
              class="border-b border-border-subtle text-[0.6875rem] tracking-wider text-text-muted uppercase"
            >
              <th class="px-3 py-2.5">Datum</th>
              <th class="px-3 py-2.5">Dauer</th>
              <th class="px-3 py-2.5">Protokoll</th>
              <th class="px-3 py-2.5">Autophagie-Zeit</th>
              <th class="px-3 py-2.5 text-right">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border-subtle font-mono">
            {#each fastingHistory as h (h.id)}
              <tr>
                <td class="px-3 py-3 font-sans font-semibold text-text-main">{h.date}</td>
                <td class="px-3 py-3 font-bold text-primary">{h.duration}</td>
                <td class="px-3 py-3 font-sans text-text-muted">{h.type}</td>
                <td class="px-3 py-3 font-bold text-success">{h.autophagyHours}</td>
                <td class="px-3 py-3 text-right font-sans">
                  <Badge variant={h.success ? 'success' : 'default'}
                    >{h.success ? 'Erreicht' : 'Vorzeitig'}</Badge
                  >
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>
