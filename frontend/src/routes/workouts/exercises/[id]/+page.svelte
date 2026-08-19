<script lang="ts">
  import { page } from '$app/state';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { brzycki1Rm } from '$lib/analytics/calculations';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import SegmentedControl from '$components/ui/SegmentedControl.svelte';
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
          ? new Date(sess.completed_at ?? sess.started_at).toLocaleDateString('de-DE', {
              day: '2-digit',
              month: '2-digit',
              year: 'numeric'
            })
          : '—';
        return {
          date,
          set: `#${l.set_number}`,
          result: `${l.weight} kg × ${l.reps}`,
          rpe: l.rpe != null ? `@${l.rpe}` : '—',
          one_rm: `${brzycki1Rm(l.weight, l.reps).toFixed(1)} kg`
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
  let totalTonnage = $derived(
    (logs ?? []).reduce((sum, l) => sum + (l.weight ?? 0) * (l.reps ?? 0), 0)
  );

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
      color: '#2563eb',
      yAxis: 'left' as const
    }
  ]);
  let tonnageSeries = $derived([
    {
      label: 'Tonnage (kg)',
      data: sessionAggregates.map((a) => a.tonnage),
      color: '#059669',
      yAxis: 'left' as const
    }
  ]);
</script>

<svelte:head><title>Salus — {exercise?.name ?? 'Übung'}</title></svelte:head>

