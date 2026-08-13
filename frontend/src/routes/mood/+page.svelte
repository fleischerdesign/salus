<script lang="ts">
  import { db } from '$lib/db/database';
  import { todayString } from '$lib/utils/datetime';

  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';
  import MoodPicker from '$components/mood/MoodPicker.svelte';
  import MoodCalendar from '$components/mood/MoodCalendar.svelte';
  import { createMoodEntry } from '$lib/mutations/wellness';
  import { useQuery } from '$lib/db/use-query.svelte';

  let saving = $state(false);

  let todayStr = todayString();
  let score = $state(0);

  const entriesQuery = useQuery(() => db.mood_entry.toArray());
  const entries = $derived(entriesQuery.value);
  const loading = $derived(entriesQuery.loading);

  $effect(() => {
    const te = (entries ?? []).find((e) => e.entry_date === todayStr);
    score = te?.mood_score ?? 0;
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
  <PageHeader title="Mood" subtitle="Log how you're feeling each day" icon="sentiment-satisfied" />

  {#if loading}
    <div class="h-32 animate-pulse rounded-xl bg-surface-100"></div>
  {:else}
    <Card>
      <h3 class="mb-3 text-sm font-semibold text-surface-700">How are you today?</h3>
      <MoodPicker {score} onSelect={handleSelect} />
      {#if saving}
        <p class="mt-2 text-xs text-surface-400">Saving...</p>
      {/if}
    </Card>

    <Card>
      <MoodCalendar entries={entries ?? []} onSelectDate={() => {}} />
    </Card>
  {/if}
</div>
