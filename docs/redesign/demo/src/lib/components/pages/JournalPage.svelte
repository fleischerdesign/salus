<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import MoodValenceSphere from '../today/MoodValenceSphere.svelte';
  import JournalEditor from '../journal/JournalEditor.svelte';

  const pastEntries = [
    {
      date: 'Gestern, 13. Aug',
      title: 'Erholung nach schwerem Beintraining',
      preview: 'Saunagang hat der Regeneration extrem gut getan. Ruhepuls am Abend bei 58 bpm...',
      mood: 'Entspannt & Vital',
      words: 112
    },
    {
      date: 'Samstag, 12. Aug',
      title: 'Fastenbrechen mit 18 Stunden',
      preview: 'Erstes Mal 18h gefastet. Die geistige Klarheit ab Stunde 14 war bemerkenswert...',
      mood: 'Klarer Fokus / Flow',
      words: 165
    },
    {
      date: 'Freitag, 11. Aug',
      title: 'Wochenrückblick & Kraftzuwächse',
      preview: 'Bankdrücken 1RM auf 140kg gesteigert. Ernährung war zu 95% im Zielbereich...',
      mood: 'Zufrieden & Kraftvoll',
      words: 210
    }
  ];
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Journal & Psychobiometrische Reflexion</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Ablenkungsfreier Zen-Modus mit integrierter Stimmungs- und Biometrie-Verknüpfung
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Ende-zu-Ende Verschlüsselt</Badge>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
    <!-- Editor & Daily Check-in (8-Col) -->
    <div class="lg:col-span-8 space-y-4">
      <JournalEditor />
      <MoodValenceSphere />
    </div>

    <!-- Timeline History & Mood Trends (4-Col) -->
    <div class="lg:col-span-4 space-y-4">
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-bold">Vergangene Einträge</span>
          <span class="text-xs text-[var(--text-muted)] font-mono">August 2026</span>
        </div>

        <div class="space-y-3">
          {#each pastEntries as entry}
            <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 hover:bg-[var(--bg-surface-100)] transition-colors cursor-pointer">
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs font-bold text-[var(--text-main)]">{entry.title}</span>
                <span class="text-[0.6875rem] font-mono text-[var(--text-soft)]">{entry.date}</span>
              </div>
              <p class="text-[0.6875rem] text-[var(--text-muted)] line-clamp-2 leading-relaxed">
                {entry.preview}
              </p>
              <div class="mt-2 pt-1.5 border-t border-[var(--border-subtle)] flex justify-between items-center text-[0.6875rem] text-[var(--text-soft)]">
                <Badge variant="default" class="text-[0.625rem]">{entry.mood}</Badge>
                <span class="font-mono">{entry.words} Wörter</span>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  </div>
</div>
