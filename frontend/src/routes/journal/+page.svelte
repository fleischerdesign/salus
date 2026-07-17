<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import type { JournalEntry } from '$lib/db/types';
  import { createJournalEntry } from '$lib/mutations/wellness';

  let loading = $state(true);
  let entries = $state<JournalEntry[]>([]);
  let title = $state('');
  let content = $state('');
  let saving = $state(false);

  $effect(() => {
    const sub = liveQuery(() =>
      db.journal_entry.orderBy('entry_date').reverse().toArray()
    ).subscribe({
      next: (v) => {
        entries = v;
        loading = false;
      },
      error: () => {
        loading = false;
      }
    });
    return () => sub.unsubscribe();
  });

  async function handleSubmit() {
    if (!content.trim()) return;
    saving = true;
    try {
      await createJournalEntry({ title: title.trim() || undefined, content: content.trim() });
      title = '';
      content = '';
    } finally {
      saving = false;
    }
  }
</script>

<svelte:head><title>Salus — Journal</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Journal"
    subtitle="Capture your thoughts and reflections"
    icon="edit-note"
    iconColor="#8b5cf6"
  />

  <Card>
    <form
      onsubmit={(e) => {
        e.preventDefault();
        handleSubmit();
      }}
      class="space-y-4"
    >
      <FormField label="Title (optional)">
        <Input name="title" bind:value={title} placeholder="Today's reflection" />
      </FormField>
      <FormField label="Entry" required>
        <textarea
          name="content"
          bind:value={content}
          rows={5}
          class="w-full resize-y rounded-lg border border-surface-200 bg-surface-0 px-3 py-2 text-sm text-surface-900 placeholder-surface-400"
          placeholder="What's on your mind?"
        ></textarea>
      </FormField>
      <div class="flex justify-end">
        <Btn variant="primary" loading={saving} onclick={handleSubmit}>Save Entry</Btn>
      </div>
    </form>
  </Card>

  {#if loading}
    <div class="space-y-3">
      {#each Array(3) as _}
        <div class="h-20 animate-pulse rounded-xl bg-surface-100"></div>
      {/each}
    </div>
  {:else if entries.length > 0}
    <div class="space-y-3">
      {#each entries.slice(0, 20) as entry (entry.id)}
        <Card padding={false}>
          <div class="p-4">
            {#if entry.title}
              <h3 class="font-semibold text-surface-900">{entry.title}</h3>
            {/if}
            <p class="mt-1 text-sm whitespace-pre-line text-surface-600">{entry.content}</p>
            <div class="mt-2 flex items-center gap-2">
              <span class="text-[11px] text-surface-400">{entry.entry_date}</span>
              {#if entry.mood_score != null}
                <Icon
                  name={['', 'mood-bad', 'sentiment-dissatisfied', 'sentiment-dissatisfied',
                    'sentiment-neutral', 'sentiment-neutral', 'sentiment-satisfied', 'sentiment-satisfied',
                    'sentiment-very-satisfied', 'sentiment-very-satisfied', 'celebration'][entry.mood_score]}
                  size="lg"
                />
              {/if}
            </div>
          </div>
        </Card>
      {/each}
    </div>
  {:else}
    <Card>
      <div class="p-12 text-center text-surface-400">
        No journal entries yet. Write your first one above.
      </div>
    </Card>
  {/if}
</div>
