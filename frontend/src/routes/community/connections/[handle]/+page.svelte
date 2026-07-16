<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { mergeMetricPrefs } from '$lib/db/types';
  import { auth } from '$lib/stores/auth.svelte';
  import { deleteConnection } from '$lib/mutations/community';
  import { page } from '$app/state';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import ProgressBar from '$components/ui/ProgressBar.svelte';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

  const handle = $derived((page.params.handle as string) ?? '');

  interface PeerMetric {
    metric_name: string;
    icon: string;
    color: string;
    aggregation: string;
    direction: string;
    relationship_id: string;
  }

  interface PeerConnection {
    handle: string;
    display_name: string;
    is_mutual: boolean;
    is_remote: boolean;
    is_pending: boolean;
    metrics: PeerMetric[];
    expiration: string | null;
    api_token: string | null;
    last_sync: string | null;
  }

  // Load single peer connection details
  let peer = liveQuery(async () => {
    const uid = auth.user?.id;
    const username = auth.user?.username;
    if (!uid || !username || !handle) return null;

    const [rels, metricTypes, prefs, profiles] = await Promise.all([
      db.sharing_relationship.toArray(),
      db.metric_definition.toArray(),
      db.user_metric_preference.toArray(),
      db.user_profile.toArray()
    ]);

    const active = rels.filter((r) => !r.deleted_at);
    const merged = mergeMetricPrefs(metricTypes, prefs);
    const metricMap = new Map(merged.map((m) => [m.code, m]));
    const profileById = new Map(profiles.map((p) => [p.id, p]));

    let resolvedPeer: PeerConnection | null = null;

    for (const rel of active) {
      const isOwned = rel.owner_id === uid;
      const isGrantee = rel.grantee_handle === username;
      if (!isOwned && !isGrantee) continue;

      const peerHandle = isOwned
        ? rel.grantee_handle
        : (profileById.get(rel.owner_id)?.username ?? `user_${rel.owner_id}`);

      if (peerHandle !== handle) continue;

      const metric = metricMap.get(rel.metric_code);

      const pm: PeerMetric = {
        metric_name: metric?.name ?? `Metric #${rel.metric_code}`,
        icon: metric?.icon ?? 'monitoring',
        color: metric?.color ?? '#6b7280',
        aggregation: rel.aggregation_level,
        direction: isOwned ? 'outgoing' : 'incoming',
        relationship_id: rel.id
      };

      if (!resolvedPeer) {
        resolvedPeer = {
          handle: peerHandle,
          display_name: profileById.get(rel.owner_id)?.display_name ?? '',
          is_mutual: false,
          is_remote: peerHandle.includes(':'),
          is_pending: false,
          metrics: [],
          expiration: null,
          api_token: null,
          last_sync: null
        };
      }

      resolvedPeer.metrics.push(pm);
      if (rel.status === 'pending') resolvedPeer.is_pending = true;
      if (
        rel.expiration_date &&
        (!resolvedPeer.expiration || rel.expiration_date > resolvedPeer.expiration)
      )
        resolvedPeer.expiration = rel.expiration_date;
      if (
        rel.last_sync_at &&
        (!resolvedPeer.last_sync || rel.last_sync_at > resolvedPeer.last_sync)
      )
        resolvedPeer.last_sync = rel.last_sync_at;
    }

    if (resolvedPeer) {
      const hasOut = resolvedPeer.metrics.some((m) => m.direction === 'outgoing');
      const hasIn = resolvedPeer.metrics.some((m) => m.direction === 'incoming');
      resolvedPeer.is_mutual = hasOut && hasIn;
    }

    return resolvedPeer;
  });

  // Filter activities belonging only to this connection
  let activities = liveQuery(async () => {
    if (!handle) return [];
    const p = await db.user_profile.where('username').equals(handle).first();
    const displayName = p?.display_name ?? '';

    return db.community_activity
      .toArray()
      .then((arr) =>
        arr
          .filter(
            (act) => act.friend_name === handle || (displayName && act.friend_name === displayName)
          )
          .sort((a, b) => new Date(b.time ?? '').getTime() - new Date(a.time ?? '').getTime())
      );
  });

  async function revoke(id: string) {
    if (!confirm('Revoke this connection?')) return;
    await deleteConnection(id);
    window.location.href = '/community/connections';
  }

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

