<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { WorkoutSession } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import ListItem from '$components/ui/ListItem.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  let sessions = liveQuery(() =>
    db.workout_session.toArray().then((arr) =>
      arr
        .filter((s) => !s.deleted_at && s.completed_at != null)
        .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
        .slice(0, 50)
    )
  );

  let logs = liveQuery(() =>
    db.workout_log_entry.toArray().then((arr) => arr.filter((l) => !l.deleted_at))
  );

  function formatDate(dt: string | null | undefined): string {
    if (!dt) return '—';
    return new Date(dt).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  function formatDuration(sess: WorkoutSession): string {
    if (!sess.started_at || !sess.completed_at) return '—';
    const diff = new Date(sess.completed_at).getTime() - new Date(sess.started_at).getTime();
    return `${Math.round(diff / 60000)} min`;
  }

  function sessionLogs(sessId: string) {
    return ($logs ?? []).filter((l) => l.session_id === sessId);
  }

  function sessionVolume(sessId: string): number {
    return sessionLogs(sessId).reduce((sum, l) => sum + (l.weight ?? 0) * (l.reps ?? 0), 0);
  }

  function sessionSetCount(sessId: string): number {
    return sessionLogs(sessId).length;
  }
</script>

<svelte:head><title>Salus — Session History</title></svelte:head>

<div class="space-y-6">
  <div>
    <a
      href="/workouts"
      class="duration-micro flex items-center gap-1 text-sm text-surface-500 no-underline transition-colors hover:text-surface-700"
    >
      <Icon name="arrow-back" size="sm" />Workouts
    </a>
    <h1 class="mt-1 text-2xl font-semibold text-surface-900">Session History</h1>
  </div>

  {#if !$sessions || !$logs}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else if $sessions.length === 0}
    <EmptyState
      title="No sessions recorded"
      description="Start a workout to see your training history here."
      icon="history"
    />
  {:else}
    <Card padding={false}>
      <div class="divide-y divide-surface-100">
        {#each $sessions as sess, i (sess.id)}
          <div in:fade={{ ...staggerFade(i) }}>
            {#if sess.completed_at}
              <ListItem hoverable>
                {#snippet children()}
                  <a
                    href="/workouts/sessions/{sess.id}"
                    class="flex min-w-0 flex-1 items-center justify-between gap-3 no-underline"
                  >
                    <div class="min-w-0">
                      <div class="flex items-center gap-2">
                        <span class="text-sm font-semibold text-surface-900">
                          {formatDate(sess.completed_at)}
                        </span>
                        {#if sess.recovery_score}
                          <Badge variant="success">
                            <Icon name="bolt" size="sm" />{Math.round(sess.recovery_score)}%
                          </Badge>
                        {/if}
                      </div>
                      <p class="mt-0.5 truncate text-xs text-surface-500">
                        {sessionSetCount(sess.id)} sets · {sessionVolume(sess.id).toFixed(0)} kg volume
                        · {formatDuration(sess)}
                      </p>
                      {#if sess.notes}
                        <p class="mt-0.5 truncate text-xs text-surface-400 italic">
                          "{sess.notes}"
                        </p>
                      {/if}
                    </div>
                    <Icon name="chevron-right" size="sm" class="text-surface-400" />
                  </a>
                {/snippet}
              </ListItem>
            {/if}
          </div>
        {/each}
      </div>
    </Card>
  {/if}
</div>
