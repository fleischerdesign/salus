<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  const insights = [
    {
      id: 'i1',
      category: 'Zirkadianer Rhythmus und Schlaf',
      title: 'Späte Mahlzeiten reduzieren deinen Tiefschlaf um 34%',
      desc: 'An Abenden, an denen deine letzte Mahlzeit nach 20:30 Uhr stattfand, sank dein Anteil an Tiefschlaf (N3) von durchschnittlich 1h 48m auf 1h 12m bei erhöhter nächtlicher Ruheherzfrequenz (+4.2 bpm).',
      evidence: 'p < 0.01 (14 Datenpunkte analysiert)',
      recommendation: 'Halte ein 3-stündiges Fastenfenster vor dem Zubettgehen ein (letzte Mahlzeit idealerweise vor 19:30 Uhr).',
      actionLabel: 'Essens-Erinnerung um 19:00 Uhr stellen'
    },
    {
      id: 'i2',
      category: 'Kardiovaskuläre Erholung',
      title: 'Zone-2 Kardio hebt deine nächtliche HRV um +12.4 ms',
      desc: 'Trainingseinheiten im aeroben Grundlagenbereich (Zone 2, 125–140 bpm) korrelieren stark positiv mit der Herzratenvariabilität in der darauffolgenden Nacht (r = +0.68).',
      evidence: 'Pearson r = +0.68 (Signifikant)',
      recommendation: 'Integriere 2x wöchentlich 45 Minuten Zone-2 Grundlagentraining.',
      actionLabel: 'Zone-2 Session planen'
    },
    {
      id: 'i3',
      category: 'Metabolische Autophagie',
      title: '16:8 Fasten stabilisiert deinen Nüchtern-Glukosespiegel',
      desc: 'In den letzten 30 Tagen führte deine Fastenkonsistenz zu einer Reduktion der Blutzuckerspitzen nach dem Frühstück um 18 mg/dL.',
      evidence: 'ADA / ESC Biomarker-Aligniert',
      recommendation: 'Setze das 16:8 Intervallfasten fort, um die Insulinsensitivität der Skelettmuskulatur aufrechtzuerhalten.',
      actionLabel: 'Fasten-Timer anzeigen'
    }
  ];
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Gesundheitsempfehlungen und Coaching</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Personalisierte Langlebigkeits-Erkenntnisse abgeleitet aus deinen biometrischen Korrelationen
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Modell: Biometric Engine v2.4</Badge>
    </div>
  </div>

  <!-- Insights List -->
  <div class="space-y-4">
    {#each insights as ins}
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-6 shadow-[var(--shadow-card)] space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <span class="text-xs font-mono font-bold text-[var(--color-primary)] uppercase tracking-wider">{ins.category}</span>
          <Badge variant="default" class="font-mono text-[0.625rem]">{ins.evidence}</Badge>
        </div>

        <h2 class="text-base font-extrabold text-[var(--text-main)] leading-snug">{ins.title}</h2>
        <p class="text-xs text-[var(--text-muted)] leading-relaxed">{ins.desc}</p>

        <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3.5 flex items-start gap-3 my-2">
          <div class="text-[var(--color-primary)] mt-0.5 shrink-0">
            <Icon name="sun" size={16} />
          </div>
          <div>
            <span class="text-xs font-bold text-[var(--text-main)] block mb-0.5">Handlungsempfehlung:</span>
            <p class="text-xs text-[var(--text-muted)] leading-relaxed">{ins.recommendation}</p>
          </div>
        </div>

        <div class="pt-2 flex justify-end">
          <Btn variant="primary" size="sm" onclick={() => alert(ins.actionLabel + ' aktiviert!')}>
            {ins.actionLabel} &rarr;
          </Btn>
        </div>
      </div>
    {/each}
  </div>
</div>
