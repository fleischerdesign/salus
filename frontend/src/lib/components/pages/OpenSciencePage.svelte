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
      description:
        'Erforschung von ApoB- und LDL-Trajektorien unter intermittierendem Fasten und Zone-2 Training.',
      sharedMetrics: ['ApoB', 'LDL-C', 'HDL-C', 'Triglyzeride', 'Ruhepuls'],
      privacyGuarantee: 'ε = 0.3 (Strenges Rausch-Modell)'
    },
    {
      id: 'rs-2',
      title: 'Zirkadiane Schlafarchitektur und HRV',
      institution: 'Stanford Center for Sleep Sciences',
      participants: 12450,
      optedIn: true,
      description:
        'Analyse des Einflusses von Mahlzeiten-Timing auf N3-Tiefschlafphasen und nächtliche Herzratenvariabilität.',
      sharedMetrics: ['Schlafdauer', 'Tiefschlaf (N3)', 'HRV (rMSSD)', 'Fastenfenster'],
      privacyGuarantee: 'ε = 0.5, k ≥ 100'
    },
    {
      id: 'rs-3',
      title: 'Progressive Überlastung und Skelettmuskel-Erhaltung',
      institution: 'Institut für Sportwissenschaften Köln',
      participants: 3180,
      optedIn: false,
      description:
        'Längsschnitt-Modellierung von 1RM-Kurven und Regenerationszeiten bei trainingserfahrenen Erwachsenen.',
      sharedMetrics: ['1RM Bankdrücken', '1RM Kniebeugen', 'Wochen-Tonnage'],
      privacyGuarantee: 'k ≥ 50'
    }
  ]);

  let isGenerating = $state(false);

  function generateSyntheticData() {
    isGenerating = true;
    setTimeout(() => {
      isGenerating = false;
      alert(
        'Synthetischer, mathematisch anonymisierter Datensatz erfolgreich generiert (Differential Privacy ε=0.5). Download bereit.'
      );
    }, 1500);
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Open Science und Dezentrale Forschung</h1>
      <p class="mt-0.5 text-sm text-[var(--text-muted)]">
        Freiwillige Bereitstellung mathematisch anonymisierter Längsschnittdaten für evidenzbasierte
        Langlebigkeits-Studien
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="primary" class="font-mono text-xs"
        >Differential Privacy: Aktiv (ε = 0.5)</Badge
      >
    </div>
  </div>

  <!-- Privacy Guarantee Card -->
  <div
    class="flex items-start gap-5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-6 shadow-[var(--shadow-card)]"
  >
    <div
      class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[var(--color-primary)]/10 text-xl text-[var(--color-primary)]"
    >
      <Icon name="labs" size={24} />
    </div>
    <div class="flex-1 space-y-2">
      <h2 class="text-base font-extrabold text-[var(--text-main)]">
        Kryptographischer Datenschutz nach akademischen Standards
      </h2>
      <p class="text-xs leading-relaxed text-[var(--text-muted)]">
        Alle Forschungsbeiträge werden vor der Übertragung lokal auf deinem Gerät mit mathematischem
        Laplace-Rauschen versetzt (<span class="font-mono text-[var(--color-primary)]"
          >ε-Differential Privacy</span
        >). Es ist mathematisch unmöglich, individuelle Messwerte oder Identitäten aus den
        aggregierten Studiendaten zu rekonstruieren.
      </p>
      <div class="flex items-center gap-4 pt-1 font-mono text-xs text-[var(--text-soft)]">
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
    <h3 class="text-sm font-bold text-[var(--text-main)]">
      Verifizierte Wissenschaftliche Studien
    </h3>

    <div class="grid grid-cols-1 gap-4">
      {#each studies as s}
        <div
          class="flex flex-col justify-between gap-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)] transition-all hover:border-[var(--color-primary)] md:flex-row md:items-center"
        >
          <div class="max-w-2xl space-y-2">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-sm font-extrabold text-[var(--text-main)]">{s.title}</span>
              <Badge variant={s.optedIn ? 'success' : 'default'}
                >{s.optedIn ? 'Teilnahme Aktiv' : 'Inaktiv'}</Badge
              >
              <span class="font-mono text-xs text-[var(--text-soft)]"
                >• {s.participants.toLocaleString('de-DE')} Teilnehmer</span
              >
            </div>

            <p class="text-xs text-[var(--text-muted)]">{s.description}</p>

            <div class="flex flex-wrap items-center gap-2 text-xs text-[var(--text-soft)]">
              <span class="font-semibold text-[var(--text-main)]">Institut:</span>
              {s.institution}
              <span>•</span>
              <span class="font-semibold text-[var(--text-main)]">Garantie:</span>
              <span class="font-mono text-[var(--color-primary)]">{s.privacyGuarantee}</span>
            </div>

            <div class="flex flex-wrap items-center gap-1.5 pt-1">
              <span class="text-[0.6875rem] font-semibold text-[var(--text-soft)]"
                >Freigegebene Parameter:</span
              >
              {#each s.sharedMetrics as m}
                <span
                  class="rounded-md border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2 py-0.5 font-mono text-[0.625rem] text-[var(--text-muted)]"
                  >{m}</span
                >
              {/each}
            </div>
          </div>

          <div class="flex shrink-0 items-center gap-3">
            <button
              type="button"
              aria-label="Teilnahme an Studie umschalten"
              onclick={() => (s.optedIn = !s.optedIn)}
              class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none {s.optedIn
                ? 'bg-[var(--color-primary)]'
                : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)]'}"
            >
              <span
                class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out {s.optedIn
                  ? 'translate-x-5'
                  : 'translate-x-0'}"
              ></span>
            </button>
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>
