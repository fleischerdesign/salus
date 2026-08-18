<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Btn from '../ui/Btn.svelte';
  import FlyoutTrackDeck from './FlyoutTrackDeck.svelte';
  import FlyoutLabsDeck from './FlyoutLabsDeck.svelte';
  import FlyoutCommunityDeck from './FlyoutCommunityDeck.svelte';
  import FlyoutInsightsDeck from './FlyoutInsightsDeck.svelte';
  import UserProfileDropdown from './UserProfileDropdown.svelte';
  import type { PageId } from '../../types';

  let {
    activeView = 'dashboard',
    onnavigate,
    onopenquicklog,
    onopennotifications,
    ontoggletheme,
    onopencmdk,
    onopenonboarding
  } = $props<{
    activeView: PageId;
    onnavigate: (view: PageId) => void;
    onopenquicklog?: () => void;
    onopennotifications?: () => void;
    ontoggletheme?: () => void;
    onopencmdk?: () => void;
    onopenonboarding?: () => void;
  }>();

  let openDeck = $state<'track' | 'labs' | 'community' | 'insights' | null>(null);
  let isProfileOpen = $state(false);
  let isMobileActionHubOpen = $state(false);

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

  function handleSelect(view: PageId) {
    onnavigate(view);
    openDeck = null;
    isProfileOpen = false;
    isMobileActionHubOpen = false;
  }

  function closeAll() {
    openDeck = null;
    isProfileOpen = false;
    isMobileActionHubOpen = false;
  }
