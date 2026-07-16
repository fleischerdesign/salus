<script lang="ts">
  import { liveQuery } from 'dexie';
  import {
    createConnection,
    acceptConnection,
    declineConnection,
    deleteConnection
  } from '$lib/mutations/community';
  import { db } from '$lib/db/database';
  import { auth } from '$lib/stores/auth.svelte';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Input from '$components/ui/Input.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import ListItem from '$components/ui/ListItem.svelte';
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';

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

  let peers = liveQuery(async () => {
    const uid = auth.user?.id;
    const username = auth.user?.username;
    if (!uid || !username) return [];

    const [rels, metricTypes, profiles] = await Promise.all([
      db.sharing_relationship.toArray(),
      db.metric_type.toArray(),
      db.user_profile.toArray()
    ]);

    const active = rels.filter((r) => !r.deleted_at);
    const metricMap = new Map(metricTypes.filter((m) => !m.deleted_at).map((m) => [m.id, m]));
    const profileById = new Map(profiles.map((p) => [p.id, p]));

    const peerMap = new Map<string, PeerConnection>();

    for (const rel of active) {
      const isOwned = rel.owner_id === uid;
      const isGrantee = rel.grantee_handle === username;
      if (!isOwned && !isGrantee) continue;

      const peerHandle = isOwned
        ? rel.grantee_handle
        : (profileById.get(rel.owner_id)?.username ?? `user_${rel.owner_id}`);

      const metric = metricMap.get(rel.metric_type_id);

      const pm: PeerMetric = {
        metric_name: metric?.name ?? `Metric #${rel.metric_type_id}`,
        icon: metric?.icon ?? 'monitoring',
        color: metric?.color ?? '#6b7280',
        aggregation: rel.aggregation_level,
        direction: isOwned ? 'outgoing' : 'incoming',
        relationship_id: rel.id
      };

      let peer = peerMap.get(peerHandle);
      if (!peer) {
        peer = {
          handle: peerHandle,
          display_name: '',
          is_mutual: false,
          is_remote: peerHandle.includes(':'),
          is_pending: false,
          metrics: [],
          expiration: null,
          api_token: null,
          last_sync: null
        };
        peerMap.set(peerHandle, peer);
      }

      peer.metrics.push(pm);
      if (rel.status === 'pending') peer.is_pending = true;
      if (rel.expiration_date && (!peer.expiration || rel.expiration_date > peer.expiration))
        peer.expiration = rel.expiration_date;
      if (rel.last_sync_at && (!peer.last_sync || rel.last_sync_at > peer.last_sync))
        peer.last_sync = rel.last_sync_at;
    }

    for (const peer of peerMap.values()) {
      const hasOut = peer.metrics.some((m) => m.direction === 'outgoing');
      const hasIn = peer.metrics.some((m) => m.direction === 'incoming');
      peer.is_mutual = hasOut && hasIn;
    }

    return [...peerMap.values()];
  });

  let error = $state('');
  let granteeHandle = $state('');
  let sharing = $state(false);

  async function invite(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    sharing = true;
    const resp = await createConnection(granteeHandle);
    sharing = false;
    if (!resp.ok) {
      error = resp.error ?? 'Request failed';
      return;
    }
    granteeHandle = '';
  }

  async function revoke(id: string) {
    if (!confirm('Revoke this connection?')) return;
    await deleteConnection(id);
  }

  async function accept(id: string) {
    const resp = await acceptConnection(id);
    if (!resp.ok) {
      error = resp.error ?? 'Request failed';
      return;
    }
  }

  async function decline(id: string) {
    const resp = await declineConnection(id);
    if (!resp.ok) {
      error = resp.error ?? 'Request failed';
      return;
    }
  }
</script>

