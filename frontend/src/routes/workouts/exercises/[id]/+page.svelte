<script lang="ts">
  import { liveQuery } from 'dexie';
  import { page } from '$app/state';
  import { db } from '$lib/db/database';
  import { epley1Rm } from '$lib/analytics/calculations';
  import Card from '$components/ui/Card.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Table from '$components/ui/Table.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Btn from '$components/ui/Btn.svelte';

  const exerciseId = $derived(page.params.id as string);

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

  import LineChart from '$components/dashboard/LineChart.svelte';
  let chartTab = $state<'1rm' | 'tonnage'>('1rm');

  let sessionAggregates = $derived.by(() => {
    if (!$logs || !$sessions) return [];
    const grouped = new Map<string, Array<{ weight: number; reps: number }>>();
    for (const log of $logs) {
      if (log.weight != null && log.reps != null && !log.deleted_at) {
        if (!grouped.has(log.session_id)) {
          grouped.set(log.session_id, []);
        }
        grouped.get(log.session_id)!.push({ weight: log.weight, reps: log.reps });
      }
    }

    const result = [];
    for (const [sessId, sets] of grouped) {
      const sess = $sessions.get(sessId);
      if (!sess) continue;
      const dateStr = sess.completed_at ?? sess.started_at;
      if (!dateStr) continue;
      const date = new Date(dateStr);
      const tonnage = sets.reduce((sum, s) => sum + s.weight * s.reps, 0);
      const max1rm = Math.max(...sets.map((s) => epley1Rm(s.weight, s.reps)));
      result.push({
        date,
        dateLabel: date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
        tonnage,
        max1rm
      });
    }
    return result.sort((a, b) => a.date.getTime() - b.date.getTime());
  });

  let chartLabels = $derived(sessionAggregates.map((a) => a.dateLabel));
  let oneRmSeries = $derived([
    {
      label: 'Estimated 1RM (kg)',
      data: sessionAggregates.map((a) => a.max1rm),
      color: 'var(--color-primary-500)',
      yAxis: 'left' as const
    }
  ]);
  let tonnageSeries = $derived([
    {
      label: 'Tonnage (kg)',
      data: sessionAggregates.map((a) => a.tonnage),
      color: 'var(--color-success-500)',
      yAxis: 'left' as const
    }
  ]);
</script>

<svelte:head><title>Salus — {$exercise?.name ?? 'Exercise'}</title></svelte:head>

{#if !$exercise}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else if $exercise}
  <div class="space-y-6">
    <PageHeader
      title={$exercise.name}
      subtitle={$exercise.description ||
        'View execution instructions and historical training volume.'}
      icon="fitness-center"
      iconColor="#4f46e5"
      backUrl="/workouts/exercises"
    >
      {#snippet actions()}
        <div class="flex flex-wrap gap-1.5">
          <Badge variant="default" class="capitalize">
            {$exercise.equipment}
          </Badge>
          {#each ($exercise.primary_muscles ?? '').split(',') as muscle (muscle.trim())}
            {#if muscle.trim()}
              <Badge variant="primary" class="capitalize">{muscle.trim()}</Badge>
            {/if}
          {/each}
        </div>
      {/snippet}
    </PageHeader>

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

        <Card padding={false}>
          {#snippet header()}
            <div class="flex w-full items-center justify-between pr-2">
              <div class="flex items-center gap-2">
                <Icon name="monitoring" size="sm" class="text-surface-400" />
                <span class="text-sm font-semibold text-surface-900">Progress History</span>
              </div>
              <div class="flex gap-1">
                <Btn
                  variant={chartTab === '1rm' ? 'primary' : 'secondary'}
                  size="sm"
                  onclick={() => (chartTab = '1rm')}
                >
                  1RM
                </Btn>
                <Btn
                  variant={chartTab === 'tonnage' ? 'primary' : 'secondary'}
                  size="sm"
                  onclick={() => (chartTab = 'tonnage')}
                >
                  Tonnage
                </Btn>
              </div>
            </div>
          {/snippet}
          <div class="p-6">
            {#if sessionAggregates.length >= 2}
              {#if chartTab === '1rm'}
                <LineChart labels={chartLabels} series={oneRmSeries} leftUnit="kg" />
              {:else}
                <LineChart labels={chartLabels} series={tonnageSeries} leftUnit="kg" />
              {/if}
            {:else}
              <div class="flex h-[200px] items-center justify-center text-center">
                <p class="text-sm text-surface-400">
                  Perform this exercise in at least 2 sessions to see progress charts.
                </p>
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
