<script lang="ts">
  import { fly, fade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    open = false,
    onclose
  } = $props<{
    open: boolean;
    onclose: () => void;
  }>();

  interface NotificationItem {
    id: string;
    type: 'circadian' | 'medication' | 'milestone' | 'info';
    title: string;
    desc: string;
    time: string;
    read: boolean;
  }

  let filterType = $state<'all' | 'unread' | 'circadian' | 'medication'>('all');

  let notifications = $state<NotificationItem[]>([
    {
      id: '1',
      type: 'circadian',
      title: 'Zirkadianer Impuls: Koffein-Cutoff',
      desc: 'Um 14:30 Uhr beginnt dein Koffein-Stopp zur Optimierung der nächtlichen Adenosin-Rezeptoren.',
      time: 'vor 15 Min',
      read: false
    },
    {
      id: '2',
      type: 'medication',
      title: 'Erinnerung: Magnesiumbisglycinat',
      desc: '400 mg elementares Magnesium vor dem Schlafen (21:30 Uhr).',
      time: 'vor 1 Std',
      read: false
    },
    {
      id: '3',
      type: 'milestone',
      title: 'Neuer 1RM-Rekord: Bankdrücken',
      desc: 'Herzlichen Glückwunsch! Du hast 143.0 kg geschätzt erreicht (+15.3% seit Juni).',
      time: 'vor 3 Std',
      read: true
    },
    {
      id: '4',
      type: 'circadian',
      title: 'Morgen-Lichtdusche empfohlen',
      desc: 'Innerhalb der ersten 30 Minuten nach dem Aufwachen 10.000 Lux natürliches Sonnenlicht tanken.',
      time: 'heute 07:15',
      read: true
    }
  ]);

  let unreadCount = $derived(notifications.filter(n => !n.read).length);

  let filteredList = $derived(
    notifications.filter(n => {
      if (filterType === 'unread') return !n.read;
      if (filterType === 'circadian') return n.type === 'circadian';
      if (filterType === 'medication') return n.type === 'medication';
      return true;
    })
  );

  function markAllRead() {
    notifications = notifications.map(n => ({ ...n, read: true }));
  }

  function toggleRead(id: string) {
    notifications = notifications.map(n => (n.id === id ? { ...n, read: !n.read } : n));
  }

  function removeNotification(id: string) {
    notifications = notifications.filter(n => n.id !== id);
  }

  const typeConfig = {
    circadian: { color: 'var(--color-circadian)', icon: 'sun', label: 'Zirkadian' },
    medication: { color: 'var(--color-vital)', icon: 'vital', label: 'Medikation' },
    milestone: { color: 'var(--color-activity)', icon: 'workout', label: 'Meilenstein' },
    info: { color: 'var(--color-primary)', icon: 'food', label: 'Info' }
  };
</script>

{#if open}
  <!-- Backdrop with Fade -->
  <div
    class="fixed inset-0 bg-black/60 backdrop-blur-md z-60 transition-opacity"
    transition:fade={{ duration: 220 }}
    onclick={onclose}
    role="presentation"
  ></div>

  <!-- Slide-Over Drawer with Spring-Out Fly -->
  <div
    class="fixed top-0 right-0 bottom-0 w-full max-w-md bg-[var(--glass-dock-bg)] backdrop-blur-2xl border-l border-[var(--border-subtle)] z-65 shadow-2xl flex flex-col p-5 sm:p-6 space-y-4"
    transition:fly={{ x: 420, duration: 320, easing: cubicOut }}
  >
    <!-- Header -->
    <div class="flex items-center justify-between pb-3 border-b border-[var(--border-subtle)]">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold">
          <Icon name="sun" size={18} />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Mitteilungen</h2>
            {#if unreadCount > 0}
              <Badge variant="primary" class="text-[0.625rem] tabular-nums font-bold animate-pulse-glow">
                {unreadCount} neu
              </Badge>
            {/if}
          </div>
          <p class="text-xs text-[var(--text-muted)]">Zirkadiane Impulse und Systemhinweise</p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        {#if unreadCount > 0}
          <button
            type="button"
            class="text-xs text-[var(--color-primary)] hover:underline cursor-pointer font-bold transition-all"
            onclick={markAllRead}
          >
            Alle gelesen
          </button>
        {/if}
        <button
          type="button"
          class="w-8 h-8 rounded-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center text-lg cursor-pointer transition-colors shadow-xs"
          onclick={onclose}
          aria-label="Schließen"
        >
          &times;
        </button>
      </div>
    </div>

    <!-- Filter Pills -->
    <div class="flex gap-1.5 overflow-x-auto no-scrollbar py-0.5">
      <button
        type="button"
        onclick={() => filterType = 'all'}
        class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer {filterType === 'all' ? 'bg-[var(--color-primary)] text-white shadow-xs' : 'bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        Alle ({notifications.length})
      </button>
      <button
        type="button"
        onclick={() => filterType = 'unread'}
        class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer {filterType === 'unread' ? 'bg-[var(--color-primary)] text-white shadow-xs' : 'bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        Ungelesen ({unreadCount})
      </button>
      <button
        type="button"
        onclick={() => filterType = 'circadian'}
        class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer {filterType === 'circadian' ? 'bg-[var(--color-primary)] text-white shadow-xs' : 'bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        Zirkadian
      </button>
      <button
        type="button"
        onclick={() => filterType = 'medication'}
        class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer {filterType === 'medication' ? 'bg-[var(--color-primary)] text-white shadow-xs' : 'bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        Medikation
      </button>
    </div>

    <!-- Notifications List -->
    <div class="space-y-2.5 overflow-y-auto flex-1 pr-1">
      {#if filteredList.length === 0}
        <div class="p-8 text-center text-xs text-[var(--text-muted)]">
          Keine Mitteilungen für diesen Filter vorhanden.
        </div>
      {:else}
        {#each filteredList as n (n.id)}
          {@const conf = typeConfig[n.type]}
          <div
            class="bg-[var(--bg-surface-0)] border rounded-2xl p-4 shadow-xs flex flex-col gap-2 transition-all hover:border-[var(--border-strong)] animate-slide-up {n.read ? 'border-[var(--border-subtle)] opacity-75' : 'border-l-4 border-l-[var(--color-primary)] border-[var(--border-subtle)]'}"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2">
                <span class="text-[0.6875rem] font-bold text-[var(--text-muted)]">{conf.label}</span>
                <span class="text-[0.625rem] text-[var(--text-soft)] tabular-nums">&bull; {n.time}</span>
              </div>
              <div class="flex items-center gap-1">
                <button
                  type="button"
                  onclick={() => toggleRead(n.id)}
                  class="text-[0.6875rem] font-bold text-[var(--text-muted)] hover:text-[var(--color-primary)] cursor-pointer px-1.5 py-0.5 rounded-lg hover:bg-[var(--bg-surface-50)]"
                  title={n.read ? 'Als ungelesen markieren' : 'Als gelesen markieren'}
                >
                  {n.read ? 'Ungelesen' : 'Gelesen'}
                </button>
                <button
                  type="button"
                  onclick={() => removeNotification(n.id)}
                  class="text-[var(--text-soft)] hover:text-rose-500 cursor-pointer p-0.5 text-sm leading-none"
                  title="Mitteilung löschen"
                >
                  &times;
                </button>
              </div>
            </div>

            <div>
              <h3 class="text-xs font-extrabold text-[var(--text-main)] leading-snug">{n.title}</h3>
              <p class="text-xs text-[var(--text-muted)] mt-1 leading-relaxed">{n.desc}</p>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  </div>
{/if}
