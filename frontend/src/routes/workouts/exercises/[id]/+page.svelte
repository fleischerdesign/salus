<script lang="ts">
  import { page } from '$app/state';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { brzycki1Rm } from '$lib/analytics/calculations';
  import Card from '$components/ui/Card.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Stat from '$components/ui/Stat.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Table from '$components/ui/Table.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import LineChart from '$components/dashboard/LineChart.svelte';
  import AnatomicalBodyVector from '$components/track/AnatomicalBodyVector.svelte';
  import {
    DETAILED_MUSCLE_MAP,
    parseMuscles,
    type DetailedMuscleKey
  } from '$lib/types/workouts';

  const exerciseId = $derived(page.params.id as string);

  const exerciseQuery = useQuery(
    () => db.exercise.get(exerciseId!).then((e) => (e && !e.deleted_at ? e : null)),
    () => exerciseId
  );
  const exercise = $derived(exerciseQuery.value);

  const logsQuery = useQuery(
    () =>
      db.workout_log_entry
        .toArray()
        .then((arr) => arr.filter((l) => l.exercise_id === exerciseId! && !l.deleted_at)),
    () => exerciseId
  );
  const logs = $derived(logsQuery.value);

  const sessionsQuery = useQuery(() =>
    db.workout_session.toArray().then((arr) => {
      const map = new Map(arr.filter((s) => !s.deleted_at).map((s) => [s.id, s]));
      return map;
    })
  );
  const sessions = $derived(sessionsQuery.value);

  let mannequinView = $state<'anterior' | 'posterior'>('anterior');
  let chartTab = $state<'1rm' | 'tonnage'>('1rm');

  // Compute exact path colors for the 2D anatomical mannequin
  const pathColorMap = $derived.by(() => {
    if (!exercise) return {};
    const map: Record<string, string> = {};

    const primaryTokens = parseMuscles(exercise.primary_muscles);
    for (const key of primaryTokens) {
      const def = DETAILED_MUSCLE_MAP[key as DetailedMuscleKey];
      if (def) {
        for (const pid of def.svgPathIds) {
          map[pid] = 'var(--color-primary)';
        }
      }
    }

    const secondaryTokens = parseMuscles(exercise.secondary_muscles);
    for (const key of secondaryTokens) {
      const def = DETAILED_MUSCLE_MAP[key as DetailedMuscleKey];
      if (def) {
        for (const pid of def.svgPathIds) {
          if (!map[pid]) {
            map[pid] = '#818cf8';
          }
        }
      }
    }

    return map;
  });

  interface HistoryRow {
    date: string;
    set: string;
    result: string;
    rpe: string;
    one_rm: string;
    [key: string]: unknown;
  }

  let historyRows = $derived.by<HistoryRow[]>(() => {
    return (logs ?? [])
      .filter((l) => l.weight != null && l.reps != null)
      .sort((a, b) => {
        const da = new Date(
          sessions?.get(a.session_id)?.completed_at ?? sessions?.get(a.session_id)?.started_at ?? ''
        ).getTime();
        const db = new Date(
          sessions?.get(b.session_id)?.completed_at ?? sessions?.get(b.session_id)?.started_at ?? ''
        ).getTime();
        return db - da;
      })
      .slice(0, 200)
      .map((l) => {
        const sess = sessions?.get(l.session_id);
        const date = sess
          ? new Date(sess.completed_at ?? sess.started_at).toLocaleDateString()
          : '—';
        return {
          date,
          set: `#${l.set_number}`,
          result: `${l.weight} × ${l.reps}`,
          rpe: l.rpe != null ? String(l.rpe) : '—',
          one_rm: `${brzycki1Rm(l.weight, l.reps).toFixed(1)}`
        };
      });
  });

  let prMaxWeight = $derived(Math.max(0, ...(logs ?? []).map((l) => l.weight ?? 0)));

  let prEstOneRm = $derived(
    Math.max(
      0,
      ...(logs ?? []).map((l) =>
        l.weight != null && l.reps != null ? brzycki1Rm(l.weight, l.reps) : 0
      )
    )
  );

  let totalSets = $derived((logs ?? []).length);
  let totalReps = $derived((logs ?? []).reduce((sum, l) => sum + (l.reps ?? 0), 0));

  let instructions = $derived(
    exercise?.instructions ? exercise.instructions.split('\n').filter((l) => l.trim()) : []
  );

  let sessionAggregates = $derived.by(() => {
    if (!logs || !sessions) return [];
    const grouped = new Map<string, Array<{ weight: number; reps: number }>>();
    for (const log of logs) {
      if (log.weight != null && log.reps != null && !log.deleted_at) {
        if (!grouped.has(log.session_id)) {
          grouped.set(log.session_id, []);
        }
        grouped.get(log.session_id)!.push({ weight: log.weight, reps: log.reps });
      }
    }

    const result = [];
    for (const [sessId, sets] of grouped) {
      const sess = sessions.get(sessId);
      if (!sess) continue;
      const dateStr = sess.completed_at ?? sess.started_at;
      if (!dateStr) continue;
      const date = new Date(dateStr);
      const tonnage = sets.reduce((sum, s) => sum + s.weight * s.reps, 0);
      const max1rm = Math.max(...sets.map((s) => brzycki1Rm(s.weight, s.reps)));
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

<svelte:head><title>Salus — {exercise?.name ?? 'Übung'}</title></svelte:head>

{#if !exercise}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else if exercise}
  <div class="space-y-6">
    <PageHeader
      title={exercise.name}
      subtitle={exercise.description ||
        'Ausführungshinweise, anatomische Zielmuskeln und historischer Trainingsfortschritt.'}
      icon="fitness-center"
      backUrl="/workouts"
    >
      {#snippet actions()}
        <div class="flex flex-wrap h-full items-center gap-1.5 px-6">
          <Badge variant="default" class="capitalize">
            {exercise.equipment}
          </Badge>
          {#each parseMuscles(exercise.primary_muscles) as pKey}
            {@const pDef = DETAILED_MUSCLE_MAP[pKey as DetailedMuscleKey]}
            <Badge variant="primary" class="capitalize">{pDef?.name || pKey}</Badge>
          {/each}
          {#each parseMuscles(exercise.secondary_muscles) as sKey}
            {@const sDef = DETAILED_MUSCLE_MAP[sKey as DetailedMuscleKey]}
            <span
              class="inline-flex items-center gap-1 rounded-full bg-[#818cf8]/15 px-2.5 py-0.5 text-xs font-semibold text-[#818cf8]"
            >
              {sDef?.name || sKey}
            </span>
          {/each}
        </div>
      {/snippet}

      {#snippet stats()}
        <div
          class="divide-surface-100 grid grid-cols-2 divide-y sm:grid-cols-4 sm:divide-x sm:divide-y-0"
        >
          <div class="px-6 py-4">
            <Stat
              value={prMaxWeight > 0 ? prMaxWeight.toFixed(1) : '—'}
              unit="kg"
              label="PR Gewicht"
            />
          </div>
          <div class="px-6 py-4">
            <Stat
              value={prEstOneRm > 0 ? prEstOneRm.toFixed(1) : '—'}
              unit="kg"
              label="PR e1RM"
            />
          </div>
          <div class="px-6 py-4">
            <Stat value={totalSets} label="Gesamt-Sätze" />
          </div>
          <div class="px-6 py-4">
            <Stat value={totalReps} label="Gesamt-Wdh." />
          </div>
        </div>
      {/snippet}
    </PageHeader>

    <div class="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <!-- Left Column: Instructions & Charts -->
      <div class="space-y-4">
        <!-- Execution Instructions -->
        <Card padding={false}>
          {#snippet header()}
            <div class="flex items-center gap-2">
              <Icon name="menu-book" size="sm" class="text-surface-400" />
              <span class="text-surface-900 text-sm font-semibold">Ausführung & Technik</span>
            </div>
          {/snippet}
          <div class="p-6">
            {#if exercise.description}
              <p class="text-surface-600 mb-4 text-sm leading-relaxed">
                {exercise.description}
              </p>
            {/if}
            {#if instructions.length > 0}
              <ol class="text-surface-600 list-decimal space-y-2 pl-5 text-sm leading-relaxed">
                {#each instructions as instr}
                  <li>{instr}</li>
                {/each}
              </ol>
            {:else if !exercise.description}
              <p class="text-surface-400 text-sm">Keine detaillierten Ausführungshinweise hinterlegt.</p>
            {/if}
            {#if exercise.video_url}
              <div class="mt-4">
                <Btn variant="secondary" size="sm" href={exercise.video_url}>
                  <Icon name="smart-display" size="sm" />Video ansehen
                </Btn>
              </div>
            {/if}
          </div>
        </Card>

        <!-- Progress History Chart -->
        <Card padding={false}>
          {#snippet header()}
            <div class="flex w-full items-center justify-between pr-2">
              <div class="flex items-center gap-2">
                <Icon name="monitoring" size="sm" class="text-surface-400" />
                <span class="text-surface-900 text-sm font-semibold">Leistungsverlauf</span>
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
                <p class="text-surface-400 text-sm">
                  Führe diese Übung in mindestens 2 Einheiten durch, um Verlaufsdiagramme zu sehen.
                </p>
              </div>
            {/if}
          </div>
        </Card>
      </div>

      <!-- Right Column: 2D Anatomical Mannequin & History Table -->
      <div class="space-y-4">
        <!-- 2D Anatomical Mannequin Card -->
        <Card padding={false}>
          {#snippet header()}
            <div class="flex w-full items-center justify-between pr-2">
              <div class="flex items-center gap-2">
                <Icon name="accessibility_new" size="sm" class="text-surface-400" />
                <span class="text-surface-900 text-sm font-semibold">Zielmuskulatur (2D Body)</span>
              </div>
              <div class="flex gap-1">
                <button
                  type="button"
                  onclick={() => (mannequinView = 'anterior')}
                  class={`rounded px-2 py-0.5 text-xs font-bold ${
                    mannequinView === 'anterior'
                      ? 'bg-[var(--color-heading)] text-white'
                      : 'text-[var(--color-text-muted)] hover:bg-[var(--bg-surface-200)]'
                  }`}
                >
                  Front
                </button>
                <button
                  type="button"
                  onclick={() => (mannequinView = 'posterior')}
                  class={`rounded px-2 py-0.5 text-xs font-bold ${
                    mannequinView === 'posterior'
                      ? 'bg-[var(--color-heading)] text-white'
                      : 'text-[var(--color-text-muted)] hover:bg-[var(--bg-surface-200)]'
                  }`}
                >
                  Rück
                </button>
              </div>
            </div>
          {/snippet}
          <div class="p-4 flex flex-col items-center">
            <div class="h-[220px] w-full flex items-center justify-center">
              <AnatomicalBodyVector view={mannequinView} {pathColorMap} />
            </div>

            <!-- Legend of targeted muscles -->
            <div class="w-full mt-3 space-y-2 border-t border-[var(--border-subtle)] pt-3 text-xs">
              <div>
                <span class="font-bold text-[var(--color-primary)]">Primär (100%):</span>
                <div class="mt-1 flex flex-wrap gap-1">
                  {#each parseMuscles(exercise.primary_muscles) as pKey}
                    {@const pDef = DETAILED_MUSCLE_MAP[pKey as DetailedMuscleKey]}
                    <span class="rounded bg-[var(--color-primary-soft)] px-2 py-0.5 font-bold text-[var(--color-primary)]">
                      {pDef?.name || pKey}
                    </span>
                  {/each}
                </div>
              </div>

              {#if parseMuscles(exercise.secondary_muscles).length > 0}
                <div>
                  <span class="font-bold text-[#818cf8]">Sekundär (50%):</span>
                  <div class="mt-1 flex flex-wrap gap-1">
                    {#each parseMuscles(exercise.secondary_muscles) as sKey}
                      {@const sDef = DETAILED_MUSCLE_MAP[sKey as DetailedMuscleKey]}
                      <span class="rounded bg-[#818cf8]/15 px-2 py-0.5 font-medium text-[#818cf8]">
                        {sDef?.name || sKey}
                      </span>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
          </div>
        </Card>

        <!-- Logged History Table -->
        <Card padding={false}>
          {#snippet header()}
            <div class="flex items-center gap-2">
              <Icon name="history" size="sm" class="text-surface-400" />
              <span class="text-surface-900 text-sm font-semibold">Historie aller Sätze</span>
            </div>
          {/snippet}
          <div class="p-2">
            {#if historyRows.length > 0}
              <div class="max-h-[350px] overflow-y-auto">
                <Table
                  columns={[
                    { key: 'date', label: 'Datum' },
                    { key: 'set', label: 'Satz' },
                    { key: 'result', label: 'Ergebnis' },
                    { key: 'rpe', label: 'RPE' },
                    { key: 'one_rm', label: 'e1RM' }
                  ]}
                  rows={historyRows}
                />
              </div>
            {:else}
              <div class="px-4 py-8 text-center">
                <p class="text-surface-400 text-sm">Noch keine protokollierten Sätze.</p>
              </div>
            {/if}
          </div>
        </Card>
      </div>
    </div>
  </div>
{:else}
  <EmptyState title="Übung nicht gefunden" icon="exercise" />
{/if}
