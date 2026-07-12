<script lang="ts">
  import { page } from '$app/stores';
  import { auth } from '$stores/auth.svelte';
  import { db } from '$lib/db/database';
  import { liveQuery } from 'dexie';
  import { slide, fly, fade } from 'svelte/transition';
  import NavDropdown from '$components/ui/NavDropdown.svelte';
  import UserMenu from '$components/ui/UserMenu.svelte';
  import NotificationBell from '$components/feedback/NotificationBell.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';

  const navLinks = [
    { href: '/', icon: 'dashboard', label: 'Dashboard' },
    { href: '/entries', icon: 'receipt-long', label: 'Logbook' },
  ];

  const workoutItemsBase = [
    { href: '/workouts', icon: 'fitness-center', label: 'Overview' },
    { href: '/workouts/plans', icon: 'assignment', label: 'Plans' },
    { href: '/workouts/exercises', icon: 'exercise', label: 'Exercises' },
    { href: '/workouts/sessions', icon: 'history', label: 'Sessions' },
  ];

  const activeSession = liveQuery(() =>
    db.workout_session.filter((s) => !s.deleted_at && !s.completed_at).first(),
  );
  let hasActiveSession = $derived($activeSession != null);

  let workoutItems = $derived(
    hasActiveSession
      ? [...workoutItemsBase, { href: '/workouts/active', icon: 'play-circle', label: 'Active Session', highlight: true as const }]
      : workoutItemsBase
  );

  const coachItems = [
    { href: '/coach/circadian', icon: 'routine', label: 'Circadian' },
    { href: '/coach/chat', icon: 'psychology', label: 'Chat' },
  ];

  const communityItems = [
    { href: '/community/feed', icon: 'rss-feed', label: 'Feed' },
    { href: '/community/leaderboard', icon: 'leaderboard', label: 'Leaderboard' },
    { href: '/community/connections', icon: 'groups', label: 'Connections' },
    { href: '/community/access-log', icon: 'history', label: 'Access Log' },
  ];

  let mobileOpen = $state(false);

  function navLinkClass(link: { href: string }) {
    const active = $page.url.pathname === link.href;
    return 'flex h-full items-center border-b-2 px-4 text-[13px] font-semibold tracking-[0.05em] no-underline transition-colors duration-150 ' +
      (active ? 'border-primary-500 text-primary-600' : 'border-transparent text-surface-600 hover:text-primary-600');
  }

  // --- Mobile menu ---
  interface NavLink { type: 'link'; href: string; icon: string; label: string; highlight?: boolean }
  interface NavGroup { type: 'group'; label: string; icon: string; items: NavLink[] }
  type NavEntry = NavLink | NavGroup;

  const baseMobileNav: NavEntry[] = [
    { type: 'link', href: '/', icon: 'dashboard', label: 'Dashboard' },
    { type: 'link', href: '/entries', icon: 'receipt-long', label: 'Logbook' },
    { type: 'link', href: '/analytics', icon: 'insights', label: 'Analytics' },
    { type: 'link', href: '/goals', icon: 'track-changes', label: 'Goals' },
    {
      type: 'group', label: 'Workouts', icon: 'fitness-center',
      items: [
        { type: 'link', href: '/workouts', icon: 'fitness-center', label: 'Overview' },
        { type: 'link', href: '/workouts/plans', icon: 'assignment', label: 'Plans' },
        { type: 'link', href: '/workouts/exercises', icon: 'exercise', label: 'Exercises' },
        { type: 'link', href: '/workouts/sessions', icon: 'history', label: 'Sessions' },
      ],
    },
    {
      type: 'group', label: 'Coach', icon: 'psychology',
      items: [
        { type: 'link', href: '/coach/circadian', icon: 'routine', label: 'Circadian' },
        { type: 'link', href: '/coach/chat', icon: 'psychology', label: 'Chat' },
      ],
    },
    {
      type: 'group', label: 'Community', icon: 'share',
      items: [
        { type: 'link', href: '/community/feed', icon: 'rss-feed', label: 'Feed' },
        { type: 'link', href: '/community/leaderboard', icon: 'leaderboard', label: 'Leaderboard' },
        { type: 'link', href: '/community/connections', icon: 'groups', label: 'Connections' },
        { type: 'link', href: '/community/access-log', icon: 'history', label: 'Access Log' },
      ],
    },
    { type: 'link', href: '/settings', icon: 'settings', label: 'Settings' },
  ];

  let mobileNav = $derived.by(() => {
    const nav = [...baseMobileNav];
    if (hasActiveSession) {
      const idx = nav.findIndex((e) => e.type === 'group' && e.label === 'Workouts');
      if (idx >= 0) {
        const group = nav[idx] as NavGroup;
        nav[idx] = { ...group, items: [...group.items, { type: 'link', href: '/workouts/active', icon: 'play-circle', label: 'Active Session', highlight: true }] };
      }
    }
    if (auth.isAdmin) {
      nav.push({ type: 'link', href: '/admin', icon: 'admin-panel-settings', label: 'Admin' });
    }
    return nav;
  });

  let expandedGroups = $state<Set<string>>(new Set());

  function isGroupActive(group: NavGroup): boolean {
    return group.items.some((item) => {
      const p = $page.url.pathname;
      return p === item.href || p.startsWith(item.href + '/');
    });
  }

  function toggleGroup(label: string) {
    const next = new Set(expandedGroups);
    if (next.has(label)) next.delete(label);
    else next.add(label);
    expandedGroups = next;
  }

  $effect(() => {
    $page.url.pathname;
    for (const entry of mobileNav) {
      if (entry.type === 'group' && isGroupActive(entry) && !expandedGroups.has(entry.label)) {
        const next = new Set(expandedGroups);
        next.add(entry.label);
        expandedGroups = next;
      }
    }
  });

  function isLinkActive(href: string): boolean {
    const p = $page.url.pathname;
    return p === href || (p.startsWith(href + '/') && href !== '/');
  }