<svelte:head><title>Salus — Connections</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Connections"
    subtitle="Manage your peer-to-peer health data sharing relationships."
    icon="groups"
    iconColor="#4f46e5"
    backUrl="/community"
  />

  {#if error}
    <AlertBanner variant="error">{error}</AlertBanner>
  {/if}

  <Card>
    {#snippet header()}
      <span class="text-sm font-semibold text-surface-900">Invite a Peer</span>
    {/snippet}
    <form onsubmit={invite} class="flex max-w-lg items-end gap-3">
      <div class="flex-1">
        <FormField label="Peer Handle">
          <Input
            name="handle"
            bind:value={granteeHandle}
            placeholder="@username or @username:domain.com"
            required
          />
        </FormField>
      </div>
      <Btn variant="primary" type="submit" size="sm" loading={sharing}>Invite</Btn>
    </form>
    <p class="mt-2 text-xs text-surface-400">
      Supports federation: use @username:domain for remote Salus instances.
    </p>
  </Card>

  <Card padding={false}>
    {#snippet header()}
      <span class="text-sm font-semibold text-surface-900">Active Connections</span>
    {/snippet}
    {#if !$peers}
      <div class="flex justify-center py-12"><Spinner /></div>
    {:else if $peers.length === 0}
      <div class="py-12">
        <EmptyState
          icon="groups"
          title="No Connections Yet"
          description="Invite a peer to start sharing health data securely."
        />
      </div>
    {:else}
      <div class="grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-3">
        {#each $peers as peer, i (peer.handle)}
          <div in:fade={{ ...staggerFade(i) }}>
            <a href="/community/connections/{peer.handle}" class="group/card block h-full">
              <div
                class="flex h-full cursor-pointer flex-col rounded-lg border border-surface-200 p-4 transition-shadow hover:shadow-md"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <p
                      class="text-sm font-semibold text-surface-900 transition-colors group-hover/card:text-primary-600"
                    >
                      {peer.display_name || peer.handle}
                    </p>
                    <p class="text-xs text-surface-500">{peer.handle}</p>
                  </div>
                  <div class="flex gap-1.5 font-sans">
                    {#if peer.is_remote}
                      <Badge variant="primary">Remote</Badge>
                    {/if}
                    {#if peer.is_pending}
                      <Badge variant="warning">Pending</Badge>
                    {:else if !peer.is_mutual}
                      <Badge variant="default">Outgoing</Badge>
                    {:else}
                      <Badge variant="success">Mutual</Badge>
                    {/if}
                  </div>
                </div>

                {#if peer.metrics.length > 0}
                  <div class="mt-3 space-y-1.5">
                    {#each peer.metrics as m}
                      <div class="flex items-center gap-2 text-xs text-surface-500">
                        <Icon name={m.icon} size="sm" style="color: {m.color}" />
                        <span>{m.metric_name}</span>
                        <span
                          class="rounded bg-surface-100 px-1.5 py-0.5 text-[10px] font-medium text-surface-400"
                        >
                          {m.aggregation} · {m.direction}
                        </span>
                      </div>
                    {/each}
                  </div>
                {/if}

                <div class="mt-auto flex items-center justify-end gap-2 pt-3">
                  {#if peer.is_pending}
                    <!-- svelte-ignore a11y_click_events_have_key_events -->
                    <span
                      role="button"
                      tabindex="-1"
                      onclick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                    >
                      <Btn
                        variant="primary"
                        size="sm"
                        onclick={() => accept(peer.metrics[0]?.relationship_id)}
                      >
                        Accept
                      </Btn>
                    </span>
                    <!-- svelte-ignore a11y_click_events_have_key_events -->
                    <span
                      role="button"
                      tabindex="-1"
                      onclick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                    >
                      <Btn
                        variant="ghost"
                        size="sm"
                        onclick={() => decline(peer.metrics[0]?.relationship_id)}
                      >
                        Decline
                      </Btn>
                    </span>
                  {:else}
                    <!-- svelte-ignore a11y_click_events_have_key_events -->
                    <span
                      role="button"
                      tabindex="-1"
                      onclick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                    >
                      <Btn
                        variant="ghost"
                        size="sm"
                        onclick={() => revoke(peer.metrics[0]?.relationship_id)}
                      >
                        Revoke
                      </Btn>
                    </span>
                  {/if}
                </div>
              </div>
            </a>
          </div>
        {/each}
      </div>
    {/if}
  </Card>
</div>
