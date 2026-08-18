<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let journalText = $state(
    `# Reflektierter Tag\n\nHeute war das Training (Push Day A) besonders fokussiert. Das 16:8-Intervallfasten lief mühelos und die Energie am Vormittag war spürbar hoch.\n\n### Erkenntnis:\nAusreichend Schlaf (>7.5h) macht sich sofort in der Regeneration und im niedrigeren Ruhepuls bemerkbar.`
  );

  let wordCount = $derived(journalText.trim() ? journalText.trim().split(/\s+/).length : 0);

  function insertPrompt(prompt: string) {
    journalText += `\n\n> **${prompt}**\n`;
  }
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
    <div>
      <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="sun" class="text-[var(--color-circadian)]" />
        <span>Abend-Reflexion und Tagebuch</span>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">Montag, 14. August 2026</p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">E2EE Verschlüsselt</Badge>
      <Badge variant="default">Auto-Save: Gesichert</Badge>
    </div>
  </div>

  <!-- Prompt Pills -->
  <div class="flex gap-2 mb-3 overflow-x-auto pb-1">
    <button
      type="button"
      onclick={() => insertPrompt('Was hat mir heute Energie gegeben?')}
      class="text-xs px-3 py-1.5 rounded-lg bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] hover:bg-[var(--bg-surface-100)] cursor-pointer whitespace-nowrap text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors"
    >
      + Was hat mir heute Energie gegeben?
    </button>
    <button
      type="button"
      onclick={() => insertPrompt('Worüber bin ich heute dankbar?')}
      class="text-xs px-3 py-1.5 rounded-lg bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] hover:bg-[var(--bg-surface-100)] cursor-pointer whitespace-nowrap text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors"
    >
      + Worüber bin ich dankbar?
    </button>
    <button
      type="button"
      onclick={() => insertPrompt('Welche Erkenntnis nehme ich mit?')}
      class="text-xs px-3 py-1.5 rounded-lg bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] hover:bg-[var(--bg-surface-100)] cursor-pointer whitespace-nowrap text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors"
    >
      + Erkenntnis des Tages
    </button>
  </div>

  <!-- Markdown Textarea -->
  <textarea
    bind:value={journalText}
    rows="6"
    class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3.5 text-xs text-[var(--text-main)] font-sans leading-relaxed outline-none focus:border-[var(--color-primary)] transition-colors resize-y"
    placeholder="Schreibe deine Gedanken auf..."
  ></textarea>

  <div class="flex justify-between items-center text-xs text-[var(--text-muted)] mt-2 pt-2 border-t border-[var(--border-subtle)]">
    <span class="font-mono">{wordCount} Wörter</span>
    <Btn variant="primary" size="sm" onclick={() => alert('Journal-Eintrag lokal und verschlüsselt gespeichert!')}>
      Eintrag sichern
    </Btn>
  </div>
</div>
