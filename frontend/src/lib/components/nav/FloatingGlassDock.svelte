<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import FlyoutTrackDeck from './FlyoutTrackDeck.svelte';
  import FlyoutLabsDeck from './FlyoutLabsDeck.svelte';
  import FlyoutCommunityDeck from './FlyoutCommunityDeck.svelte';
  import FlyoutInsightsDeck from './FlyoutInsightsDeck.svelte';
  import UserProfileDropdown from './UserProfileDropdown.svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { theme } from '$stores/theme.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  let { onopenquicklog, onopennotifications, onopencmdk, onopenonboarding } = $props<{
    onopenquicklog?: () => void;
    onopennotifications?: () => void;
    onopencmdk?: () => void;
    onopenonboarding?: () => void;
  }>();

  let openDeck = $state<'track' | 'labs' | 'community' | 'insights' | null>(null);
  let isProfileOpen = $state(false);
  let isMobileActionHubOpen = $state(false);

  const currentPath = $derived(page.url.pathname);

  const userProfilesQuery = useQuery(() => db.user_profile.toArray());
  const userProfiles = $derived(userProfilesQuery.value);
  let userProfile = $derived(
    userProfiles && (userProfiles ?? []).length > 0 ? userProfiles[0] : null
  );

  let displayName = $derived(
    userProfile?.display_name || userProfile?.username || 'Philipp Fleischer'
  );
  let email = $derived(userProfile?.email || 'philipp@salus.local');
  let initial = $derived(displayName.charAt(0).toUpperCase());

  function toggleDeck(deck: 'track' | 'labs' | 'community' | 'insights') {
    isProfileOpen = false;
    isMobileActionHubOpen = false;
    openDeck = openDeck === deck ? null : deck;
  }

  function toggleProfile() {
    openDeck = null;
    isMobileActionHubOpen = false;
    isProfileOpen = !isProfileOpen;
  }

  function toggleMobileActionHub() {
    openDeck = null;
    isProfileOpen = false;
    isMobileActionHubOpen = !isMobileActionHubOpen;
  }

  function navigateTo(path: string) {
    goto(path);
    closeAll();
  }

  function closeAll() {
    openDeck = null;
    isProfileOpen = false;
    isMobileActionHubOpen = false;
  }

  function toggleTheme() {
    theme.toggle();
  }
</script>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- 1. DESKTOP FLOATING CAPSULE DOCK (Sticky Top on Desktop >= 768px)   -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div
  class="pointer-events-none sticky top-4 z-50 mb-2 hidden justify-center px-4 transition-all md:flex"
