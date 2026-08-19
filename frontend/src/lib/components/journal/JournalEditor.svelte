<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Textarea from '../ui/Textarea.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { createJournalEntry } from '$lib/mutations/wellness';

  let journalText = $state('');
  let isSaved = $state(false);

  let wordCount = $derived(journalText.trim() ? journalText.trim().split(/\s+/).length : 0);

  function insertPrompt(prompt: string) {
    journalText += (journalText ? '\n\n' : '') + `> **${prompt}**\n`;
  }

  async function handleSave() {
    if (!journalText.trim()) return;
    await createJournalEntry({
      entry_date: todayString(),
      content: journalText.trim()
    });
    isSaved = true;
    setTimeout(() => {
      isSaved = false;
      journalText = '';
    }, 1500);
  }
</script>

<div class="rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card">
  <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
    <div>
      <div class="flex items-center gap-1.5 text-sm font-bold text-text-main">
        <Icon name="wb-sunny" class="text-circadian" />
        <span>Abend-Reflexion und Tagebuch</span>
      </div>
      <p class="mt-0.5 text-xs text-text-muted">Tagesreflexion & psychobiometrische Notizen</p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">E2EE Verschlüsselt</Badge>
      {#if isSaved}
        <Badge variant="success">Gespeichert ✓</Badge>
      {/if}
    </div>
  </div>

  <!-- Prompt Pills -->
  <div class="mb-3 flex gap-2 overflow-x-auto pb-1">
    <button
      type="button"
      onclick={() => insertPrompt('Was hat mir heute Energie gegeben?')}
      class="cursor-pointer rounded-lg border border-border-subtle bg-surface-50 px-3 py-1.5 text-xs whitespace-nowrap text-text-muted transition-colors hover:bg-surface-100 hover:text-text-main"
    >
      + Was hat mir heute Energie gegeben?
    </button>
    <button
      type="button"
      onclick={() => insertPrompt('Worüber bin ich heute dankbar?')}
      class="cursor-pointer rounded-lg border border-border-subtle bg-surface-50 px-3 py-1.5 text-xs whitespace-nowrap text-text-muted transition-colors hover:bg-surface-100 hover:text-text-main"
    >
      + Worüber bin ich dankbar?
    </button>
    <button
      type="button"
      onclick={() => insertPrompt('Welche Erkenntnis nehme ich mit?')}
      class="cursor-pointer rounded-lg border border-border-subtle bg-surface-50 px-3 py-1.5 text-xs whitespace-nowrap text-text-muted transition-colors hover:bg-surface-100 hover:text-text-main"
    >
      + Erkenntnis des Tages
    </button>
  </div>

  <!-- Markdown Textarea Component -->
  <Textarea bind:value={journalText} rows={6} placeholder="Schreibe deine Gedanken auf..." />

  <div
    class="mt-2 flex items-center justify-between border-t border-border-subtle pt-2 text-xs text-text-muted"
  >
    <span class="font-mono">{wordCount} Wörter</span>
    <Btn variant="primary" size="sm" onclick={handleSave} disabled={!journalText.trim()}>
      {isSaved ? 'Gespeichert ✓' : 'Eintrag sichern'}
    </Btn>
  </div>
</div>
