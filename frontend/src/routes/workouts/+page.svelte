<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { WorkoutPlan, Exercise, WorkoutSession } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  let plans = liveQuery(() =>
    db.workout_plan.toArray().then((arr) => arr.filter((p) => !p.deleted_at))
  );
  let exercises = liveQuery(() =>
    db.exercise.toArray().then((arr) => arr.filter((e) => !e.deleted_at))
  );
  let sessions = liveQuery(() =>
    db.workout_session
      .toArray()
      .then((arr) =>
        arr
          .filter((s) => !s.deleted_at)
          .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
      )
  );
  let logs = liveQuery(() =>
    db.workout_log_entry.toArray().then((arr) => arr.filter((l) => !l.deleted_at))
  );

  let recentSessions = $derived(($sessions ?? []).slice(0, 5));
  let activeSession = $derived($sessions?.find((s) => s.completed_at == null) ?? null);

  let loaded = $derived($plans != null && $exercises != null && $sessions != null && $logs != null);

  function sessionVolume(sessId: string): number {
    return ($logs ?? [])
      .filter((l) => l.session_id === sessId)
      .reduce((sum, l) => sum + (l.weight ?? 0) * (l.reps ?? 0), 0);
  }

  function formatDate(dt: string | null | undefined): string {
    if (!dt) return '—';
    return new Date(dt).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric'
    });
  }
</script>

<svelte:head><title>Salus — Workouts</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Workout Planner"
    subtitle="Create plans, track sets, and get dynamic intensity suggestions."
    icon="fitness-center"
    iconColor="#4f46e5"
  />

  {#if !loaded}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else}
    {#if activeSession}
      <a href="/workouts/active" class="block no-underline">
        <div
          class="duration-micro flex items-center justify-between rounded-lg border border-primary-200 bg-primary-50 px-5 py-3 transition-colors hover:bg-primary-100"
        >
          <div class="flex items-center gap-3">
            <Icon name="play-circle" class="text-primary-600" />
            <div>
              <p class="text-sm font-semibold text-primary-900">
                Active workout session in progress
              </p>
              <p class="text-xs text-primary-600">
                Started {formatDate(activeSession.started_at)}
              </p>
            </div>
          </div>
          <Icon name="chevron-right" class="text-primary-400" />
        </div>
      </a>
    {/if}

    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <a href="/workouts/plans" class="no-underline">
        <Card padding={false} hoverable>
          {#snippet header()}
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-50 text-primary-600"
              >
                <Icon name="assignment" />
              </div>
              <div class="flex-1">
                <p class="text-sm font-semibold text-surface-900">Training Plans</p>
                <p class="text-xs text-surface-400">
                  {$plans.length}
                  {$plans.length === 1 ? 'plan' : 'plans'}
                </p>
              </div>
            </div>
          {/snippet}
          <div class="p-6">
            {#if $plans.length > 0}
              <div class="space-y-1.5">
                {#each $plans.slice(0, 3) as plan, i (plan.id)}
                  <div
                    in:fade={{ ...staggerFade(i) }}
                    class="flex items-center justify-between text-sm"
                  >
                    <span class="truncate text-surface-700">{plan.name}</span>
                  </div>
                {/each}
              </div>
            {:else}
              <p class="text-sm text-surface-400">No plans created yet.</p>
            {/if}
          </div>
        </Card>
      </a>

      <a href="/workouts/exercises" class="no-underline">
        <Card padding={false} hoverable>
          {#snippet header()}
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-lg bg-success-50 text-success-600"
              >
                <Icon name="exercise" />
              </div>
              <div class="flex-1">
                <p class="text-sm font-semibold text-surface-900">Exercise Library</p>
                <p class="text-xs text-surface-400">
                  {$exercises.length}
                  {$exercises.length === 1 ? 'exercise' : 'exercises'}
                </p>
              </div>
            </div>
          {/snippet}
          <div class="p-6">
            {#if $exercises.length > 0}
              <div class="flex flex-wrap gap-1.5">
                {#each $exercises.slice(0, 6) as ex, i (ex.id)}
                  <span in:fade={{ ...staggerFade(i) }}
                    ><Badge variant="default">{ex.name}</Badge></span
                  >
                {/each}
                {#if $exercises.length > 6}
                  <span class="text-xs text-surface-400">+{$exercises.length - 6} more</span>
                {/if}
              </div>
            {:else}
              <p class="text-sm text-surface-400">No exercises cataloged.</p>
            {/if}
          </div>
        </Card>
      </a>

      <a href="/workouts/sessions" class="no-underline">
        <Card padding={false} hoverable>
          {#snippet header()}
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-100 text-surface-600"
              >
                <Icon name="history" />
              </div>
              <div class="flex-1">
                <p class="text-sm font-semibold text-surface-900">Session History</p>
                <p class="text-xs text-surface-400">
                  {recentSessions.length} recent
                  {recentSessions.length === 1 ? 'session' : 'sessions'}
                </p>
              </div>
            </div>
          {/snippet}
          <div class="p-6">
            {#if recentSessions.length > 0}
              <div class="space-y-1.5">
                {#each recentSessions.slice(0, 3) as sess, i (sess.id)}
                  <div
                    in:fade={{ ...staggerFade(i) }}
                    class="flex items-center justify-between text-sm"
                  >
                    <span class="truncate text-surface-700">
                      {formatDate(sess.completed_at ?? sess.started_at)}
                    </span>
                    <span class="text-xs text-surface-400"
                      >{sessionVolume(sess.id).toFixed(0)} kg</span
                    >
                  </div>
                {/each}
              </div>
            {:else}
              <p class="text-sm text-surface-400">No sessions recorded.</p>
            {/if}
          </div>
        </Card>
      </a>
    </div>
  {/if}
</div>
