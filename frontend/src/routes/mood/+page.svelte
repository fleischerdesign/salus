<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { MoodEntry } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import MoodPicker from '$components/mood/MoodPicker.svelte';
  import MoodCalendar from '$components/mood/MoodCalendar.svelte';
  import { createMoodEntry } from '$lib/mutations/wellness';

  let loading = $state(true);
  let entries = $state<MoodEntry[]>([]);
  let saving = $state(false);

  let todayStr = new Date().toISOString().split('T')[0];
  let todayEntry = $derived(entries.find((e) => e.entry_date === todayStr));
  let score = $state(todayEntry?.mood_score ?? 0);

  $effect(() => {
    const sub = liveQuery(() => db.mood_entry.toArray()).subscribe((v) => {
      entries = v;
      const te = v.find((e) => e.entry_date === todayStr);
      score = te?.mood_score ?? 0;
      loading = false;
    });
    return () => sub.unsubscribe();
  });

  async function handleSelect(newScore: number) {
    score = newScore;
    saving = true;
    try {
      await createMoodEntry({ mood_score: newScore });
    } finally {
      saving = false;
    }
  }
</script>

<svelte:head><title>Salus — Mood</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Mood"
    subtitle="Log how you're feeling each day"
    icon="sentiment-satisfied"
    iconColor="#f59e0b"
  />

  {#if loading}
    <div class="h-32 animate-pulse rounded-xl bg-surface-100"></div>
  {:else}
    <div class="rounded-xl border border-surface-200 bg-surface-0 p-6">
      <h3 class="mb-3 text-sm font-semibold text-surface-700">How are you today?</h3>
      <MoodPicker {score} onSelect={handleSelect} />
      {#if saving}
        <p class="mt-2 text-xs text-surface-400">Saving...</p>
      {/if}
    </div>

    <div class="rounded-xl border border-surface-200 bg-surface-0 p-6">
      <MoodCalendar {entries} onSelectDate={(d) => {}} />
    </div>
  {/if}
</div>
