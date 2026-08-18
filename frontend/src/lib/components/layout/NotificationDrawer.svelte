<script lang="ts">
  import { fly, fade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Icon from '$components/ui/Icon.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { markNotificationRead, markAllNotificationsRead } from '$lib/mutations/notification';

  let { open = false, onclose } = $props<{
    open: boolean;
    onclose: () => void;
  }>();

  let filterType = $state<'all' | 'unread' | 'circadian' | 'medication'>('all');

  const notificationsQuery = useQuery(
    async () => {
      const all = await db.notification.toArray();
      return all
        .filter((n) => !n.deleted_at)
        .map((n) => ({
          id: n.id,
          type: (n.category as 'circadian' | 'medication' | 'milestone' | 'info') || 'info',
          title: n.title,
          desc: n.message,
          time: new Date(n.created_at).toLocaleTimeString('de-DE', {
            hour: '2-digit',
            minute: '2-digit'
          }),
          read: n.is_read
        }));
    },
    () => open
  );

  const notifications = $derived(notificationsQuery.value ?? []);
  const unreadCount = $derived(notifications.filter((n) => !n.read).length);

  const filteredList = $derived(
    notifications.filter((n) => {
      if (filterType === 'unread') return !n.read;
      if (filterType === 'circadian') return n.type === 'circadian';
      if (filterType === 'medication') return n.type === 'medication';
      return true;
    })
  );

  async function handleMarkAllRead() {
    await markAllNotificationsRead();
  }

  async function handleToggleRead(id: string) {
    await markNotificationRead(id);
  }

  const typeConfig: Record<string, { color: string; icon: string; label: string }> = {
    circadian: { color: 'var(--color-circadian)', icon: 'wb_sunny', label: 'Zirkadian' },
    medication: { color: 'var(--color-vital)', icon: 'medication', label: 'Medikation' },
    milestone: { color: 'var(--color-activity)', icon: 'fitness_center', label: 'Meilenstein' },
    info: { color: 'var(--color-primary)', icon: 'notifications', label: 'Info' }
  };
</script>

{#if open}
  <!-- Backdrop with Fade -->
  <div
    class="fixed inset-0 z-60 bg-black/60 backdrop-blur-md transition-opacity"
    transition:fade={{ duration: 220 }}
    onclick={onclose}
    role="presentation"
  ></div>

  <!-- Flyout Drawer Container -->
  <div
    class="glass-panel fixed top-0 right-0 bottom-0 z-61 flex w-full max-w-md flex-col border-l border-[var(--border-subtle)] text-[var(--text-main)] shadow-2xl"
    transition:fly={{ x: 420, duration: 320, easing: cubicOut }}
  >
    <!-- Drawer Header -->
    <div class="flex items-center justify-between border-b border-[var(--border-subtle)] px-5 py-4">
      <div class="flex items-center gap-2.5">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-primary-soft)] font-bold text-[var(--color-primary)]"
        >
          <Icon name="notifications" size="sm" />
        </div>
        <div>
          <h2 class="text-sm font-extrabold text-[var(--text-main)]">Mitteilungen &amp; Impulse</h2>
          <p class="text-[0.6875rem] text-[var(--text-muted)]">
            {unreadCount} ungelesene Benachrichtigungen
          </p>
        </div>
      </div>

      <div class="flex items-center gap-1.5">
        {#if unreadCount > 0}
          <button
            type="button"
            onclick={handleMarkAllRead}
            class="cursor-pointer rounded-lg px-2 py-1 text-[0.6875rem] font-bold text-[var(--color-primary)] transition-colors hover:underline"
          >
            Alle gelesen
          </button>
        {/if}
        <button
          type="button"
          onclick={onclose}
          class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-full text-[var(--text-muted)] transition-colors hover:bg-[var(--bg-surface-50)] hover:text-[var(--text-main)]"
        >
          <Icon name="close" size="sm" />
        </button>
      </div>
    </div>

    <!-- Filter Pills -->
    <div
      class="no-scrollbar flex items-center gap-1.5 overflow-x-auto border-b border-[var(--border-subtle)] bg-[var(--bg-surface-50)]/40 px-5 py-2.5"
    >
      <button
        type="button"
        onclick={() => (filterType = 'all')}
        class="cursor-pointer rounded-full px-2.5 py-1 text-xs font-semibold whitespace-nowrap transition-colors {filterType ===
        'all'
          ? 'bg-[var(--color-primary)] font-bold text-white'
          : 'text-[var(--text-muted)] hover:bg-[var(--bg-surface-100)]'}"
      >
        Alle ({notifications.length})
      </button>

      <button
        type="button"
        onclick={() => (filterType = 'unread')}
        class="cursor-pointer rounded-full px-2.5 py-1 text-xs font-semibold whitespace-nowrap transition-colors {filterType ===
        'unread'
          ? 'bg-[var(--color-primary)] font-bold text-white'
          : 'text-[var(--text-muted)] hover:bg-[var(--bg-surface-100)]'}"
      >
        Ungelesen ({unreadCount})
      </button>

      <button
        type="button"
        onclick={() => (filterType = 'circadian')}
        class="cursor-pointer rounded-full px-2.5 py-1 text-xs font-semibold whitespace-nowrap transition-colors {filterType ===
        'circadian'
          ? 'bg-[var(--color-circadian)] font-bold text-white'
          : 'text-[var(--text-muted)] hover:bg-[var(--bg-surface-100)]'}"
      >
        Zirkadian
      </button>

      <button
        type="button"
        onclick={() => (filterType = 'medication')}
        class="cursor-pointer rounded-full px-2.5 py-1 text-xs font-semibold whitespace-nowrap transition-colors {filterType ===
        'medication'
          ? 'bg-[var(--color-vital)] font-bold text-white'
          : 'text-[var(--text-muted)] hover:bg-[var(--bg-surface-100)]'}"
      >
        Medikation
      </button>
    </div>

    <!-- Notification Feed List -->
    <div class="flex-1 space-y-2.5 overflow-y-auto p-4">
      {#if filteredList.length === 0}
        <div
          class="flex h-64 flex-col items-center justify-center space-y-2 text-center text-[var(--text-muted)]"
        >
          <Icon name="check_circle" size="lg" class="text-emerald-500 opacity-60" />
          <p class="text-xs font-bold">Alles erledigt!</p>
          <p class="text-[0.6875rem] text-[var(--text-soft)]">
            Keine Mitteilungen in dieser Kategorie vorhanden.
          </p>
        </div>
      {:else}
        {#each filteredList as item}
          {@const conf = typeConfig[item.type] || typeConfig.info}
          <div
            class="group relative flex flex-col gap-1.5 rounded-2xl border p-3.5 transition-all {item.read
              ? 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)]/40 text-[var(--text-muted)]'
              : 'border-[var(--color-primary)]/30 bg-[var(--bg-surface-0)] text-[var(--text-main)] shadow-xs'}"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <div
                  class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[0.6875rem] text-white"
                  style="background-color: {conf.color};"
                >
                  <Icon name={conf.icon} size="sm" />
                </div>
                <span class="text-xs font-extrabold">{item.title}</span>
              </div>
              <span class="shrink-0 text-[0.625rem] font-medium text-[var(--text-soft)]"
                >{item.time}</span
              >
            </div>

            <p class="pl-8 text-xs leading-relaxed text-[var(--text-muted)]">
              {item.desc}
            </p>

            <div
              class="mt-1 flex items-center justify-between border-t border-[var(--border-subtle)]/50 pt-1 pl-8"
            >
              <button
                type="button"
                onclick={() => handleToggleRead(item.id)}
                class="cursor-pointer text-[0.6875rem] font-bold text-[var(--color-primary)] hover:underline"
              >
                {item.read ? 'Als ungelesen markieren' : 'Als gelesen markieren'}
              </button>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  </div>
{/if}
