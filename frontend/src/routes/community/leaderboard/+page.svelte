<script lang="ts">
  import { liveQuery } from 'dexie';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';
  import { createLeaderboard, joinLeaderboard } from '$lib/mutations/community';
  import { db } from '$lib/db/database';
  import { auth } from '$lib/stores/auth.svelte';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import Badge from '$components/ui/Badge.svelte';

  interface Challenge {
    id: string;
    name: string;
    metric_type_code: string;
    time_frame: string;
    start_date: string;
    end_date: string;
    participant_count: number;
    rank: number | null;
    score: string;
    is_creator: boolean;
  }

  let challenges = liveQuery(async () => {
    const groups = await db.leaderboard_group.toArray();
    const members = await db.leaderboard_member.toArray();

    const userId = auth.user?.id;
    const userHandle = auth.user ? `@${auth.user.username}` : null;

    return groups
      .filter((g) => {
        if (g.deleted_at) return false;
        if (!userId || !userHandle) return false;
        if (g.creator_id === userId) return true;
        return members.some(
          (m) => m.group_id === g.id && m.user_handle === userHandle && m.status === 'active'
        );
      })
      .map((g) => {
        const activeMembers = members.filter((m) => m.group_id === g.id && m.status === 'active');
        return {
          id: g.id,
          name: g.name,
          metric_type_code: g.metric_type_code,
          time_frame: g.time_frame,
          start_date: g.start_date ?? '',
          end_date: g.end_date ?? '',
          participant_count: activeMembers.length,
          rank: null,
          score: '\u2014',
          is_creator: g.creator_id === userId
        } satisfies Challenge;
      });
  });

  let inviteCode = $state('');
  let joining = $state(false);

  let createName = $state('');
  let createMetric = $state('steps');
  let createTimeframe = $state('weekly');
  let creating = $state(false);
  let error = $state('');

  const metricIcon: Record<string, string> = {
    steps: 'directions-walk',
    workouts: 'fitness-center',
    sleep: 'bedtime',
    water: 'water-drop'
  };

  const scoreUnit: Record<string, string> = {
    steps: 'steps',
    workouts: 'workouts',
    sleep: 'hrs',
    water: 'ml'
  };

  async function join(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    joining = true;
    const resp = await joinLeaderboard('', inviteCode);
    joining = false;
    if (!resp.ok) {
      error = resp.error ?? 'Request failed';
      return;
    }
    inviteCode = '';
  }

  async function create(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    creating = true;
    const resp = await createLeaderboard(createName, createMetric, createTimeframe);
    creating = false;
    if (!resp.ok) {
      error = resp.error ?? 'Request failed';
      return;
    }
    createName = '';
  }

  function rankIcon(rank: number | null) {
    if (rank === 1 || rank === 2 || rank === 3) return 'workspace-premium';
    return null;
  }

  function rankColor(rank: number | null) {
    if (rank === 1) return '#d4af37';
    if (rank === 2) return '#aaa9ad';
    if (rank === 3) return '#b08d57';
    return undefined;
  }

  function rankLabel(rank: number | null) {
    if (rank === 1) return '1st';
    if (rank === 2) return '2nd';
    if (rank === 3) return '3rd';
    if (rank) return `#${rank}`;
    return '\u2014';
  }

  const metricOptions = [
    { value: 'steps', label: 'Steps' },
    { value: 'workouts', label: 'Workouts' },
    { value: 'sleep', label: 'Sleep Duration' },
    { value: 'water', label: 'Water Intake' }
  ];

  const timeframeOptions = [
    { value: 'weekly', label: 'Rolling 7 Days' },
    { value: 'monthly', label: 'Rolling 30 Days' }
  ];
</script>

