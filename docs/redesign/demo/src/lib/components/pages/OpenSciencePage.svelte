<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  interface ResearchStudy {
    id: string;
    title: string;
    institution: string;
    participants: number;
    optedIn: boolean;
    description: string;
    sharedMetrics: string[];
    privacyGuarantee: string;
  }

  let studies = $state<ResearchStudy[]>([
    {
      id: 'rs-1',
      title: 'EAS Langlebigkeits- und Lipidstudie 2026',
      institution: 'European Atherosclerosis Society / Charité Berlin',
      participants: 4820,
      optedIn: true,
      description: 'Erforschung von ApoB- und LDL-Trajektorien unter intermittierendem Fasten und Zone-2 Training.',
      sharedMetrics: ['ApoB', 'LDL-C', 'HDL-C', 'Triglyzeride', 'Ruhepuls'],
      privacyGuarantee: 'ε = 0.3 (Strenges Rausch-Modell)'
    },
    {
      id: 'rs-2',
      title: 'Zirkadiane Schlafarchitektur und HRV',
      institution: 'Stanford Center for Sleep Sciences',
      participants: 12450,
      optedIn: true,
      description: 'Analyse des Einflusses von Mahlzeiten-Timing auf N3-Tiefschlafphasen und nächtliche Herzratenvariabilität.',
      sharedMetrics: ['Schlafdauer', 'Tiefschlaf (N3)', 'HRV (rMSSD)', 'Fastenfenster'],
      privacyGuarantee: 'ε = 0.5, k ≥ 100'
    },
    {
      id: 'rs-3',
      title: 'Progressive Überlastung und Skelettmuskel-Erhaltung',
      institution: 'Institut für Sportwissenschaften Köln',
      participants: 3180,
      optedIn: false,
      description: 'Längsschnitt-Modellierung von 1RM-Kurven und Regenerationszeiten bei trainingserfahrenen Erwachsenen.',
      sharedMetrics: ['1RM Bankdrücken', '1RM Kniebeugen', 'Wochen-Tonnage'],
      privacyGuarantee: 'k ≥ 50'
    }
  ]);

  let isGenerating = $state(false);

  function generateSyntheticData() {
    isGenerating = true;
    setTimeout(() => {
      isGenerating = false;
      alert('Synthetischer, mathematisch anonymisierter Datensatz erfolgreich generiert (Differential Privacy ε=0.5). Download bereit.');
    }, 1500);
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Open Science und Dezentrale Forschung</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Freiwillige Bereitstellung mathematisch anonymisierter Längsschnittdaten für evidenzbasierte Langlebigkeits-Studien
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="primary" class="font-mono text-xs">Differential Privacy: Aktiv (ε = 0.5)</Badge>
    </div>
  </div>

  <!-- Privacy Guarantee Card -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-6 shadow-[var(--shadow-card)] flex items-start gap-5">
    <div class="w-12 h-12 rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center text-xl shrink-0">
      <Icon name="labs" size={24} />
    </div>
    <div class="space-y-2 flex-1">
      <h2 class="text-base font-extrabold text-[var(--text-main)]">Kryptographischer Datenschutz nach akademischen Standards</h2>
      <p class="text-xs text-[var(--text-muted)] leading-relaxed">
        Alle Forschungsbeiträge werden vor der Übertragung lokal auf deinem Gerät mit mathematischem Laplace-Rauschen versetzt (<span class="font-mono text-[var(--color-primary)]">ε-Differential Privacy</span>). 
        Es ist mathematisch unmöglich, individuelle Messwerte oder Identitäten aus den aggregierten Studiendaten zu rekonstruieren.
      </p>
      <div class="flex items-center gap-4 pt-1 text-xs font-mono text-[var(--text-soft)]">
        <span>• Lokales Rauschen: Laplace(0, Δf/ε)</span>
        <span>• k-Anonymität: k ≥ 50</span>
        <span>• Zero Server Knowledge</span>
      </div>
    </div>
    <Btn variant="secondary" size="sm" onclick={generateSyntheticData} disabled={isGenerating}>
      {isGenerating ? 'Generiere...' : 'Synthetischen Datensatz exportieren'}
    </Btn>
  </div>

  <!-- Active Studies Grid -->
  <div class="space-y-4">
    <h3 class="text-sm font-bold text-[var(--text-main)]">Verifizierte Wissenschaftliche Studien</h3>
    
    <div class="grid grid-cols-1 gap-4">
      {#each studies as s}
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all hover:border-[var(--color-primary)]">
          <div class="space-y-2 max-w-2xl">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-sm font-extrabold text-[var(--text-main)]">{s.title}</span>
              <Badge variant={s.optedIn ? 'success' : 'default'}>{s.optedIn ? 'Teilnahme Aktiv' : 'Inaktiv'}</Badge>
              <span class="text-xs font-mono text-[var(--text-soft)]">• {s.participants.toLocaleString('de-DE')} Teilnehmer</span>
            </div>
            
            <p class="text-xs text-[var(--text-muted)]">{s.description}</p>
            
            <div class="flex items-center gap-2 flex-wrap text-xs text-[var(--text-soft)]">
              <span class="font-semibold text-[var(--text-main)]">Institut:</span> {s.institution}
              <span>•</span>
              <span class="font-semibold text-[var(--text-main)]">Garantie:</span> <span class="font-mono text-[var(--color-primary)]">{s.privacyGuarantee}</span>
            </div>

            <div class="flex items-center gap-1.5 flex-wrap pt-1">
              <span class="text-[0.6875rem] font-semibold text-[var(--text-soft)]">Freigegebene Parameter:</span>
              {#each s.sharedMetrics as m}
                <span class="px-2 py-0.5 rounded-md bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[0.625rem] font-mono text-[var(--text-muted)]">{m}</span>
              {/each}
            </div>
          </div>

          <div class="flex items-center gap-3 shrink-0">
            <button
              type="button"
              aria-label="Teilnahme an Studie umschalten"
              onclick={() => s.optedIn = !s.optedIn}
              class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none {s.optedIn ? 'bg-[var(--color-primary)]' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)]'}"
            >
              <span class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out {s.optedIn ? 'translate-x-5' : 'translate-x-0'}"></span>
            </button>
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>