</script>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- 1. DESKTOP FLOATING CAPSULE DOCK (Sticky Top on Desktop >= 768px)   -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div class="hidden md:flex sticky top-6 z-50 justify-center pointer-events-none transition-all px-4">
  
  <!-- Anchor frame for Desktop Dock Pill + Dropdowns -->
  <div class="relative pointer-events-auto w-auto flex justify-center">
    
    <!-- ─── THE DOCK PILL (has its own glass-panel) ─── -->
    <div
      class="glass-panel rounded-full py-1.5 px-3 flex items-center gap-2 shadow-[var(--shadow-dock)] transition-all"
    >
      <!-- Brand -->
      <button
        type="button"
        onclick={() => handleSelect('dashboard')}
        class="flex items-center gap-2 px-3 py-1.5 font-extrabold text-base tracking-tight rounded-full hover:bg-[var(--bg-surface-50)] transition-colors cursor-pointer text-[var(--text-main)]"
      >
        <div class="w-6 h-6 rounded-full bg-[var(--color-primary)] text-white flex items-center justify-center font-extrabold text-xs">
          S
        </div>
        <span>salus</span>
      </button>

      <!-- 5 Primary Navigation Pillars -->
      <nav class="flex items-center gap-1 bg-[var(--bg-surface-50)] p-[3px] rounded-full border border-[var(--border-subtle)]">
        <!-- 1. Dashboard -->
        <button
          type="button"
          onclick={() => handleSelect('dashboard')}
          class="px-3.5 py-1.5 rounded-full text-[0.8125rem] font-semibold flex items-center gap-1.5 transition-all cursor-pointer {activeView === 'dashboard'
            ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm font-bold'
            : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        >
          <Icon name="sun" size={16} />
          <span>Dashboard</span>
        </button>

        <!-- 2. Track (Flyout) -->
        <button
          type="button"
          onclick={() => toggleDeck('track')}
          class="px-3.5 py-1.5 rounded-full text-[0.8125rem] font-semibold flex items-center gap-1.5 transition-all cursor-pointer {activeView.startsWith('workouts') || activeView.startsWith('food') || activeView === 'fasting' || activeView === 'habits' || activeView === 'journal' || openDeck === 'track'
            ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm font-bold'
            : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        >
          <Icon name="chart" size={16} />
          <span>Track</span>
          <Icon name="chevron-down" size={12} class="inline-block opacity-50 transition-transform {openDeck === 'track' ? 'rotate-180' : ''}" />
        </button>

        <!-- 3. Klinik (Flyout) -->
        <button
          type="button"
          onclick={() => toggleDeck('labs')}
          class="px-3.5 py-1.5 rounded-full text-[0.8125rem] font-semibold flex items-center gap-1.5 transition-all cursor-pointer {activeView.startsWith('metric') || activeView === 'labs' || activeView === 'medications' || activeView === 'goals' || openDeck === 'labs'
            ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm font-bold'
            : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        >
          <Icon name="labs" size={16} />
          <span>Klinik</span>
          <Icon name="chevron-down" size={12} class="inline-block opacity-50 transition-transform {openDeck === 'labs' ? 'rotate-180' : ''}" />
        </button>

        <!-- 4. Community (Flyout) -->
        <button
          type="button"
          onclick={() => toggleDeck('community')}
          class="px-3.5 py-1.5 rounded-full text-[0.8125rem] font-semibold flex items-center gap-1.5 transition-all cursor-pointer {activeView.startsWith('community') || activeView === 'open-science' || openDeck === 'community'
            ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm font-bold'
            : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        >
          <Icon name="labs" size={16} />
          <span>Community</span>
          <Icon name="chevron-down" size={12} class="inline-block opacity-50 transition-transform {openDeck === 'community' ? 'rotate-180' : ''}" />
        </button>

        <!-- 5. Insights (Flyout) -->
        <button
          type="button"
          onclick={() => toggleDeck('insights')}
          class="px-3.5 py-1.5 rounded-full text-[0.8125rem] font-semibold flex items-center gap-1.5 transition-all cursor-pointer {activeView === 'insights' || activeView === 'coach' || activeView === 'achievements' || openDeck === 'insights'
            ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm font-bold'
            : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
        >
          <Icon name="insights" size={16} />
          <span>Insights</span>
          <Icon name="chevron-down" size={12} class="inline-block opacity-50 transition-transform {openDeck === 'insights' ? 'rotate-180' : ''}" />
        </button>
      </nav>

      <!-- Desktop Action Buttons -->
      <div class="flex items-center gap-1.5 ml-1">
        <button
          type="button"
          onclick={onopencmdk}
          class="flex w-8 h-8 rounded-full items-center justify-center bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors cursor-pointer"
          title="Spotlight (Cmd+K)"
        >
          <Icon name="search" size={16} />
        </button>
        
        <button
          type="button"
          onclick={onopennotifications}
          class="relative flex w-8 h-8 rounded-full items-center justify-center bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors cursor-pointer"
          title="Mitteilungen"
        >
          <Icon name="sun" size={16} />
          <span class="absolute top-1 right-1 w-2 h-2 rounded-full bg-[var(--color-vital)]"></span>
        </button>

        <button
          type="button"
          onclick={ontoggletheme}
          class="flex w-8 h-8 rounded-full items-center justify-center bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors cursor-pointer"
          title="Theme wechseln"
        >
          <Icon name="moon" size={16} />
        </button>

        <Btn
          variant="primary"
          class="rounded-full !px-3.5 !py-1.5"
          onclick={onopenquicklog}
        >
          <Icon name="plus" size={16} />
          <span class="text-xs font-semibold">1-Tap Log</span>
        </Btn>

        <!-- Desktop Avatar Button -->
        <button
          type="button"
          onclick={toggleProfile}
          class="relative w-8 h-8 rounded-full bg-gradient-to-tr from-[var(--color-primary)] to-[var(--color-activity)] text-white font-black text-xs flex items-center justify-center cursor-pointer shadow-xs border border-white/20 hover:scale-105 transition-all ml-0.5"
          title="Profil und Kontoverwaltung"
        >
          <span>P</span>
          <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-[var(--bg-canvas)]"></span>
        </button>
      </div>
    </div>

    <!-- Desktop Dropdown (Anchored to right edge of dock pill) -->
    {#if isProfileOpen}
      <div
        class="fixed inset-0 z-50 bg-transparent"
        onclick={closeAll}
        role="presentation"
      ></div>

      <div class="pointer-events-auto absolute top-14 right-0 z-51">
        <UserProfileDropdown
          onnavigate={handleSelect}
          onopenonboarding={() => onopenonboarding?.()}
          onclose={() => isProfileOpen = false}
        />
      </div>
    {/if}

    <!-- Desktop Flyout Sub-Decks (Centered under dock pill) -->
    {#if openDeck}
      <div
        class="fixed inset-0 z-45 bg-transparent"
        onclick={closeAll}
        role="presentation"
      ></div>

      <div
        class="pointer-events-auto z-46 transition-all duration-300 absolute top-14 left-1/2 -translate-x-1/2 w-[860px] glass-panel rounded-2xl p-5 shadow-[var(--shadow-dock)] animate-modal-pop"
      >
        {#if openDeck === 'track'}
          <FlyoutTrackDeck onselect={handleSelect} />
        {:else if openDeck === 'labs'}
          <FlyoutLabsDeck onselect={handleSelect} />
        {:else if openDeck === 'community'}
          <FlyoutCommunityDeck onselect={handleSelect} />
        {:else if openDeck === 'insights'}
          <FlyoutInsightsDeck onselect={handleSelect} />
        {/if}
      </div>
    {/if}

  </div>
</div>


<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- 2. MOBILE FLOATING GLASS DOCK WITH CENTER ACTION HUB               -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div class="md:hidden fixed bottom-3 inset-x-3 z-45 flex justify-center pointer-events-none">
  <div
    class="pointer-events-auto glass-panel rounded-full px-2.5 py-1.5 flex items-center justify-around shadow-[var(--shadow-dock)] w-full max-w-sm mx-auto"
  >
    <!-- 1. Dashboard -->
    <button
      type="button"
      onclick={() => handleSelect('dashboard')}
      class="flex flex-col items-center justify-center w-12 h-12 rounded-full transition-all cursor-pointer {activeView === 'dashboard'
        ? 'text-[var(--color-primary)] bg-[var(--color-primary-soft)] font-bold'
        : 'text-[var(--text-muted)] active:text-[var(--text-main)]'}"
      title="Dashboard"
      aria-label="Dashboard"
    >
      <Icon name="sun" size={22} />
      <span class="text-[0.625rem] font-semibold mt-0.5">Home</span>
    </button>

    <!-- 2. Track -->
    <button
      type="button"
      onclick={() => toggleDeck('track')}
      class="flex flex-col items-center justify-center w-12 h-12 rounded-full transition-all cursor-pointer {activeView.startsWith('workouts') || activeView.startsWith('food') || activeView === 'fasting' || activeView === 'habits' || activeView === 'journal' || openDeck === 'track'
        ? 'text-[var(--color-primary)] bg-[var(--color-primary-soft)] font-bold'
        : 'text-[var(--text-muted)] active:text-[var(--text-main)]'}"
      title="Track"
      aria-label="Track Übersicht"
    >
      <Icon name="chart" size={22} />
      <span class="text-[0.625rem] font-semibold mt-0.5">Track</span>
    </button>

    <!-- 3. CENTER ACTION HUB BUTTON (Opens Quick Menu / Command Hub) -->
    <button
      type="button"
      onclick={toggleMobileActionHub}
      class="w-12 h-12 rounded-full bg-gradient-to-tr from-[var(--color-primary)] to-blue-600 text-white flex items-center justify-center shadow-lg shadow-blue-500/30 hover:scale-105 active:scale-95 transition-all cursor-pointer border-2 border-white/30 -my-2"
      title={isMobileActionHubOpen ? 'Schließen' : 'Aktionszentrale öffnen'}
      aria-label={isMobileActionHubOpen ? 'Schließen' : 'Aktionszentrale öffnen'}
    >
      {#if isMobileActionHubOpen}
        <Icon name="close" size={20} />
      {:else}
        <Icon name="apps" size={22} />
      {/if}
    </button>

    <!-- 4. Klinik -->
    <button
      type="button"
      onclick={() => toggleDeck('labs')}
      class="flex flex-col items-center justify-center w-12 h-12 rounded-full transition-all cursor-pointer {activeView.startsWith('metric') || activeView === 'labs' || activeView === 'medications' || activeView === 'goals' || openDeck === 'labs'
        ? 'text-[var(--color-primary)] bg-[var(--color-primary-soft)] font-bold'
        : 'text-[var(--text-muted)] active:text-[var(--text-main)]'}"
      title="Klinik"
      aria-label="Klinik & Labor"
    >
      <Icon name="labs" size={22} />
      <span class="text-[0.625rem] font-semibold mt-0.5">Klinik</span>
    </button>

    <!-- 5. Insights -->
    <button
      type="button"
      onclick={() => toggleDeck('insights')}
      class="flex flex-col items-center justify-center w-12 h-12 rounded-full transition-all cursor-pointer {activeView === 'insights' || activeView === 'coach' || activeView === 'achievements' || activeView.startsWith('community') || openDeck === 'insights'
        ? 'text-[var(--color-primary)] bg-[var(--color-primary-soft)] font-bold'
        : 'text-[var(--text-muted)] active:text-[var(--text-main)]'}"
      title="Insights"
      aria-label="Insights & Analytik"
    >
      <Icon name="insights" size={22} />
      <span class="text-[0.625rem] font-semibold mt-0.5">Insights</span>
    </button>
  </div>