<svelte:head><title>Salus — Leaderboard</title></svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-semibold text-surface-900">Leaderboard</h1>
    <p class="mt-1 text-sm text-surface-500">
      Compete with connections and track your health rankings.
    </p>
  </div>

  {#if error}
    <AlertBanner variant="error">{error}</AlertBanner>
  {/if}

  <div class="grid gap-6 lg:grid-cols-[2fr_1.2fr]">
    <div>
      <h2 class="mb-4 text-lg font-semibold text-surface-900">Active Challenges</h2>
      {#if !$challenges}
        <div class="flex justify-center py-12"><Spinner /></div>
      {:else if $challenges.length === 0}
        <EmptyState
          icon="emoji-events"
          title="No Active Challenges"
          description="Join or create a challenge to compete with peers."
        />
      {:else}
        <div class="space-y-4">
          {#each $challenges as c, i (c.id)}
            <a
              href="/community/leaderboard/{c.id}"
              class="no-underline"
              in:fade={{ ...staggerFade(i) }}
            >
              <Card hoverable padding={false}>
                <div class="flex items-start gap-3 p-4">
                  <div
                    class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-100 text-primary-600"
                  >
                    <Icon name={metricIcon[c.metric_type_code] ?? 'emoji-events'} size="sm" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <h3 class="text-sm font-semibold text-surface-900">{c.name}</h3>
                    <p class="mt-0.5 text-xs text-surface-500">
                      {c.time_frame} · {c.metric_type_code}
                    </p>
                  </div>
                  <Badge variant="default">{c.participant_count} participants</Badge>
                </div>

                <div class="flex items-center gap-6 border-t border-surface-100 px-4 py-3">
                  <div>
                    <p class="text-[10px] font-semibold tracking-wider text-surface-400 uppercase">
                      Your Rank
                    </p>
                    <div class="mt-0.5 flex items-center gap-1.5">
                      {#if rankIcon(c.rank) && rankColor(c.rank)}
                        <Icon
                          name={rankIcon(c.rank) ?? 'workspace-premium'}
                          size="md"
                          style="color: {rankColor(c.rank)}"
                        />
                        <span class="text-base font-extrabold" style="color: {rankColor(c.rank)}"
                          >{rankLabel(c.rank)}</span
                        >
                      {:else if c.rank}
                        <span class="text-base font-extrabold text-surface-900">#{c.rank}</span>
                      {:else}
                        <span class="text-sm font-semibold text-surface-400">No data</span>
                      {/if}
                    </div>
                  </div>
                  <div>
                    <p class="text-[10px] font-semibold tracking-wider text-surface-400 uppercase">
                      Score
                    </p>
                    <p class="mt-0.5 text-base font-extrabold text-surface-900">
                      {c.score}
                      <span class="ml-1 text-xs font-semibold text-surface-500"
                        >{scoreUnit[c.metric_type_code] ?? ''}</span
                      >
                    </p>
                  </div>
                  <div
                    class="ml-auto flex items-center gap-1 text-xs font-semibold text-primary-600"
                  >
                    View Details <Icon name="arrow-forward" size="sm" />
                  </div>
                </div>
              </Card>
            </a>
          {/each}
        </div>
      {/if}
    </div>

    <div class="space-y-6">
      <Card>
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="vpn-key" size="sm" class="text-primary-500" />
            <span class="text-sm font-semibold text-surface-900">Join via Code</span>
          </div>
        {/snippet}
        <form onsubmit={join} class="flex items-end gap-2">
          <div class="flex-1">
            <FormField label="Invite Code">
              <Input name="code" bind:value={inviteCode} placeholder="A1B2-C3D4" required />
            </FormField>
          </div>
          <Btn variant="primary" type="submit" size="sm" loading={joining}>Join</Btn>
        </form>
      </Card>

      <Card>
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="add-circle" size="sm" class="text-primary-500" />
            <span class="text-sm font-semibold text-surface-900">Create Challenge</span>
          </div>
        {/snippet}
        <form onsubmit={create} class="space-y-4">
          <FormField label="Challenge Name">
            <Input
              name="name"
              bind:value={createName}
              placeholder="e.g. Weekend Step Battle"
              required
            />
          </FormField>
          <FormField label="Metric Type">
            <Select name="metric" options={metricOptions} bind:value={createMetric} />
          </FormField>
          <FormField label="Time Frame">
            <Select name="timeframe" options={timeframeOptions} bind:value={createTimeframe} />
          </FormField>
          <Btn variant="primary" type="submit" size="sm" loading={creating} fullWidth
            >Create Challenge</Btn
          >
        </form>
      </Card>
    </div>
  </div>
</div>
