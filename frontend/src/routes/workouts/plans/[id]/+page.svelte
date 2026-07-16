<script lang="ts">
  import { liveQuery } from 'dexie';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import { startWorkout } from '$lib/mutations/workout';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import ListItem from '$components/ui/ListItem.svelte';

  const planId = $derived(page.params.id as string);

  let plan = liveQuery(() =>
    db.workout_plan.get(planId!).then((p) => (p && !p.deleted_at ? p : null))
  );

  let planExercises = liveQuery(() =>
    db.workout_plan_exercise
      .toArray()
      .then((arr) =>
        arr
          .filter((pe) => pe.plan_id === planId && !pe.deleted_at)
          .sort((a, b) => a.sequence - b.sequence)
      )
  );

  let exercises = liveQuery(() =>
    db.exercise.toArray().then((arr) => {
      const map = new Map(arr.map((e) => [e.id, e]));
      return map;
    })
  );

  let sessions = liveQuery(() =>
    db.workout_session
      .toArray()
      .then((arr) =>
        arr
          .filter((s) => !s.deleted_at && s.plan_id === planId && s.completed_at != null)
          .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
      )
  );

  let logs = liveQuery(() =>
    db.workout_log_entry.toArray().then((arr) => arr.filter((l) => !l.deleted_at))
  );

  let starting = $state(false);

  async function startSession() {
    starting = true;
    const { ok } = await startWorkout(planId!, $plan?.autoreg_mode || 'advisory');
    starting = false;
    if (ok) await goto('/workouts/active');
  }

  function formatDuration(sessStart: string, sessEnd: string | null): string {
    if (!sessStart || !sessEnd) return '—';
    return `${Math.round((new Date(sessEnd).getTime() - new Date(sessStart).getTime()) / 60000)} min`;
  }

  function sessionVolume(sessId: string): number {
    return ($logs ?? [])
      .filter((l) => l.session_id === sessId)
      .reduce((sum, l) => sum + (l.weight ?? 0) * (l.reps ?? 0), 0);
  }
</script>

<svelte:head><title>Salus — {$plan?.name ?? 'Plan'}</title></svelte:head>

{#if !$plan || !$planExercises}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else if $plan}
  <div class="space-y-6">
    <PageHeader
      title={$plan.name}
      subtitle={$plan.description || 'Training routine details and completed history.'}
      icon="event_note"
      iconColor="#4f46e5"
      backUrl="/workouts/plans"
    >
      {#snippet actions()}
        <div class="mr-2 flex items-center gap-1.5">
          <Badge
            variant={$plan.autoreg_mode === 'disabled' ? 'default' : 'primary'}
            class="capitalize"
          >
            {$plan.autoreg_mode}
          </Badge>
          <Badge variant="default">{$planExercises.length} exercises</Badge>
        </div>
        <Btn variant="primary" loading={starting} onclick={startSession}>
          <Icon name="play-arrow" size="sm" />Start Workout
        </Btn>
      {/snippet}
    </PageHeader>

    <div class="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <div class="space-y-3">
        <h2 class="text-lg font-semibold text-surface-900">Exercises</h2>
        {#if $planExercises.length === 0}
          <EmptyState
            title="No exercises"
            description="No exercises in this plan yet."
            icon="exercise"
          />
        {:else}
          <Card padding={false}>
            <div class="divide-y divide-surface-100">
              {#each $planExercises as pe (pe.id)}
                {@const ex = $exercises?.get(pe.exercise_id)}
                <ListItem hoverable>
                  {#snippet children()}
                    <a
                      href="/workouts/exercises/{pe.exercise_id}"
                      class="flex min-w-0 flex-1 items-center justify-between gap-3 no-underline"
                    >
                      <div class="min-w-0">
                        <p class="truncate text-sm font-medium text-surface-900">
                          {ex?.name ?? 'Unknown'}
                        </p>
                        <p class="mt-0.5 text-xs text-surface-400 capitalize">
                          {ex?.equipment ?? ''} · {ex?.primary_muscles ?? ''}
                        </p>
                      </div>
                      <div class="shrink-0 text-right">
                        <p class="text-sm font-semibold text-surface-700">
                          {pe.target_sets}×{pe.target_reps}
                        </p>
                        <p class="text-xs text-surface-400">@ RPE {pe.target_rpe ?? '—'}</p>
                      </div>
                    </a>
                  {/snippet}
                </ListItem>
              {/each}
            </div>
          </Card>
        {/if}
      </div>

      <div class="space-y-3">
        <h2 class="text-lg font-semibold text-surface-900">Session History</h2>
        {#if !$sessions || $sessions.length === 0}
          <Card
            ><p class="text-sm text-surface-400">No completed sessions for this plan yet.</p></Card
          >
        {:else}
          <Card padding={false}>
            <div class="divide-y divide-surface-100">
              {#each $sessions.slice(0, 10) as sess (sess.id)}
                <ListItem hoverable>
                  {#snippet children()}
                    <a
                      href="/workouts/sessions/{sess.id}"
                      class="flex min-w-0 flex-1 items-center justify-between gap-3 no-underline"
                    >
                      <div class="min-w-0">
                        <p class="truncate text-sm font-medium text-surface-700">
                          {new Date(sess.completed_at ?? sess.started_at).toLocaleDateString()}
                        </p>
                        <p class="text-xs text-surface-400">
                          {formatDuration(sess.started_at, sess.completed_at)} · {sessionVolume(
                            sess.id
                          ).toFixed(0)} kg
                        </p>
                      </div>
                      <Icon name="chevron-right" size="sm" class="text-surface-400" />
                    </a>
                  {/snippet}
                </ListItem>
              {/each}
            </div>
          </Card>
        {/if}
      </div>
    </div>
  </div>
{:else}
  <EmptyState title="Plan not found" icon="assignment" />
{/if}
