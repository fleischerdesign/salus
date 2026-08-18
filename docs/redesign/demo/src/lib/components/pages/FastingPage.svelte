<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let isFastingActive = $state(true);
  let elapsedHours = $state(15.75); // 15h 45m
  let targetHours = $state(16);
  let protocol = $state('16:8 Intervallfasten');

  const metabolicStages = [
    { title: 'Blutzucker & Insulin sinken', range: '0 – 4 Std', desc: 'Nahrungsaufnahme wird verarbeitet, Insulin fällt ab.', active: true, passed: true },
    { title: 'Glykogen-Entleerung & Fettverbrennung', range: '4 – 12 Std', desc: 'Leberglykogen wird aufgebraucht, Glukagon steigt an.', active: true, passed: true },
    { title: 'Metabolische Ketose (Ketonkörper)', range: '12 – 18 Std', desc: 'Leber synthetisiert Beta-Hydroxybutyrat zur neuronalen Energieversorgung.', active: true, passed: false },
    { title: 'Autophagie (Zellreinigung)', range: '18 – 24 Std', desc: 'Geschädigte Zellorganellen und fehlgefaltete Proteine werden recycelt.', active: false, passed: false },
    { title: 'Tiefe Autophagie & Stammzell-Reset', range: '24+ Std', desc: 'Immunzellregeneration und Seneszenz-Abbau.', active: false, passed: false }
  ];

  const fastingHistory = [
    { date: 'Gestern (13.08.)', duration: '16h 30m', target: '16h', type: '16:8', success: true, autophagyHours: '0.5h' },
    { date: '12. August', duration: '18h 15m', target: '16h', type: '16:8', success: true, autophagyHours: '2.25h' },
    { date: '11. August', duration: '15h 45m', target: '16h', type: '16:8', success: true, autophagyHours: '0h' },
    { date: '10. August', duration: '20h 00m', target: '20:4', type: 'Warrior Fast', success: true, autophagyHours: '4.0h' }
  ];

  let progressPercent = $derived(Math.min(100, Math.round((elapsedHours / targetHours) * 100)));
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Intervallfasten & Autophagie-Zentrale</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Protokolle, zelluläre Stoffwechselphasen & mitochondriale Regeneration
      </p>
    </div>
    <div class="flex items-center gap-2">
      {#if isFastingActive}
        <Btn variant="primary" size="sm" onclick={() => { isFastingActive = false; alert('Fastenfenster erfolgreich beendet!'); }}>
          Fasten beenden
        </Btn>
      {:else}
        <Btn variant="primary" size="sm" onclick={() => { isFastingActive = true; alert('Neues Fastenfenster gestartet!'); }}>
          Fasten starten
        </Btn>
      {/if}
    </div>
  </div>

  <!-- Active Fasting Hero Card -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
    
    <!-- Left: Clock & Timer (6-Col) -->
    <div class="lg:col-span-6 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-6 shadow-[var(--shadow-card)] flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <span class="text-sm font-bold text-[var(--text-main)]">Aktives Fastenfenster</span>
            <Badge variant="success">Ketose aktiv</Badge>
          </div>
          <span class="text-xs font-mono text-[var(--text-muted)]">{protocol}</span>
        </div>

        <!-- Visual Ring / Metric Counter -->
        <div class="flex items-center gap-6 my-6">
          <div class="relative w-32 h-32 flex items-center justify-center shrink-0">
            <svg class="w-full h-full -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" fill="none" stroke="var(--bg-surface-50)" stroke-width="8" />
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
              <span class="text-xs text-[var(--text-soft)] font-mono">Fortschritt</span>
              <span class="text-lg font-mono font-extrabold text-[var(--color-primary)]">{progressPercent}%</span>
            </div>
          </div>

          <div>
            <span class="text-xs text-[var(--text-muted)] uppercase font-mono block">Vergangene Zeit:</span>
            <span class="text-3xl font-extrabold font-mono text-[var(--text-main)]">15h 45m</span>
            <p class="text-xs text-[var(--text-soft)] mt-1 font-mono">Ziel: {targetHours}h (noch 15 Minuten)</p>
          </div>
        </div>
      </div>

      <!-- Quick Fasting Actions -->
      <div class="pt-4 border-t border-[var(--border-subtle)] flex items-center justify-between text-xs">
        <span class="text-[var(--text-soft)]">Gestartet: Gestern 21:00 Uhr</span>
        <button type="button" class="text-[var(--color-primary)] font-semibold hover:underline cursor-pointer" onclick={() => alert('Fastenzeit anpassen')}>
          Ziel anpassen (18h / 20h) &rarr;
        </button>
      </div>
    </div>

    <!-- Right: Metabolic Stages Timeline (6-Col) -->
    <div class="lg:col-span-6 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-6 shadow-[var(--shadow-card)]">
      <h2 class="text-sm font-bold text-[var(--text-main)] mb-3">Zelluläre Stoffwechselphasen</h2>
      <div class="space-y-3">
        {#each metabolicStages as stage}
          <div class="p-3 rounded-xl border transition-all {stage.active && !stage.passed ? 'bg-[var(--color-primary-soft)]/20 border-[var(--color-primary)] ring-1 ring-[var(--color-primary)]/30' : stage.passed ? 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] opacity-85' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] opacity-50'}">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-bold text-[var(--text-main)] flex items-center gap-1.5">
                {#if stage.passed}
                  <span class="text-[var(--color-success)] text-xs"></span>
                {:else if stage.active}
                  <span class="w-2 h-2 rounded-full bg-[var(--color-primary)] animate-pulse"></span>
                {/if}
                <span>{stage.title}</span>
              </span>
              <Badge variant={stage.active && !stage.passed ? 'primary' : 'default'} class="text-[0.625rem] font-mono">{stage.range}</Badge>
            </div>
            <p class="text-[0.6875rem] text-[var(--text-muted)] leading-relaxed">{stage.desc}</p>
          </div>
        {/each}
      </div>
    </div>

  </div>

  <!-- Fasting History -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-base font-extrabold text-[var(--text-main)]">Fasten-Historie & Autophagie-Ausbeute</h2>
      <Badge variant="success">Ø 16.5h Konsistenz</Badge>
    </div>
    <div class="w-full overflow-x-auto">
      <table class="w-full text-left text-xs border-collapse">
        <thead>
          <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.6875rem]">
            <th class="py-2.5 px-3">Datum</th>
            <th class="py-2.5 px-3">Dauer</th>
            <th class="py-2.5 px-3">Protokoll</th>
            <th class="py-2.5 px-3">Autophagie-Zeit</th>
            <th class="py-2.5 px-3 text-right">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)] font-mono">
          {#each fastingHistory as h}
            <tr>
              <td class="py-3 px-3 font-sans font-semibold text-[var(--text-main)]">{h.date}</td>
              <td class="py-3 px-3 font-bold text-[var(--color-primary)]">{h.duration}</td>
              <td class="py-3 px-3 font-sans text-[var(--text-muted)]">{h.type}</td>
              <td class="py-3 px-3 text-[var(--color-success)] font-bold">{h.autophagyHours}</td>
              <td class="py-3 px-3 text-right font-sans">
                <Badge variant="success">Erreicht</Badge>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>
