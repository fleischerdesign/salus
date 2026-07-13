<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';
  import { mutateDomain } from '$lib/db/mutate-domain';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import type { Notification } from '$lib/db/types';

  let open = $state(false);
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  const { value: unreadCount = 0 } = useQuery(() =>
    db.notification.filter((n) => !n.deleted_at && !n.is_read).count()
  );
  const { value: notifications = [] } = useQuery(() =>
    db.notification
      .filter((n) => !n.deleted_at)
      .toArray()
      .then((arr) =>
        arr.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      )
  );

  function show() {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    open = true;
  }

  function hide() {
    timeoutId = setTimeout(() => {
      open = false;
    }, 150);
  }

  async function markAllRead() {
    await mutateDomain({
      url: '/api/v1/notifications/read-all',
      method: 'POST'
    });
    await db.notification.filter((n) => !n.is_read && !n.deleted_at).modify({ is_read: true });
  }

  let menuClass = $derived(
    'absolute right-0 top-full mt-2 w-80 rounded-lg border border-surface-200 bg-surface-0 py-1 shadow-lg z-dropdown transition-all duration-micro ' +
      (open
        ? 'opacity-100 pointer-events-auto translate-y-0'
        : 'opacity-0 pointer-events-none -translate-y-1')
  );
</script>

<div class="relative" onmouseenter={show} onmouseleave={hide} role="presentation">
  <button
    class="duration-micro relative flex h-9 w-9 items-center justify-center rounded-full text-surface-600 transition-colors hover:bg-surface-200 hover:text-surface-900"
    aria-label="Notifications"
    aria-expanded={open}
    aria-haspopup="true"
    type="button"
  >
    <Icon name="notifications" size="md" />
    {#if unreadCount > 0}
      <span
        class="absolute top-1 right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-error-500 px-1 text-[10px] font-bold text-white"
      >
        {unreadCount > 99 ? '99+' : unreadCount}
      </span>
    {/if}
  </button>
  <div class={menuClass}>
    <div class="flex items-center justify-between border-b border-surface-200 px-4 py-2">
      <h4 class="text-sm font-semibold text-surface-900">Notifications</h4>
      {#if unreadCount > 0}
        <button
          type="button"
          class="text-xs font-medium text-primary-600 hover:text-primary-700"
          onclick={markAllRead}
        >
          Mark all read
        </button>
      {/if}
    </div>
    <div class="max-h-80 overflow-auto">
      {#if notifications.length === 0}
        <div class="px-4 py-8 text-center text-sm text-surface-400">No notifications</div>
      {:else}
        {#each notifications as n}
          <div
            class="duration-micro border-b border-surface-100 px-4 py-3 transition-colors hover:bg-surface-50 {n.is_read
              ? 'opacity-60'
              : ''}"
          >
            <div class="flex items-start gap-2">
              {#if !n.is_read}
                <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary-500"></span>
              {/if}
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-surface-900">{n.title}</p>
                <p class="text-xs text-surface-500">{n.message}</p>
                {#if n.created_at}
                  <p class="mt-1 text-[11px] text-surface-400">
                    {new Date(n.created_at).toLocaleString()}
                  </p>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  </div>
</div>
