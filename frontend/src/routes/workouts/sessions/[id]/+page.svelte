<script lang="ts">
  import { liveQuery } from 'dexie';
  import { page } from '$app/state';
  import { db } from '$lib/db/database';
  import type { WorkoutSession } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Table from '$components/ui/Table.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';

  const sessionId = $derived(page.params.id as string);

  let session = liveQuery(() =>
    db.workout_session.get(sessionId!).then((s) => (s && !s.deleted_at ? s : null))
  );

  let logs = liveQuery(() =>
    db.workout_log_entry
      .toArray()
      .then((arr) => arr.filter((l) => l.session_id === sessionId! && !l.deleted_at))
  );

  let exercises = liveQuery(() =>
    db.exercise.toArray().then((arr) => {
      const map = new Map(arr.map((e) => [e.id, e]));
      return map;
    })
  );

  let groupedLogs = $derived.by(() => {
    const map = new Map<string, typeof $logs>();
    for (const log of $logs ?? []) {
      const name = $exercises?.get(log.exercise_id)?.name ?? `Exercise ${log.exercise_id}`;
      const arr = map.get(name);
      if (arr) arr.push(log);
      else map.set(name, [log]);
    }
    return map;
  });

  let totalVolume = $derived(
    ($logs ?? []).reduce((sum, log) => sum + (log.weight ?? 0) * (log.reps ?? 0), 0)
  );

  let totalSets = $derived(($logs ?? []).length);

  let avgRpe = $derived.by(() => {
    if (!$logs || $logs.length === 0) return 0;
    const rpes = $logs.map((l) => l.rpe).filter((r): r is number => r != null);
    if (rpes.length === 0) return 0;
    return rpes.reduce((s, r) => s + r, 0) / rpes.length;
  });

  let durationMin = $derived.by(() => {
    if (!$session || !$session.started_at || !$session.completed_at) return 0;
    return Math.round(
      (new Date($session.completed_at).getTime() - new Date($session.started_at).getTime()) / 60000
    );
  });

  function est1rm(weight: number, reps: number): number {
    if (reps <= 1) return weight;
    return weight / (1.0278 - 0.0278 * reps);
  }
</script>

<svelte:head><title>Salus — Session</title></svelte:head>

{#if !$session}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else if $session}
  <div class="space-y-6">
    <PageHeader
      title="Workout Session"
      subtitle={`${new Date($session.completed_at ?? $session.started_at).toLocaleDateString()} • ${durationMin} min`}
      icon="fitness-center"
      iconColor="#4f46e5"
      backUrl="/workouts/sessions"
    >
      {#snippet actions()}
        {#if $session.recovery_score}
          <Badge variant="success">
            <Icon name="bolt" size="sm" />Recovery {Math.round($session.recovery_score)}%
          </Badge>
        {/if}
      {/snippet}

      {#snippet stats()}
        <div class="flex flex-wrap items-center gap-x-8 gap-y-4 px-6 py-4">
          <Stat value={totalVolume.toFixed(0)} unit="kg" label="Total Volume" />
          <Stat value={durationMin} unit="min" label="Duration" />
          <Stat value={totalSets} label="Sets Logged" />
          <Stat value={avgRpe > 0 ? avgRpe.toFixed(1) : '—'} label="Avg. RPE" />
        </div>
      {/snippet}
    </PageHeader>

    {#if $session.notes}
      <Card>
        <p class="text-sm text-surface-600 italic">"{$session.notes}"</p>
      </Card>
    {/if}

    <div class="space-y-4">
      <h2 class="text-lg font-semibold text-surface-900">Exercise Log</h2>
      {#if !$logs || groupedLogs.size === 0}
        <EmptyState
          title="No exercises logged"
          description="No sets were logged in this session."
          icon="exercise"
        />
      {:else}
        {#each groupedLogs as [name, entryLogs] (name)}
          <Card padding={false}>
            {#snippet header()}
              <span class="text-sm font-semibold text-surface-900">{name}</span>
            {/snippet}
            <div class="p-2">
              <Table
                columns={[
                  { key: 'set', label: 'Set' },
                  { key: 'weight', label: 'Weight (kg)' },
                  { key: 'reps', label: 'Reps' },
                  { key: 'rpe', label: 'RPE' },
                  { key: 'one_rm', label: 'Est. 1RM' }
                ]}
                rows={entryLogs.map((l) => ({
                  set: `#${l.set_number}`,
                  weight: l.weight,
                  reps: l.reps,
                  rpe: l.rpe ?? '—',
                  one_rm: est1rm(l.weight, l.reps).toFixed(1)
                }))}
              />
            </div>
          </Card>
        {/each}
      {/if}
    </div>
  </div>
{:else}
  <EmptyState title="Session not found" icon="history" />
{/if}
