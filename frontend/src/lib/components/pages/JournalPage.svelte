<script lang="ts">
  import Badge from '../ui/Badge.svelte';
  import MoodValenceSphere from '../today/MoodValenceSphere.svelte';
  import JournalEditor from '../journal/JournalEditor.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  const journalQuery = useQuery(async () => {
    const entries = await db.journal_entry.toArray();
    return entries
      .filter((e) => !e.deleted_at)
      .sort(
        (a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime()
      )
      .map((e) => {
        const d = new Date(e.created_at || e.entry_date || '');
        const wordCount = e.content.trim() ? e.content.trim().split(/\s+/).length : 0;
        return {
          id: e.id,
          date: d.toLocaleDateString('de-DE', { day: '2-digit', month: 'short', year: 'numeric' }),
          title: e.title || 'Tagebuch-Eintrag',
          preview: e.content.substring(0, 140) + (e.content.length > 140 ? '...' : ''),
          words: wordCount
        };
      });
  });

  const pastEntries = $derived(journalQuery.value ?? []);
  const loading = $derived(journalQuery.loading);
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Journal & Psychobiometrische Reflexion</h1>
      <p class="mt-0.5 text-sm text-text-muted">
        Ablenkungsfreier Zen-Modus mit integrierter Stimmungs- und Biometrie-Verknüpfung
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Ende-zu-Ende Verschlüsselt</Badge>
    </div>
  </div>

  <div class="grid grid-cols-1 gap-5 lg:grid-cols-12">
    <!-- Editor & Daily Check-in (8-Col) -->
    <div class="space-y-4 lg:col-span-8">
      <JournalEditor />
      <MoodValenceSphere />
    </div>

    <!-- Timeline History & Mood Trends (4-Col) -->
    <div class="space-y-4 lg:col-span-4">
      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card">
        <div class="mb-3 flex items-center justify-between">
          <span class="text-sm font-bold text-text-main">Vergangene Einträge</span>
          {#if pastEntries.length > 0}
            <span class="font-mono text-xs text-text-muted">{pastEntries.length} Einträge</span>
          {/if}
        </div>

        {#if loading}
          <div class="py-8 text-center text-xs text-text-muted">Einträge werden geladen...</div>
        {:else if pastEntries.length === 0}
          <div class="py-8 text-center text-xs text-text-muted">
            Noch keine Tagebuch-Einträge vorhanden. Nutze den Editor links, um deine Gedanken
            festzuhalten.
          </div>
        {:else}
          <div class="space-y-3">
            {#each pastEntries as entry (entry.id)}
              <div
                class="cursor-pointer rounded-xl border border-border-subtle bg-surface-50 p-3 transition-colors hover:bg-surface-100"
              >
                <div class="mb-1 flex items-center justify-between">
                  <span class="text-xs font-bold text-text-main">{entry.title}</span>
                  <span class="font-mono text-[0.6875rem] text-text-soft">{entry.date}</span>
                </div>
                <p class="line-clamp-2 text-[0.6875rem] leading-relaxed text-text-muted">
                  {entry.preview}
                </p>
                <div
                  class="mt-2 flex items-center justify-between border-t border-border-subtle pt-1.5 text-[0.6875rem] text-text-soft"
                >
                  <Badge variant="default" class="text-[0.625rem]">Tagebuch</Badge>
                  <span class="font-mono">{entry.words} Wörter</span>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