<svelte:head>
  <title>Salus — Connection Details</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <PageHeader
    title={$peer?.display_name || handle}
    subtitle={handle}
    backUrl="/community/connections"
    icon="person"
    iconColor="#4f46e5"
  >
    {#snippet actions()}
      {#if $peer}
        <div class="flex gap-1.5 font-sans">
          {#if $peer.is_remote}
            <Badge variant="primary">Remote</Badge>
          {/if}
          {#if $peer.is_pending}
            <Badge variant="warning">Pending</Badge>
          {:else if !$peer.is_mutual}
            <Badge variant="default">Outgoing</Badge>
          {:else}
            <Badge variant="success">Mutual</Badge>
          {/if}
        </div>
      {/if}
    {/snippet}

    {#snippet stats()}
      {#if $peer}
        <div class="grid gap-6 px-6 py-6 md:grid-cols-2">
          {#if $peer.last_sync}
            <div class="space-y-1">
              <span class="text-xs font-medium tracking-wider text-surface-400 uppercase"
                >Last Synced</span
              >
              <div class="text-sm font-semibold text-surface-700">
                {new Date($peer.last_sync).toLocaleDateString(undefined, {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
          {/if}

          {#if $peer.expiration}
            <div class="space-y-1">
              <span class="text-xs font-medium tracking-wider text-surface-400 uppercase"
                >Expires On</span
              >
              <div class="text-sm font-semibold text-surface-700">
                {new Date($peer.expiration).toLocaleDateString(undefined, {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric'
                })}
              </div>
            </div>
          {/if}
        </div>
      {/if}
    {/snippet}
  </PageHeader>

  {#if !$peer || !$activities}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else}
    <div class="grid gap-6 lg:grid-cols-12">
      <!-- Shared Metrics Card -->
      <Card padding={false} class="lg:col-span-4">
        {#snippet header()}
          <span class="text-sm font-semibold text-surface-900">Shared Metrics</span>
        {/snippet}
        <div class="space-y-4 p-6">
          {#if $peer.metrics.length === 0}
            <p class="text-xs text-surface-400">No active metrics sharing setup.</p>
          {:else}
            <div class="space-y-3">
              {#each $peer.metrics as m}
                <div
                  class="flex items-center justify-between rounded-lg border border-surface-100 bg-surface-50 p-3"
                >
                  <div class="flex items-center gap-2">
                    <Icon name={m.icon} size="sm" style="color: {m.color}" />
                    <span class="text-sm font-medium text-surface-700">{m.metric_name}</span>
                  </div>
                  <span
                    class="bg-surface-150 rounded px-2 py-0.5 text-[10px] font-semibold tracking-wider text-surface-500 uppercase"
                  >
                    {m.direction}
                  </span>
                </div>
              {/each}
            </div>
          {/if}
          <div class="border-t border-surface-100 pt-4">
            <Btn
              variant="danger"
              class="w-full justify-center"
              size="sm"
              onclick={() => revoke($peer.metrics[0]?.relationship_id)}
            >
              Revoke Connection
            </Btn>
          </div>
        </div>
      </Card>

      <!-- Friend's Activity Feed -->
      <Card padding={false} class="lg:col-span-8">
        {#snippet header()}
          <span class="text-sm font-semibold text-surface-900">Recent Activities</span>
        {/snippet}
        <div class="divide-y divide-surface-100">
          {#if $activities.length === 0}
            <div class="p-8">
              <EmptyState
                icon="rss-feed"
                title="No Activities Logged"
                description="This connection hasn't shared any fitness activities yet."
              />
            </div>
          {:else}
            {#each $activities as act, i (act.id)}
              <div
                in:fade={{ ...staggerFade(i) }}
                class="p-5 transition-colors hover:bg-surface-50"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-600"
                  >
                    <Icon name={activityIcon[act.activity_type] ?? 'fitness-center'} size="sm" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <p class="text-sm font-semibold text-surface-900">
                      {activityLabel[act.activity_type] ?? act.activity_description}
                    </p>
                    <p class="text-xs text-surface-500">{act.time}</p>
                  </div>
                </div>

                <div class="pt-3 pl-13">
                  {#if act.activity_type === 'steps' && act.value}
                    <div class="flex items-baseline gap-2">
                      <span class="text-2xl font-bold text-surface-900"
                        >{act.value.toLocaleString()}</span
                      >
                      <span class="text-sm text-surface-500">steps</span>
                    </div>
                    <ProgressBar value={act.value} max={10000} height="sm" class="mt-2 max-w-sm" />
                  {:else if act.value}
                    <span class="text-2xl font-bold text-surface-900">{act.value}</span>
                  {/if}
                  {#if act.notes}
                    <p class="mt-2 text-sm text-surface-500 italic">"{act.notes}"</p>
                  {/if}
                </div>
              </div>
            {/each}
          {/if}
        </div>
      </Card>
    </div>
  {/if}
</div>
