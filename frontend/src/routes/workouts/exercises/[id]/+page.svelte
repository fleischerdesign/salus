<script lang="ts">
  import { liveQuery } from 'dexie';
  import { page } from '$app/state';
  import { db } from '$lib/db/database';
  import { epley1Rm } from '$lib/analytics/calculations';
  import Card from '$components/ui/Card.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Table from '$components/ui/Table.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Btn from '$components/ui/Btn.svelte';

  const exerciseId = $derived(page.params.id);

  let exercise = liveQuery(() =>
    db.exercise.get(exerciseId!).then((e) => (e && !e.deleted_at ? e : null))
  );

  let logs = liveQuery(() =>
    db.workout_log_entry
      .toArray()
      .then((arr) => arr.filter((l) => l.exercise_id === exerciseId! && !l.deleted_at))
  );

  let sessions = liveQuery(() =>
    db.workout_session.toArray().then((arr) => {
      const map = new Map(arr.filter((s) => !s.deleted_at).map((s) => [s.id, s]));
      return map;
    })
  );

  interface HistoryRow {
    date: string;
    set: string;
    result: string;
    rpe: string;
    one_rm: string;
    [key: string]: unknown;
  }

  let historyRows = $derived.by<HistoryRow[]>(() => {
    return ($logs ?? [])
      .filter((l) => l.weight != null && l.reps != null)
      .sort((a, b) => {
        const da = new Date(
          $sessions?.get(a.session_id)?.completed_at ??
            $sessions?.get(a.session_id)?.started_at ??
            ''
        ).getTime();
        const db = new Date(
          $sessions?.get(b.session_id)?.completed_at ??
            $sessions?.get(b.session_id)?.started_at ??
            ''
        ).getTime();
        return db - da;
      })
      .slice(0, 200)
      .map((l) => {
        const sess = $sessions?.get(l.session_id);
        const date = sess
          ? new Date(sess.completed_at ?? sess.started_at).toLocaleDateString()
          : '—';
        return {
          date,
          set: `#${l.set_number}`,
          result: `${l.weight} × ${l.reps}`,
          rpe: l.rpe != null ? String(l.rpe) : '—',
          one_rm: `${epley1Rm(l.weight, l.reps).toFixed(1)}`
        };
      });
  });

  let prMaxWeight = $derived(Math.max(0, ...($logs ?? []).map((l) => l.weight ?? 0)));

  let prEstOneRm = $derived(
    Math.max(
      0,
      ...($logs ?? []).map((l) =>
        l.weight != null && l.reps != null ? epley1Rm(l.weight, l.reps) : 0
      )
    )
  );

  let totalSets = $derived(($logs ?? []).length);
  let totalReps = $derived(($logs ?? []).reduce((sum, l) => sum + (l.reps ?? 0), 0));

  let instructions = $derived(
    $exercise?.instructions ? $exercise.instructions.split('\n').filter((l) => l.trim()) : []
  );
</script>

<svelte:head><title>Salus — {$exercise?.name ?? 'Exercise'}</title></svelte:head>

{#if !$exercise}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else if $exercise}
  <div class="space-y-6">
    <div>
      <a
        href="/workouts/exercises"
        class="duration-micro flex items-center gap-1 text-sm text-surface-500 no-underline transition-colors hover:text-surface-700"
      >
        <Icon name="arrow-back" size="sm" />Exercise Library
      </a>
      <h1 class="mt-1 text-2xl font-semibold text-surface-900">
        {$exercise.name}
      </h1>
      <div class="mt-2 flex flex-wrap gap-1.5">
        <Badge variant="default" class="capitalize">
          {$exercise.equipment}
        </Badge>
        {#each ($exercise.primary_muscles ?? '').split(',') as muscle (muscle.trim())}
          {#if muscle.trim()}
            <Badge variant="primary" class="capitalize">{muscle.trim()}</Badge>
          {/if}
        {/each}
      </div>
    </div>

    <div class="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <div class="space-y-4">
        <Card padding={false}>
          {#snippet header()}
            <div class="flex items-center gap-2">
              <Icon name="menu-book" size="sm" class="text-surface-400" />
              <span class="text-sm font-semibold text-surface-900"> Execution Instructions </span>
            </div>
          {/snippet}
          <div class="p-6">
            {#if $exercise.description}
              <p class="mb-4 text-sm leading-relaxed text-surface-600">
                {$exercise.description}
              </p>
            {/if}
            {#if instructions.length > 0}
              <ol class="list-decimal space-y-2 pl-5 text-sm leading-relaxed text-surface-600">
                {#each instructions as instr}
                  <li>{instr}</li>
                {/each}
              </ol>
            {:else if !$exercise.description}
              <p class="text-sm text-surface-400">No detailed instructions recorded.</p>
            {/if}
            {#if $exercise.video_url}
              <div class="mt-4">
                <Btn variant="secondary" size="sm" href={$exercise.video_url}>
                  <Icon name="smart-display" size="sm" />Watch Video
                </Btn>
              </div>
            {/if}
          </div>
        </Card>
      </div>

      <div class="space-y-4">
        <Card padding={false}>
          {#snippet header()}
            <div class="flex items-center gap-2">
              <Icon name="trophy" size="sm" class="text-surface-400" />
              <span class="text-sm font-semibold text-surface-900"> Personal Records </span>
            </div>
          {/snippet}
          <div class="flex flex-wrap items-center gap-x-6 gap-y-4 p-6">
            <Stat
              value={prMaxWeight > 0 ? prMaxWeight.toFixed(1) : '—'}
              unit="kg"
              label="Max Weight"
            />
            <Stat value={prEstOneRm > 0 ? prEstOneRm.toFixed(1) : '—'} unit="kg" label="Est. 1RM" />
            <Stat value={totalSets} label="Total Sets" />
            <Stat value={totalReps} label="Total Reps" />
          </div>
        </Card>

        <Card padding={false}>
          {#snippet header()}
            <div class="flex items-center gap-2">
              <Icon name="history" size="sm" class="text-surface-400" />
              <span class="text-sm font-semibold text-surface-900"> Logged History </span>
            </div>
          {/snippet}
          <div class="p-2">
            {#if historyRows.length > 0}
              <div class="max-h-[400px] overflow-y-auto">
                <Table
                  columns={[
                    { key: 'date', label: 'Date' },
                    { key: 'set', label: 'Set' },
                    { key: 'result', label: 'Result' },
                    { key: 'rpe', label: 'RPE' },
                    { key: 'one_rm', label: 'Est. 1RM' }
                  ]}
                  rows={historyRows}
                />
              </div>
            {:else}
              <div class="px-4 py-8">
                <p class="text-sm text-surface-400">No logged sets yet.</p>
              </div>
            {/if}
          </div>
        </Card>
      </div>
    </div>
  </div>
{:else}
  <EmptyState title="Exercise not found" icon="exercise" />
{/if}
