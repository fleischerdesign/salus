<script lang="ts">
  import { liveQuery } from 'dexie';
  import { mutateDomain } from '$lib/db/mutate-domain';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import { auth } from '$lib/stores/auth.svelte';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';

  interface Ranking {
    rank: number;
    username: string;
    score: string;
    is_me: boolean;
  }

  interface ChallengeDetail {
    id: number;
    name: string;
    metric_type_code: string;
    time_frame: string;
    start_date: string;
    end_date: string;
    invite_code: string;
    created_by: string;
    is_creator: boolean;
    rankings: Ranking[];
  }

  let copied = $state(false);

  const challengeId = $derived(Number(page.params.id));

  let detail = liveQuery(async () => {
    const group = await db.leaderboard_group.get(challengeId);
    if (!group || group.deleted_at) return null;

    const members = await db.leaderboard_member
      .where('group_id')
      .equals(challengeId)
      .toArray();

    const activeMembers = members.filter(
      (m) => m.status === 'active' && !m.deleted_at,
    );

    const userHandle = auth.user ? `@${auth.user.username}` : null;
    const userId = auth.user?.id;

    const rankings: Ranking[] = activeMembers.map((m, i) => ({
      rank: i + 1,
      username: m.user_handle.startsWith('@') ? m.user_handle.slice(1) : m.user_handle,
      score: '\u2014',
      is_me: userHandle ? m.user_handle === userHandle : false,
    }));

    return {
      id: group.id,
      name: group.name,
      metric_type_code: group.metric_type_code,
      time_frame: group.time_frame,
      start_date: group.start_date ?? '',
      end_date: group.end_date ?? '',
      invite_code: group.invite_code,
      created_by: String(group.creator_id),
      is_creator: group.creator_id === userId,
      rankings,
    } satisfies ChallengeDetail;
  });

  const metricIcon: Record<string, string> = {
    steps: 'directions-walk',
    workouts: 'fitness-center',
    sleep: 'bedtime',
    water: 'water-drop',
  };

  const scoreUnit: Record<string, string> = {
    steps: 'steps',
    workouts: 'workouts',
    sleep: 'hrs',
    water: 'ml',
  };

  async function disband() {
    if (!confirm('Disband this challenge? This cannot be undone.')) return;
    await mutateDomain({
      url: `/api/v1/sharing/leaderboard/${challengeId}/delete`,
      method: 'POST',
    });
    await goto('/community/leaderboard');
  }

  async function leave() {
    if (!confirm('Leave this challenge?')) return;
    await mutateDomain({
      url: `/api/v1/sharing/leaderboard/${challengeId}/leave`,
      method: 'POST',
    });
    await goto('/community/leaderboard');
  }

  async function copyInviteCode() {
    const current = $detail;
    if (!current) return;
    await navigator.clipboard.writeText(current.invite_code);
    copied = true;
    setTimeout(() => (copied = false), 2000);
  }

  function rankIcon(rank: number) { return rank <= 3 ? 'workspace-premium' : null; }

  function rankColor(rank: number) {
    if (rank === 1) return '#d4af37';
    if (rank === 2) return '#aaa9ad';
    if (rank === 3) return '#b08d57';
    return undefined;
  }
</script>

<svelte:head><title>Salus — Challenge</title></svelte:head>

{#if !$detail}
  <div class="flex justify-center py-20">
    <Spinner size="lg" />
  </div>
{:else if $detail}
  <div class="max-w-4xl space-y-6">
    <a href="/community/leaderboard" class="inline-flex items-center gap-1.5 text-sm font-medium text-surface-500 no-underline transition-colors duration-150 hover:text-surface-700">
      <Icon name="arrow-back" size="sm" />Back to Challenges
    </a>

    <div class="flex flex-wrap items-start justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-100 text-primary-600">
          <Icon name={metricIcon[$detail.metric_type_code] ?? 'emoji-events'} size="lg" />
        </div>
        <div>
          <h1 class="text-2xl font-semibold text-surface-900">{$detail.name}</h1>
          <p class="mt-1 flex items-center gap-1.5 text-sm text-surface-500">
            <span class="capitalize">{$detail.time_frame}</span>·<span>{$detail.metric_type_code}</span>·<span>{new Date($detail.start_date).toLocaleDateString()} — {new Date($detail.end_date).toLocaleDateString()}</span>
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3 rounded-lg border border-surface-200 bg-surface-50 px-4 py-3">
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wider text-surface-400">Invite Code</p>
          <code class="text-sm font-bold tracking-wide text-surface-700">{$detail.invite_code}</code>
        </div>
        <Btn variant="secondary" size="sm" onclick={copyInviteCode}>
          <Icon name={copied ? 'check' : 'content-copy'} size="sm" />{copied ? 'Copied' : 'Copy'}
        </Btn>
      </div>
    </div>

    <Card padding={false}>
      {#snippet header()}
        {#if $detail}
        <div class="flex items-center justify-between">
          <span class="text-sm font-semibold text-surface-900">Standings</span>
          <span class="text-xs font-semibold uppercase tracking-wider text-primary-500">{$detail.metric_type_code}</span>
        </div>
        {/if}
      {/snippet}

      {#if $detail.rankings.length === 0}
        <div class="py-12">
          <EmptyState icon="leaderboard" title="No participants yet" description="Share the invite code to get started." />
        </div>
      {:else}
        <div class="divide-y divide-surface-100">
          {#each $detail.rankings as r}
            <div class="flex items-center justify-between px-5 py-3.5 {r.is_me ? 'bg-primary-50' : ''}">
              <div class="flex items-center gap-4">
                <div class="flex w-7 justify-center">
                  {#if rankIcon(r.rank)}
                    <Icon name="workspace-premium" size="md" style="color: {rankColor(r.rank)}" />
                  {:else}
                    <span class="text-sm font-semibold text-surface-400">#{r.rank}</span>
                  {/if}
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-sm font-semibold text-surface-900">{r.username}</span>
                  {#if r.is_me}
                    <Badge variant="primary">You</Badge>
                  {/if}
                </div>
              </div>
              <span class="text-sm font-semibold text-surface-700">
                {r.score}
                <span class="ml-1 text-xs font-medium text-surface-500">{scoreUnit[$detail.metric_type_code] ?? ''}</span>
              </span>
            </div>
          {/each}
        </div>
      {/if}
    </Card>

    <div class="flex items-center justify-between">
      <p class="text-sm text-surface-400">Created by <strong>@{$detail.created_by}</strong></p>
      {#if $detail.is_creator}
        <Btn variant="danger" size="sm" onclick={disband}>Disband Challenge</Btn>
      {:else}
        <Btn variant="secondary" size="sm" onclick={leave}>Leave Challenge</Btn>
      {/if}
    </div>
  </div>
{/if}
