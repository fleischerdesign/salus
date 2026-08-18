<script lang="ts">
  import { fade } from 'svelte/transition';
  import { staggerFade } from '$lib/utils/motion';
  import { db } from '$lib/db/database';
  import { markAllNotificationsRead } from '$lib/mutations/notification';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';

  const notificationsQuery = useQuery(() =>
    db.notification
      .toArray()
      .then((arr) =>
        arr
          .filter((n) => !n.deleted_at)
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      )
  );
  const notifications = $derived(notificationsQuery.value);

  let unreadCount = $derived(notifications?.filter((n) => !n.is_read).length ?? 0);

  async function markAllRead() {
    await markAllNotificationsRead();
    // Optimistic: mark all Dexie notifications as read
    const unread = await db.notification.filter((n) => !n.is_read).toArray();
    for (const n of unread) {
      await db.notification.put({ ...n, is_read: true });
    }
  }
</script>

<svelte:head><title>Salus — Notifications</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title={`Notifications (${unreadCount} unread)`}
    subtitle="Stay updated on updates, sync alerts, and sharing triggers."
    icon="notifications"
  >
    {#snippet actions()}
      {#if unreadCount > 0}
        <Btn variant="secondary" size="sm" onclick={markAllRead}>Mark all read</Btn>
      {/if}
    {/snippet}
  </PageHeader>

  {#if !notifications}
    <div class="flex flex-col gap-3">
      {#each Array(5) as _}
        <div class="bg-surface-200 h-20 animate-pulse rounded-lg"></div>
      {/each}
    </div>
  {:else if (notifications ?? []).length === 0}
    <EmptyState title="No notifications" icon="notifications" />
  {:else}
    <div class="flex flex-col gap-3">
      {#each notifications ?? [] as n, i (n.id)}
        <div in:fade={{ ...staggerFade(i) }}>
          <Card>
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <p class="text-surface-900 text-sm font-medium">
                    {n.title ?? 'Notification'}
                  </p>
                  {#if !n.is_read}
                    <span class="bg-primary-500 h-2 w-2 rounded-full"></span>
                  {/if}
                </div>
                <p class="text-surface-600 mt-1 text-sm">
                  {n.message ?? ''}
                </p>
              </div>
            </div>
          </Card>
        </div>
      {/each}
    </div>
  {/if}
</div>