>
  <!-- Anchor frame for Desktop Dock Pill + Dropdowns -->
  <div class="pointer-events-auto relative flex w-auto justify-center">
    <!-- ─── THE DOCK PILL (has its own glass-panel) ─── -->
    <div
      class="glass-panel flex items-center gap-2 rounded-full px-3 py-1.5 shadow-dock transition-all"
    >
      <!-- Brand -->
      <button
        type="button"
        onclick={() => navigateTo('/')}
        class="flex cursor-pointer items-center gap-2 rounded-full px-3 py-1.5 text-base font-extrabold tracking-tight text-text-main transition-colors hover:bg-surface-50"
      >
        <div
          class="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-xs font-extrabold text-white"
        >
          S
        </div>
        <span>salus</span>
      </button>

      <!-- 5 Primary Navigation Pillars -->
      <nav
        class="flex items-center gap-1 rounded-full border border-border-subtle bg-surface-50 p-[3px]"
      >
        <!-- 1. Dashboard -->
        <button
          type="button"
          onclick={() => navigateTo('/')}
          class="flex cursor-pointer items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[0.8125rem] font-semibold transition-all {currentPath ===
          '/'
            ? 'bg-surface-0 font-bold text-primary shadow-sm'
            : 'text-text-muted hover:text-text-main'}"
        >
          <Icon name="dashboard" size="sm" />
          <span>Dashboard</span>
        </button>

        <!-- 2. Track (Flyout) -->
        <button
          type="button"
          onclick={() => toggleDeck('track')}
          class="flex cursor-pointer items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[0.8125rem] font-semibold transition-all {currentPath.startsWith(
            '/workouts'
          ) ||
          currentPath.startsWith('/food') ||
          currentPath.startsWith('/fasting') ||
          currentPath.startsWith('/habits') ||
          currentPath.startsWith('/journal') ||
          openDeck === 'track'
            ? 'bg-surface-0 font-bold text-primary shadow-sm'
            : 'text-text-muted hover:text-text-main'}"
        >
          <Icon name="fitness-center" size="sm" />
          <span>Track</span>
          <Icon
            name="expand-more"
            size="sm"
            class="inline-block opacity-50 transition-transform {openDeck === 'track'
              ? 'rotate-180'
              : ''}"
          />
        </button>

        <!-- 3. Klinik (Flyout) -->
        <button
          type="button"
          onclick={() => toggleDeck('labs')}
          class="flex cursor-pointer items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[0.8125rem] font-semibold transition-all {currentPath.startsWith(
            '/entries'
          ) ||
          currentPath.startsWith('/labs') ||
          currentPath.startsWith('/medications') ||
          currentPath.startsWith('/goals') ||
          openDeck === 'labs'
            ? 'bg-surface-0 font-bold text-primary shadow-sm'
            : 'text-text-muted hover:text-text-main'}"
        >
          <Icon name="science" size="sm" />
          <span>Klinik</span>
          <Icon
            name="expand-more"
            size="sm"
            class="inline-block opacity-50 transition-transform {openDeck === 'labs'
              ? 'rotate-180'
              : ''}"
          />
        </button>

        <!-- 4. Community (Flyout) -->
        <button
          type="button"
          onclick={() => toggleDeck('community')}
          class="flex cursor-pointer items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[0.8125rem] font-semibold transition-all {currentPath.startsWith(
            '/community'
          ) || openDeck === 'community'
            ? 'bg-surface-0 font-bold text-primary shadow-sm'
            : 'text-text-muted hover:text-text-main'}"
        >
          <Icon name="groups" size="sm" />
          <span>Community</span>
          <Icon
            name="expand-more"
            size="sm"
            class="inline-block opacity-50 transition-transform {openDeck === 'community'
              ? 'rotate-180'
              : ''}"
          />
        </button>

        <!-- 5. Insights (Flyout) -->
        <button
          type="button"
          onclick={() => toggleDeck('insights')}
          class="flex cursor-pointer items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[0.8125rem] font-semibold transition-all {currentPath.startsWith(
            '/analytics'
          ) ||
          currentPath.startsWith('/coach') ||
          currentPath.startsWith('/achievements') ||
          openDeck === 'insights'
            ? 'bg-surface-0 font-bold text-primary shadow-sm'
            : 'text-text-muted hover:text-text-main'}"
        >
          <Icon name="insights" size="sm" />
          <span>Insights</span>
          <Icon
            name="expand-more"
            size="sm"
            class="inline-block opacity-50 transition-transform {openDeck === 'insights'
              ? 'rotate-180'
              : ''}"
          />
        </button>
      </nav>

      <!-- Desktop Action Buttons -->
      <div class="ml-1 flex items-center gap-1.5">
        <button
          type="button"
          onclick={onopencmdk}
          class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-border-subtle bg-surface-50 text-text-muted transition-colors hover:text-text-main"
          title="Spotlight (Cmd+K)"
        >
          <Icon name="search" size="sm" />
        </button>

        <button
          type="button"
          onclick={onopennotifications}
          class="relative flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-border-subtle bg-surface-50 text-text-muted transition-colors hover:text-text-main"
          title="Mitteilungen"
        >
          <Icon name="notifications" size="sm" />
        </button>

        <button
          type="button"
          onclick={toggleTheme}
          class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-border-subtle bg-surface-50 text-text-muted transition-colors hover:text-text-main"
          title="Theme wechseln"
        >
          <Icon name="dark-mode" size="sm" />
        </button>

        <button
          type="button"
          onclick={onopenquicklog}
          class="flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-full bg-primary text-white shadow-sm transition-all hover:scale-105 hover:opacity-90 active:scale-95"
          title="Schnellerfassung (1-Tap Log)"
          aria-label="Schnellerfassung (1-Tap Log)"
        >
          <Icon name="add" size="sm" />
        </button>

        <!-- Desktop Avatar Button -->
        <button
          type="button"
          onclick={toggleProfile}
          class="relative ml-0.5 flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-white/20 bg-gradient-to-tr from-primary to-activity text-xs font-black text-white shadow-xs transition-all hover:scale-105"
          title="Profil und Kontoverwaltung"
        >
          <span>{initial}</span>
          <span
            class="absolute -right-0.5 -bottom-0.5 h-2.5 w-2.5 rounded-full border-2 border-canvas bg-emerald-500"
          ></span>
        </button>
      </div>
    </div>

    <!-- Desktop Dropdown (Anchored to right edge of dock pill) -->
    {#if isProfileOpen}
      <div class="fixed inset-0 z-50 bg-transparent" onclick={closeAll} role="presentation"></div>

      <div class="pointer-events-auto absolute top-14 right-0 z-51">
        <UserProfileDropdown
          onnavigate={navigateTo}
          onopenonboarding={() => onopenonboarding?.()}
          onclose={() => (isProfileOpen = false)}
        />
      </div>
    {/if}

    <!-- Desktop Flyout Sub-Decks (Centered under dock pill) -->
    {#if openDeck}
      <div class="fixed inset-0 z-45 bg-transparent" onclick={closeAll} role="presentation"></div>

      <div
        class="glass-panel animate-modal-pop pointer-events-auto absolute top-14 left-1/2 z-46 w-[860px] -translate-x-1/2 rounded-2xl p-5 shadow-dock transition-all duration-300"
      >
        {#if openDeck === 'track'}
          <FlyoutTrackDeck onselect={navigateTo} />
        {:else if openDeck === 'labs'}
          <FlyoutLabsDeck onselect={navigateTo} />
        {:else if openDeck === 'community'}
          <FlyoutCommunityDeck onselect={navigateTo} />
        {:else if openDeck === 'insights'}
          <FlyoutInsightsDeck onselect={navigateTo} />
        {/if}
      </div>
    {/if}
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- 2. MOBILE FLOATING GLASS DOCK WITH CENTER ACTION HUB               -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div class="pointer-events-none fixed inset-x-3 bottom-3 z-45 flex justify-center md:hidden">
  <div
    class="glass-panel pointer-events-auto mx-auto flex w-full max-w-sm items-center justify-around rounded-full px-2.5 py-1.5 shadow-dock"
  >
    <!-- 1. Dashboard -->
    <button
      type="button"
      onclick={() => navigateTo('/')}
      class="flex h-12 w-12 cursor-pointer flex-col items-center justify-center rounded-full transition-all {currentPath ===
      '/'
        ? 'bg-primary-soft font-bold text-primary'
        : 'text-text-muted active:text-text-main'}"
      title="Dashboard"
      aria-label="Dashboard"
    >
      <Icon name="dashboard" size="md" />
      <span class="mt-0.5 text-[0.625rem] font-semibold">Home</span>
    </button>

    <!-- 2. Track -->
    <button
      type="button"
      onclick={() => toggleDeck('track')}
      class="flex h-12 w-12 cursor-pointer flex-col items-center justify-center rounded-full transition-all {currentPath.startsWith(
        '/workouts'
      ) ||
      currentPath.startsWith('/food') ||
      currentPath.startsWith('/fasting') ||
      currentPath.startsWith('/habits') ||
      currentPath.startsWith('/journal') ||
      openDeck === 'track'
        ? 'bg-primary-soft font-bold text-primary'
        : 'text-text-muted active:text-text-main'}"
      title="Track"
      aria-label="Track Übersicht"
    >
      <Icon name="fitness-center" size="md" />
      <span class="mt-0.5 text-[0.625rem] font-semibold">Track</span>
    </button>

    <!-- 3. CENTER ACTION HUB BUTTON (Opens Quick Menu / Command Hub) -->
    <button
      type="button"
      onclick={toggleMobileActionHub}
      class="-my-2 flex h-12 w-12 cursor-pointer items-center justify-center rounded-full border-2 border-white/30 bg-gradient-to-tr from-primary to-blue-600 text-white shadow-lg shadow-blue-500/30 transition-all hover:scale-105 active:scale-95"
      title={isMobileActionHubOpen ? 'Schließen' : 'Aktionszentrale öffnen'}
      aria-label={isMobileActionHubOpen ? 'Schließen' : 'Aktionszentrale öffnen'}
    >
      {#if isMobileActionHubOpen}
        <Icon name="close" size="md" />
      {:else}
        <Icon name="apps" size="md" />
      {/if}
    </button>

    <!-- 4. Klinik -->
    <button
      type="button"
      onclick={() => toggleDeck('labs')}
      class="flex h-12 w-12 cursor-pointer flex-col items-center justify-center rounded-full transition-all {currentPath.startsWith(
        '/entries'
      ) ||
      currentPath.startsWith('/labs') ||
      currentPath.startsWith('/medications') ||
      currentPath.startsWith('/goals') ||
      openDeck === 'labs'
        ? 'bg-primary-soft font-bold text-primary'
        : 'text-text-muted active:text-text-main'}"
      title="Klinik"
      aria-label="Klinik & Labor"
    >
      <Icon name="science" size="md" />
      <span class="mt-0.5 text-[0.625rem] font-semibold">Klinik</span>
    </button>

    <!-- 5. Insights -->
    <button
      type="button"
      onclick={() => toggleDeck('insights')}
      class="flex h-12 w-12 cursor-pointer flex-col items-center justify-center rounded-full transition-all {currentPath.startsWith(
        '/analytics'
      ) ||
      currentPath.startsWith('/coach') ||
      currentPath.startsWith('/achievements') ||
      currentPath.startsWith('/community') ||
      openDeck === 'insights'
        ? 'bg-primary-soft font-bold text-primary'
        : 'text-text-muted active:text-text-main'}"
      title="Insights"
      aria-label="Insights & Analytik"
    >
      <Icon name="insights" size="md" />
      <span class="mt-0.5 text-[0.625rem] font-semibold">Insights</span>
    </button>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- 3. MOBILE CENTER ACTION HUB POPOVER (Replaces Top Bar)             -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
{#if isMobileActionHubOpen}
  <!-- Invisible Click Catcher -->
  <div
    class="fixed inset-0 z-48 bg-transparent md:hidden"
    onclick={closeAll}
    role="presentation"
  ></div>

  <!-- Action Hub Floating Frosted Glass Card -->
  <div
    class="glass-panel animate-modal-pop pointer-events-auto fixed inset-x-4 bottom-20 z-50 mx-auto max-w-sm space-y-3.5 rounded-3xl p-4 text-text-main shadow-2xl md:hidden"
  >
    <!-- Header: User Profile Card -->
    <div
      class="flex items-center justify-between rounded-2xl border border-border-subtle/70 bg-surface-50/60 p-3"
    >
      <div class="flex items-center gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-tr from-primary to-activity text-sm font-extrabold text-white shadow-xs"
        >
          {initial}
        </div>
        <div class="overflow-hidden">
          <span class="block truncate text-sm font-extrabold text-text-main">{displayName}</span>
          <span class="block truncate text-[0.6875rem] text-text-muted">{email}</span>
        </div>
      </div>

      <!-- Settings & Admin Shortcut Pills -->
      <div class="flex items-center gap-1">
        <button
          type="button"
          onclick={() => navigateTo('/settings')}
          class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-xl border border-border-subtle bg-surface-0 text-text-muted transition-colors hover:text-primary"
          title="Einstellungen"
        >
          <Icon name="settings" size="sm" />
        </button>
        {#if userProfile?.is_admin}
          <button
            type="button"
            onclick={() => navigateTo('/admin')}
            class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-xl border border-border-subtle bg-surface-0 text-text-muted transition-colors hover:text-vital"
            title="Administration"
          >
            <Icon name="admin-panel-settings" size="sm" />
          </button>
        {/if}
      </div>
    </div>

    <!-- Hero Primary Action: 1-Tap Quick-Log -->
    <button
      type="button"
      onclick={() => {
        onopenquicklog?.();
        isMobileActionHubOpen = false;
      }}
      class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-primary to-blue-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-blue-500/25 transition-all active:scale-98"
    >
      <Icon name="add" size="md" />
      <span>1-Tap Schnell erfassen</span>
    </button>

    <!-- Quick Utilities Toolbar: Search, Notifications, Theme, Tour -->
    <div class="grid grid-cols-4 gap-2 pt-1">
      <!-- 1. Search -->
      <button
        type="button"
        onclick={() => {
          onopencmdk?.();
          isMobileActionHubOpen = false;
        }}
        class="flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-border-subtle/70 bg-surface-50/50 p-2.5 text-xs text-text-muted transition-all hover:bg-surface-50 hover:text-text-main"
      >
        <Icon name="search" size="md" class="mb-1 text-primary" />
        <span class="text-[0.625rem] font-medium">Suche</span>
      </button>

      <!-- 2. Notifications -->
      <button
        type="button"
        onclick={() => {
          onopennotifications?.();
          isMobileActionHubOpen = false;
        }}
        class="relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-border-subtle/70 bg-surface-50/50 p-2.5 text-xs text-text-muted transition-all hover:bg-surface-50 hover:text-text-main"
      >
        <Icon name="notifications" size="md" class="mb-1 text-vital" />
        <span class="text-[0.625rem] font-medium">Mitteilungen</span>
      </button>

      <!-- 3. Theme Toggle -->
      <button
        type="button"
        onclick={() => {
          toggleTheme();
        }}
        class="flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-border-subtle/70 bg-surface-50/50 p-2.5 text-xs text-text-muted transition-all hover:bg-surface-50 hover:text-text-main"
      >
        <Icon name="dark-mode" size="md" class="mb-1 text-circadian" />
        <span class="text-[0.625rem] font-medium">Theme</span>
      </button>

      <!-- 4. Onboarding Tour -->
      <button
        type="button"
        onclick={() => {
          onopenonboarding?.();
          isMobileActionHubOpen = false;
        }}
        class="flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-border-subtle/70 bg-surface-50/50 p-2.5 text-xs text-text-muted transition-all hover:bg-surface-50 hover:text-text-main"
      >
        <Icon name="auto-awesome" size="md" class="mb-1 text-activity" />
        <span class="text-[0.625rem] font-medium">Tour</span>
      </button>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- 4. MOBILE FLYOUT SUB-DECKS (Slide up above Bottom Dock)             -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
{#if openDeck}
  <div
    class="fixed inset-0 z-45 bg-transparent md:hidden"
    onclick={closeAll}
    role="presentation"
  ></div>

  <div
    class="glass-panel animate-modal-pop pointer-events-auto fixed inset-x-3 bottom-20 z-46 max-h-[72vh] overflow-y-auto rounded-3xl p-4 shadow-dock transition-all sm:p-5 md:hidden"
  >
    {#if openDeck === 'track'}
      <FlyoutTrackDeck onselect={navigateTo} />
    {:else if openDeck === 'labs'}
      <FlyoutLabsDeck onselect={navigateTo} />
    {:else if openDeck === 'community'}
      <FlyoutCommunityDeck onselect={navigateTo} />
    {:else if openDeck === 'insights'}
      <FlyoutInsightsDeck onselect={navigateTo} />
    {/if}
  </div>
{/if}