</script>

<header class="sticky top-0 z-200 h-16 border-b border-surface-200 bg-surface-0" data-scrolled>
  <div class="mx-auto flex h-full max-w-[1440px] items-center gap-6 px-6">
    <a href="/" class="text-xl font-semibold leading-7 -track-[0.01em] text-primary-600 no-underline shrink-0">
      salus
    </a>

    <nav class="hidden h-full items-center gap-0 lg:flex" style="margin-left: 32px;">
      {#each navLinks as link}
        <a href={link.href} class={navLinkClass(link)} aria-current={$page.url.pathname === link.href ? 'page' : undefined}>
          {link.label}
        </a>
      {/each}

      <a href="/analytics" class={navLinkClass({ href: '/analytics' })} aria-current={$page.url.pathname === '/analytics' ? 'page' : undefined}>
        Analytics
      </a>
      <a href="/goals" class={navLinkClass({ href: '/goals' })} aria-current={$page.url.pathname === '/goals' ? 'page' : undefined}>
        Goals
      </a>

      <NavDropdown label="Workouts" items={workoutItems} />
      <NavDropdown label="Coach" items={coachItems} />
      <NavDropdown label="Community" items={communityItems} />
    </nav>

    <div class="flex-1"></div>

    <div class="flex items-center gap-2">
      {#if auth.isAuthenticated}
        <NotificationBell />
        <UserMenu />
        <button
          class="flex h-9 w-9 items-center justify-center rounded-md text-surface-600 hover:bg-surface-100 hover:text-surface-900 lg:hidden"
          aria-label="Toggle navigation"
          aria-expanded={mobileOpen}
          onclick={() => (mobileOpen = !mobileOpen)}
        >
          <Icon name={mobileOpen ? 'close' : 'menu'} size="lg" />
        </button>
      {:else}
        <Btn href="/auth/login" variant="secondary">Sign In</Btn>
      {/if}
    </div>
  </div>
</header>

{#if mobileOpen && auth.isAuthenticated}
  <div
    class="fixed inset-0 z-300 bg-surface-900/30 lg:hidden"
    onclick={() => (mobileOpen = false)}
    onkeydown={(e) => { if (e.key === 'Escape') mobileOpen = false; }}
    role="dialog" aria-modal="true" tabindex="-1"
    transition:fade={{ duration: 150 }}
  ></div>
  <div class="fixed left-0 top-0 bottom-0 z-400 w-[280px] bg-surface-0 shadow-xl lg:hidden" transition:fly={{ x: -280, duration: 250 }}>
    <div class="flex h-16 items-center justify-between border-b border-surface-200 px-4">
      <h2 class="text-xl font-semibold text-surface-900">Navigation</h2>
      <button
        class="flex h-9 w-9 items-center justify-center rounded-full text-surface-500 hover:bg-surface-100 hover:text-surface-700"
        onclick={() => (mobileOpen = false)} aria-label="Close navigation"
      >
        <Icon name="close" />
      </button>
    </div>
    <div class="overflow-y-auto p-2">
      {#each mobileNav as entry}
        {#if entry.type === 'link'}
          {@const active = isLinkActive(entry.href)}
          <a
            href={entry.href}
            class="flex items-center gap-3 rounded-md px-4 py-3 text-[13px] font-semibold tracking-[0.05em] no-underline transition-colors duration-150 hover:bg-surface-50 {entry.highlight ? 'text-success-600' : active ? 'bg-primary-50 text-primary-600' : 'text-surface-600'}"
            aria-current={active ? 'page' : undefined}
            onclick={() => (mobileOpen = false)}
          >
            {#if entry.highlight}
              <span class="inline-block h-2 w-2 shrink-0 rounded-full bg-success-500 animate-pulse"></span>
            {/if}
            <Icon name={entry.icon} size="md" class={entry.highlight ? 'text-success-500' : ''} />
            {entry.label}
          </a>
        {:else}
          {@const expanded = expandedGroups.has(entry.label)}
          {@const groupHasActive = isGroupActive(entry)}
          <button
            type="button"
            class="flex w-full items-center gap-3 rounded-md px-4 py-3 text-[13px] font-semibold tracking-[0.05em] text-surface-600 transition-colors duration-150 hover:bg-surface-50"
            onclick={() => toggleGroup(entry.label)}
            aria-expanded={expanded}
          >
            <Icon name={entry.icon} size="md" />
            {entry.label}
            {#if groupHasActive && !expanded}
              <span class="ml-auto h-2 w-2 rounded-full bg-primary-500"></span>
            {/if}
            <Icon name="expand-more" size="sm" class="ml-auto transition-transform duration-150 {expanded ? 'rotate-180' : ''}" />
          </button>
          {#if expanded}
            <div class="overflow-hidden" transition:slide={{ duration: 200 }}>
              {#each entry.items as subItem}
                {@const active = isLinkActive(subItem.href)}
                <a
                  href={subItem.href}
                  class="flex items-center gap-3 rounded-md py-2.5 pl-8 pr-4 text-[13px] font-medium tracking-[0.05em] no-underline transition-colors duration-150 hover:bg-surface-50 {subItem.highlight ? 'text-success-600' : active ? 'bg-primary-50 text-primary-600' : 'text-surface-500'}"
                  aria-current={active ? 'page' : undefined}
                  onclick={() => (mobileOpen = false)}
                >
                  {#if subItem.highlight}
                    <span class="inline-block h-2 w-2 shrink-0 rounded-full bg-success-500 animate-pulse"></span>
                  {:else}
                    <Icon name={subItem.icon} size="sm" class="text-surface-400" />
                  {/if}
                  {subItem.label}
                </a>
              {/each}
            </div>
          {/if}
        {/if}
      {/each}
    </div>
  </div>
{/if}
