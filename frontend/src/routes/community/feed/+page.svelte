<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { CommunityActivity } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import ProgressBar from '$components/ui/ProgressBar.svelte';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  let activities = liveQuery(() =>
    db.community_activity
      .toArray()
      .then((arr) =>
        arr.sort((a, b) => new Date(b.time ?? '').getTime() - new Date(a.time ?? '').getTime())
      )
  );

  const activityIcon: Record<string, string> = {
    workout: 'fitness-center',
    steps: 'directions-walk',
    weight: 'monitor-weight'
  };

  const activityLabel: Record<string, string> = {
    workout: 'Completed a Workout',
    steps: 'Steps Activity',
    weight: 'Logged Weight'
  };
</script>

<svelte:head><title>Salus — Community Feed</title></svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-semibold text-surface-900">Activity Feed</h1>
    <p class="mt-1 text-sm text-surface-500">
      Stay updated on your connections' health and fitness progress.
    </p>
  </div>

  {#if $activities === undefined}
    <div class="flex justify-center py-20">
      <Spinner size="lg" />
    </div>
  {:else if $activities.length === 0}
    <EmptyState
      icon="rss-feed"
      title="Your Feed is Quiet"
      description="Connect with peers to see their activity updates here."
    >
      <Btn variant="primary" href="/community/connections">Manage Connections</Btn>
    </EmptyState>
  {:else}
    <div class="space-y-4">
      {#each $activities ?? [] as act, i (act.id)}
        <div in:fade={{ ...staggerFade(i) }}>
          <Card padding={false}>
            <div class="flex items-center gap-3 px-5 pt-4">
              <div
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-600"
              >
                <Icon name={activityIcon[act.activity_type] ?? 'fitness-center'} size="sm" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-semibold text-surface-900">{act.friend_name}</p>
                <p class="text-xs text-surface-500">
                  {activityLabel[act.activity_type] ?? act.activity_description}
                  {#if act.time}· {act.time}{/if}
                </p>
              </div>
            </div>

            <div class="px-5 pt-3">
              {#if act.activity_type === 'steps' && act.value}
                <div class="flex items-baseline gap-2">
                  <span class="text-2xl font-semibold text-surface-900"
                    >{act.value.toLocaleString()}</span
                  >
                  <span class="text-sm text-surface-500">steps</span>
                </div>
                <ProgressBar value={act.value} max={10000} height="sm" class="mt-2" />
              {:else if act.value}
                <span class="text-2xl font-semibold text-surface-900">{act.value}</span>
              {/if}
              {#if act.notes}
                <p class="mt-2 text-sm text-surface-500 italic">"{act.notes}"</p>
              {/if}
            </div>

            <div class="mt-3 flex items-center gap-4 border-t border-surface-100 px-5 py-2.5">
              <button
                type="button"
                class="duration-micro flex items-center gap-1 text-xs font-medium text-surface-400 transition-colors hover:text-primary-600"
              >
                <Icon name="favorite" size="sm" />Kudos
              </button>
              <button
                type="button"
                class="duration-micro flex items-center gap-1 text-xs font-medium text-surface-400 transition-colors hover:text-primary-600"
              >
                <Icon name="chat-bubble-outline" size="sm" />Comment
              </button>
            </div>
          </Card>
        </div>
      {/each}
    </div>
  {/if}
</div>