</div>


<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- 3. MOBILE CENTER ACTION HUB POPOVER (Replaces Top Bar)             -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
{#if isMobileActionHubOpen}
  <!-- Invisible Click Catcher -->
  <div
    class="md:hidden fixed inset-0 z-48 bg-transparent"
    onclick={closeAll}
    role="presentation"
  ></div>

  <!-- Action Hub Floating Frosted Glass Card -->
  <div
    class="md:hidden pointer-events-auto fixed bottom-20 inset-x-4 max-w-sm mx-auto z-50 glass-panel rounded-3xl p-4 shadow-2xl space-y-3.5 animate-modal-pop text-[var(--text-main)]"
  >
    <!-- Header: User Profile Card -->
    <div class="p-3 bg-[var(--bg-surface-50)]/60 border border-[var(--border-subtle)]/70 rounded-2xl flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-[var(--color-primary)] to-[var(--color-activity)] text-white font-extrabold text-sm flex items-center justify-center shadow-xs shrink-0">
          P
        </div>
        <div class="overflow-hidden">
          <span class="font-extrabold text-sm text-[var(--text-main)] truncate block">Philipp Fleischer</span>
          <span class="text-[0.6875rem] text-[var(--text-muted)] truncate block">philipp@salus.local</span>
        </div>
      </div>

      <!-- Settings & Admin Shortcut Pills -->
      <div class="flex items-center gap-1">
        <button
          type="button"
          onclick={() => handleSelect('settings')}
          class="w-8 h-8 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--color-primary)] transition-colors cursor-pointer"
          title="Einstellungen"
        >
          <Icon name="sun" size={16} />
        </button>
        <button
          type="button"
          onclick={() => handleSelect('admin')}
          class="w-8 h-8 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--color-vital)] transition-colors cursor-pointer"
          title="Administration"
        >
          <Icon name="labs" size={16} />
        </button>
      </div>
    </div>

    <!-- Hero Primary Action: 1-Tap Quick-Log -->
    <button
      type="button"
      onclick={() => { onopenquicklog?.(); isMobileActionHubOpen = false; }}
      class="w-full py-3 px-4 rounded-2xl bg-gradient-to-r from-[var(--color-primary)] to-blue-600 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-blue-500/25 active:scale-98 transition-all cursor-pointer"
    >
      <Icon name="plus" size={18} />
      <span>1-Tap Schnell erfassen</span>
    </button>

    <!-- Quick Utilities Toolbar: Search, Notifications, Theme, Tour -->
    <div class="grid grid-cols-4 gap-2 pt-1">
      <!-- 1. Search -->
      <button
        type="button"
        onclick={() => { onopencmdk?.(); isMobileActionHubOpen = false; }}
        class="flex flex-col items-center justify-center p-2.5 rounded-2xl bg-[var(--bg-surface-50)]/50 hover:bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]/70 transition-all cursor-pointer text-xs text-[var(--text-muted)] hover:text-[var(--text-main)]"
      >
        <Icon name="search" size={18} class="mb-1 text-[var(--color-primary)]" />
        <span class="text-[0.625rem] font-medium">Suche</span>
      </button>

      <!-- 2. Notifications -->
      <button
        type="button"
        onclick={() => { onopennotifications?.(); isMobileActionHubOpen = false; }}
        class="relative flex flex-col items-center justify-center p-2.5 rounded-2xl bg-[var(--bg-surface-50)]/50 hover:bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]/70 transition-all cursor-pointer text-xs text-[var(--text-muted)] hover:text-[var(--text-main)]"
      >
        <Icon name="sun" size={18} class="mb-1 text-[var(--color-vital)]" />
        <span class="absolute top-2 right-4 w-2 h-2 rounded-full bg-[var(--color-vital)]"></span>
        <span class="text-[0.625rem] font-medium">Mitteilungen</span>
      </button>

      <!-- 3. Theme Toggle -->
      <button
        type="button"
        onclick={() => { ontoggletheme?.(); }}
        class="flex flex-col items-center justify-center p-2.5 rounded-2xl bg-[var(--bg-surface-50)]/50 hover:bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]/70 transition-all cursor-pointer text-xs text-[var(--text-muted)] hover:text-[var(--text-main)]"
      >
        <Icon name="moon" size={18} class="mb-1 text-[var(--color-circadian)]" />
        <span class="text-[0.625rem] font-medium">Theme</span>
      </button>

      <!-- 4. Onboarding Tour -->
      <button
        type="button"
        onclick={() => { onopenonboarding?.(); isMobileActionHubOpen = false; }}
        class="flex flex-col items-center justify-center p-2.5 rounded-2xl bg-[var(--bg-surface-50)]/50 hover:bg-[var(--bg-surface-50)] border border-[var(--border-subtle)]/70 transition-all cursor-pointer text-xs text-[var(--text-muted)] hover:text-[var(--text-main)]"
      >
        <Icon name="sparkles" size={18} class="mb-1 text-[var(--color-activity)]" />
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
    class="md:hidden fixed inset-0 z-45 bg-transparent"
    onclick={closeAll}
    role="presentation"
  ></div>

  <div
    class="md:hidden pointer-events-auto z-46 transition-all fixed bottom-20 inset-x-3 max-h-[72vh] overflow-y-auto glass-panel rounded-3xl p-4 sm:p-5 shadow-[var(--shadow-dock)] animate-modal-pop"
  >
    {#if openDeck === 'track'}
      <FlyoutTrackDeck onselect={handleSelect} />
    {:else if openDeck === 'labs'}
      <FlyoutLabsDeck onselect={handleSelect} />
    {:else if openDeck === 'community'}
      <FlyoutCommunityDeck onselect={handleSelect} />
    {:else if openDeck === 'insights'}
      <FlyoutInsightsDeck onselect={handleSelect} />
    {/if}
  </div>
{/if}