{#if !exercise}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else if exercise}
  <div class="space-y-6">
    <!-- Back Navigation Breadcrumb -->
    <div>
      <a
        href="/workouts"
        class="inline-flex items-center gap-1.5 text-xs font-bold text-text-muted hover:text-text-main transition-colors"
      >
        <Icon name="arrow_back" class="text-sm" />
        <span>Zurück zu Übungen</span>
      </a>
    </div>

    <!-- Hero Header -->
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div class="space-y-1.5">
        <div class="flex flex-wrap items-center gap-2">
          <h1 class="text-2xl font-extrabold tracking-tight sm:text-3xl">{exercise.name}</h1>
          <Badge variant={exercise.user_id ? 'activity' : 'default'} class="text-[0.6875rem]">
            {exercise.user_id ? 'Benutzerdefiniert' : 'System-Übung'}
          </Badge>
          <div class="flex items-center gap-1 rounded-md border border-border-subtle bg-surface-50 px-2 py-0.5 text-xs font-semibold text-text-muted">
            <Icon name="fitness_center" class="text-xs" />
            <span class="capitalize">{exercise.equipment || 'Frei'}</span>
          </div>
          {#if exercise.suggested_rest_seconds}
            <div class="rounded-md border border-border-subtle bg-surface-50 px-2 py-0.5 font-mono text-xs text-text-muted">
              {exercise.suggested_rest_seconds}s Pause
            </div>
          {/if}
        </div>
        {#if exercise.description}
          <p class="max-w-3xl text-xs leading-relaxed text-text-muted sm:text-sm">
            {exercise.description}
          </p>
        {/if}
      </div>

      {#if exercise.video_url}
        <Btn variant="secondary" size="sm" href={exercise.video_url}>
          <Icon name="smart_display" class="text-sm" />
          <span>Videoanleitung</span>
        </Btn>
      {/if}
    </div>

    <!-- 4 Statistical KPI Tiles -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <span class="block text-[0.6875rem] font-bold tracking-wider text-text-muted uppercase">
          PR Gewicht
        </span>
        <div class="mt-1 text-2xl font-extrabold text-text-main tabular-nums">
          {#if prMaxWeight > 0}
            {prMaxWeight.toFixed(1)} <span class="text-xs font-semibold text-text-soft">kg</span>
          {:else}
            <span class="text-base font-normal text-text-muted">—</span>
          {/if}
        </div>
      </div>

      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <span class="block text-[0.6875rem] font-bold tracking-wider text-text-muted uppercase">
          PR e1RM (Brzycki)
        </span>
        <div class="mt-1 text-2xl font-extrabold text-text-main tabular-nums">
          {#if prEstOneRm > 0}
            {prEstOneRm.toFixed(1)} <span class="text-xs font-semibold text-text-soft">kg</span>
          {:else}
            <span class="text-base font-normal text-text-muted">—</span>
          {/if}
        </div>
      </div>

      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <span class="block text-[0.6875rem] font-bold tracking-wider text-text-muted uppercase">
          Sätze & Wdh.
        </span>
        <div class="mt-1 text-2xl font-extrabold text-text-main tabular-nums">
          {totalSets} <span class="text-xs font-semibold text-text-soft">Sätze</span>
          <span class="text-xs font-normal text-text-muted">· {totalReps} Wdh</span>
        </div>
      </div>

      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-4 shadow-xs">
        <span class="block text-[0.6875rem] font-bold tracking-wider text-text-muted uppercase">
          Gesamt-Tonnage
        </span>
        <div class="mt-1 text-2xl font-extrabold text-text-main tabular-nums">
          {#if totalTonnage > 0}
            {Math.round(totalTonnage).toLocaleString()} <span class="text-xs font-semibold text-text-soft">kg</span>
          {:else}
            <span class="text-base font-normal text-text-muted">—</span>
          {/if}
        </div>
      </div>
    </div>

    <!-- Main Content 2-Column Split -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
      <!-- Left Column (Anatomy & Execution): 5 cols on lg -->
      <div class="space-y-6 lg:col-span-5">
        <!-- 2D Anatomical Mannequin Card -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <div class="flex items-center justify-between border-b border-border-subtle/60 pb-3">
            <div class="flex items-center gap-2">
              <Icon name="accessibility_new" class="text-primary" />
              <h2 class="text-sm font-extrabold text-text-main">Zielmuskulatur</h2>
            </div>
            <SegmentedControl
              size="sm"
              bind:value={mannequinView}
              options={[
                { value: 'anterior', label: 'Front' },
                { value: 'posterior', label: 'Rück' }
              ]}
            />
          </div>

          <div class="flex flex-col items-center">
            <div class="flex h-[240px] w-full items-center justify-center">
              <AnatomicalBodyVector
                view={mannequinView as 'anterior' | 'posterior'}
                {pathColorMap}
              />
            </div>

            <!-- Targeted Muscles Badges -->
            <div class="mt-3 w-full space-y-2 border-t border-border-subtle pt-3 text-xs">
              <div>
                <span class="block text-[11px] font-bold text-primary">Primär (100% Satzvolumen):</span>
                <div class="mt-1.5 flex flex-wrap gap-1.5">
                  {#each parseMuscles(exercise.primary_muscles) as pKey}
                    {@const pDef = DETAILED_MUSCLE_MAP[pKey as DetailedMuscleKey]}
                    <span
                      class="inline-flex items-center gap-1 rounded-md bg-primary-soft px-2 py-0.5 text-[11px] font-bold text-primary"
                      title={pDef?.latin}
                    >
                      {pDef?.name || pKey}
                    </span>
                  {/each}
                </div>
              </div>

              {#if parseMuscles(exercise.secondary_muscles).length > 0}
                <div>
                  <span class="block text-[11px] font-bold text-[#818cf8]">Synergisten (50% Satzvolumen):</span>
                  <div class="mt-1.5 flex flex-wrap gap-1.5">
                    {#each parseMuscles(exercise.secondary_muscles) as sKey}
                      {@const sDef = DETAILED_MUSCLE_MAP[sKey as DetailedMuscleKey]}
                      <span
                        class="inline-flex items-center gap-1 rounded-md bg-[#818cf8]/15 px-2 py-0.5 text-[11px] font-medium text-[#818cf8]"
                        title={`Synergist: ${sDef?.latin || sKey}`}
                      >
                        {sDef?.name || sKey}
                      </span>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
          </div>
        </div>

        <!-- Execution & Technique Steps -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <div class="flex items-center gap-2 border-b border-border-subtle/60 pb-3">
            <Icon name="menu_book" class="text-primary" />
            <h2 class="text-sm font-extrabold text-text-main">Ausführung & Technik</h2>
          </div>

          {#if instructions.length > 0}
            <ol class="space-y-3">
              {#each instructions as instr, idx}
                <li class="flex items-start gap-3 text-xs leading-relaxed text-text-muted">
                  <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-surface-100 text-[10px] font-extrabold text-text-main">
                    {idx + 1}
                  </span>
                  <span class="pt-0.5">{instr}</span>
                </li>
              {/each}
            </ol>
          {:else}
            <p class="text-xs text-text-muted italic">
              Keine schrittweisen Ausführungshinweise für diese Übung hinterlegt.
            </p>
          {/if}
        </div>
      </div>

      <!-- Right Column (Performance & Set History): 7 cols on lg -->
      <div class="space-y-6 lg:col-span-7">
        <!-- Performance Progression Chart -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-border-subtle/60 pb-3">
            <div class="flex items-center gap-2">
              <Icon name="monitoring" class="text-primary" />
              <h2 class="text-sm font-extrabold text-text-main">Leistungsverlauf</h2>
            </div>
            <SegmentedControl
              size="sm"
              bind:value={chartTab}
              options={[
                { value: '1rm', label: '1RM Verlauf' },
                { value: 'tonnage', label: 'Tonnage' }
              ]}
            />
          </div>

          <div>
            {#if sessionAggregates.length >= 2}
              {#if chartTab === '1rm'}
                <LineChart labels={chartLabels} series={oneRmSeries} leftUnit="kg" />
              {:else}
                <LineChart labels={chartLabels} series={tonnageSeries} leftUnit="kg" />
              {/if}
            {:else}
              <div class="flex h-[200px] flex-col items-center justify-center space-y-1.5 text-center text-xs text-text-muted">
                <Icon name="show_chart" class="text-xl text-text-soft opacity-60" />
                <p class="font-semibold text-text-main">Noch nicht genügend Einheiten</p>
                <p class="text-[11px] text-text-soft max-w-xs">
                  Protokolliere diese Übung in mindestens 2 Trainingseinheiten, um den Verlauf zu visualisieren.
                </p>
              </div>
            {/if}
          </div>
        </div>

        <!-- Logged Sets History Table -->
        <div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
          <div class="flex items-center justify-between border-b border-border-subtle/60 pb-3">
            <div class="flex items-center gap-2">
              <Icon name="history" class="text-primary" />
              <h2 class="text-sm font-extrabold text-text-main">Historie aller protokollierten Sätze</h2>
            </div>
            <span class="font-mono text-xs text-text-soft">
              {historyRows.length} {historyRows.length === 1 ? 'Satz' : 'Sätze'}
            </span>
          </div>

          {#if historyRows.length > 0}
            <div class="max-h-[400px] overflow-y-auto no-scrollbar rounded-xl border border-border-subtle">
              <table class="w-full text-left text-xs">
                <thead class="sticky top-0 bg-surface-50 text-[10px] font-bold text-text-muted uppercase tracking-wider border-b border-border-subtle">
                  <tr>
                    <th class="px-3.5 py-2.5">Datum</th>
                    <th class="px-3 py-2.5">Satz</th>
                    <th class="px-3 py-2.5">Leistung</th>
                    <th class="px-3 py-2.5">RPE</th>
                    <th class="px-3.5 py-2.5 text-right">e1RM</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border-subtle bg-surface-0">
                  {#each historyRows as row}
                    <tr class="hover:bg-surface-50/60 transition-colors">
                      <td class="px-3.5 py-2.5 font-mono text-[11px] text-text-muted">{row.date}</td>
                      <td class="px-3 py-2.5 font-mono text-[11px] font-bold text-text-soft">{row.set}</td>
                      <td class="px-3 py-2.5 font-bold text-text-main tabular-nums">{row.result}</td>
                      <td class="px-3 py-2.5 font-mono text-[11px] text-text-muted">{row.rpe}</td>
                      <td class="px-3.5 py-2.5 font-mono text-[11px] font-bold text-primary text-right tabular-nums">
                        {row.one_rm}
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {:else}
            <div class="py-10 text-center text-xs text-text-muted space-y-1">
              <Icon name="event_note" class="mx-auto text-xl text-text-soft opacity-60" />
              <p class="font-semibold text-text-main">Noch keine protokollierten Sätze</p>
              <p class="text-[11px] text-text-soft">
                Sobald du diese Übung in einem Workout absolvierst, erscheinen deine Sätze hier.
              </p>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
{:else}
  <EmptyState title="Übung nicht gefunden" icon="fitness_center" />
{/if}
