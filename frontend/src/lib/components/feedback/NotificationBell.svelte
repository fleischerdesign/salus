<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import StatusDot from '$components/ui/StatusDot.svelte';
  import { markAllNotificationsRead } from '$lib/mutations/notification';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  let open = $state(false);
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  const notificationsQuery = useQuery(() =>
    db.notification
      .filter((n) => !n.deleted_at)
      .toArray()
      .then((arr) =>
        arr.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      )
  );
  const notifications = $derived(notificationsQuery.value ?? []);

  let unreadList = $derived(notifications.filter((n) => !n.is_read));
  let unreadCount = $derived(unreadList.length);

  let highestSeverity = $derived.by(() => {
    if (unreadCount === 0) return null;
    // Severity cascade: critical > warning > success > info
    const hasCritical = unreadList.some(
      (n) =>
        (n as unknown as { severity?: string }).severity === 'critical' ||
        n.title.toLowerCase().includes('update') ||
        n.title.toLowerCase().includes('security')
    );
    if (hasCritical) return 'critical' as const;

    const hasWarning = unreadList.some(
      (n) => (n as unknown as { severity?: string }).severity === 'warning'
    );
    if (hasWarning) return 'warning' as const;

    const hasSuccess = unreadList.some(
      (n) => (n as unknown as { severity?: string }).severity === 'success'
    );
    if (hasSuccess) return 'success' as const;

    return 'info' as const;
  });

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
    await markAllNotificationsRead();
    await db.notification.filter((n) => !n.is_read && !n.deleted_at).modify({ is_read: true });
  }

  let menuClass = $derived(
    'absolute right-0 top-full mt-2 w-80 rounded-xl border border-surface-200 bg-surface-0 py-1 shadow-lg z-50 transition-all duration-micro ' +
      (open
        ? 'opacity-100 pointer-events-auto translate-y-0'
        : 'opacity-0 pointer-events-none -translate-y-1')
  );
</script>

<div class="relative" onmouseenter={show} onmouseleave={hide} role="presentation">
  <button
    class="duration-micro relative flex h-9 w-9 cursor-pointer items-center justify-center rounded-full text-surface-600 transition-colors hover:bg-surface-200 hover:text-surface-900"
    aria-label="Notifications"
    aria-expanded={open}
    aria-haspopup="true"
    type="button"
  >
    <Icon name="notifications" size="md" />
    {#if highestSeverity}
      <StatusDot
        status={highestSeverity}
        size="sm"
        class="absolute top-[2px] right-[2px] ring-2 ring-surface-0"
      />
    {/if}
  </button>
  <div class={menuClass}>
    <div class="flex items-center justify-between border-b border-surface-200 px-4 py-2.5">
      <div class="flex items-center gap-2">
        <h3 class="text-sm font-semibold text-surface-900">Notifications</h3>
        {#if unreadCount > 0}
          <span
            class="rounded-full bg-surface-100 px-1.5 py-0.5 text-[10px] font-bold text-surface-600"
          >
            {unreadCount}
          </span>
        {/if}
      </div>
      {#if unreadCount > 0}
        <button
          type="button"
          class="cursor-pointer text-xs font-semibold text-primary-600 hover:text-primary-700"
          onclick={markAllRead}
        >
          Mark all read
        </button>
      {/if}
    </div>
    <div class="max-h-80 overflow-y-auto">
      {#if notifications.length === 0}
        <div class="px-4 py-8 text-center text-sm text-surface-400">No notifications</div>
      {:else}
        {#each notifications as n}
          {@const isCritical =
            (n as unknown as { severity?: string }).severity === 'critical' ||
            n.title.toLowerCase().includes('update')}
          <div
            class="duration-micro border-b border-surface-100 px-4 py-3 transition-colors hover:bg-surface-50 {n.is_read
              ? 'opacity-60'
              : ''}"
          >
            <div class="flex items-start gap-2.5">
              {#if !n.is_read}
                <span
                  class="mt-1.5 h-2 w-2 shrink-0 rounded-full {isCritical
                    ? 'animate-pulse bg-error-500'
                    : 'bg-primary-500'}"
                ></span>
              {/if}
              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between">
                  <p class="text-sm font-semibold text-surface-900">{n.title}</p>
                  {#if isCritical}
                    <span
                      class="rounded-md bg-error-50 px-1.5 py-0.5 text-[10px] font-bold text-error-700 uppercase"
                    >
                      Update
                    </span>
                  {/if}
                </div>
                <p class="mt-0.5 text-xs leading-relaxed text-surface-600">{n.message}</p>
                {#if n.created_at}
                  <p class="mt-1 font-mono text-[10px] text-surface-400">
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
