<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import Card from '$components/ui/Card.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';

  let counts = liveQuery(async () => {
    const [connections, challenges] = await Promise.all([
      db.sharing_relationship.filter((r) => !r.deleted_at).count(),
      db.leaderboard_group.filter((g) => !g.deleted_at).count()
    ]);
    return { connections, challenges };
  });

  const cards = [
    {
      href: '/community/feed',
      icon: 'rss-feed',
      title: 'Activity Feed',
      description: "Stay updated on your connections' health and fitness progress."
    },
    {
      href: '/community/leaderboard',
      icon: 'emoji-events',
      title: 'Leaderboard',
      description: 'Compete with connections and track your health rankings.',
      count: () => $counts?.challenges ?? null,
      countLabel: 'active challenges'
    },
    {
      href: '/community/connections',
      icon: 'groups',
      title: 'Connections',
      description: 'Manage your peer-to-peer health data sharing relationships.',
      count: () => $counts?.connections ?? null,
      countLabel: 'connections'
    }
  ] as const;
</script>

<svelte:head><title>Salus — Community</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Community"
    subtitle="Connect, compete, and share your health journey with peers."
    icon="groups"
    iconColor="#4f46e5"
  />

  {#if !$counts}
    <div class="flex justify-center py-16">
      <Spinner size="lg" />
    </div>
  {:else}
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {#each cards as card}
        <a href={card.href} class="no-underline">
          <Card>
            <div class="flex items-start gap-3">
              <div
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-surface-100"
              >
                <Icon name={card.icon} class="text-surface-600" />
              </div>
              <div class="min-w-0 flex-1">
                <h3 class="text-sm font-semibold text-surface-900">{card.title}</h3>
                <p class="mt-1 text-xs text-surface-500">{card.description}</p>
                {#if (card as { count?: () => number | null }).count}
                  <div
                    class="mt-2 inline-flex items-center gap-1 rounded-full bg-surface-100 px-2 py-0.5 text-xs font-medium text-surface-600"
                  >
                    {(card as { count?: () => number | null }).count!()}
                    {(card as { countLabel?: string }).countLabel}
                  </div>
                {/if}
              </div>
            </div>
          </Card>
        </a>
      {/each}
    </div>
  {/if}
</div>
