<script lang="ts">
  import '../app.css';
  import '@fontsource/manrope/400.css';
  import '@fontsource/manrope/500.css';
  import '@fontsource/manrope/600.css';
  import '@fontsource/manrope/700.css';
  import '@fontsource/manrope/800.css';
  import { addCollection } from '@iconify/svelte/dist/offline-functions.js';
  import icons from '$lib/icons.json';
  import { AUTH_USER_KEY } from '$lib/constants';
  addCollection(icons);
  import { auth } from '$stores/auth.svelte';
  import { db } from '$lib/db/database';
  import { setLocaleState } from '$lib/api/headers';
  import { onMount } from 'svelte';
  import { on } from 'svelte/events';
  import Icon from '$components/ui/Icon.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import { page } from '$app/state';
  import { beforeNavigate, goto } from '$app/navigation';
  import { useOffline } from '$lib/db/use-offline.svelte';
  import FloatingGlassDock from '$components/nav/FloatingGlassDock.svelte';
  import QuickLogModal from '$components/modals/QuickLogModal.svelte';
  import CommandPalette from '$components/modals/CommandPalette.svelte';
  import NotificationDrawer from '$components/layout/NotificationDrawer.svelte';
  import OnboardingModal from '$components/onboarding/OnboardingModal.svelte';
  import PageTransition from '$components/ui/PageTransition.svelte';
  import Toast from '$components/ui/Toast.svelte';
  import ConflictResolver from '$components/feedback/ConflictResolver.svelte';
  import { syncEngine } from '$lib/db/sync-engine.svelte';
  import { updateService } from '$lib/stores/update.svelte';
  import { getSystemStats } from '$lib/db/metric-stats';
  import { startBackgroundSync } from '$lib/native/background-sync';
  import { reportDeviceSourceStatus } from '$lib/sources';
  import { nativeBridge } from '$lib/native/bridge';
  import { biometricLock } from '$lib/native/biometric-lock.svelte';
  import { seedReferenceData } from '$lib/db/seed';
  import { localMode, SERVER_ONLY_PATH_PREFIXES } from '$lib/db/local-mode.svelte';
  import { theme } from '$stores/theme.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { setUserTimezone } from '$lib/utils/timezone';

  let { children } = $props();

  const publicPaths = ['/auth/login', '/auth/register'];
  let isPublic = $derived(publicPaths.includes(page.url.pathname));

  const userProfilesQuery = useQuery(() => db.user_profile.toArray());
  const userProfiles = $derived(userProfilesQuery.value);
  let userProfile = $derived(
    userProfiles && (userProfiles ?? []).length > 0 ? userProfiles[0] : null
  );

  $effect(() => {
    setUserTimezone(userProfile?.timezone);
  });

  $effect(() => {
    theme.apply();
  });

  function updateFocusState() {
    const activeEl = document.activeElement;
    const isInputFocused =
      activeEl &&
      (activeEl.tagName === 'INPUT' ||
        activeEl.tagName === 'TEXTAREA' ||
        activeEl.getAttribute('contenteditable') === 'true');
    updateService.setIsDirty(Boolean(isInputFocused));
  }

  function handleVisibilityChange() {
    if (document.visibilityState === 'hidden') {
      updateService.triggerSafeReload();
    } else if (document.visibilityState === 'visible') {
      biometricLock.enforce().catch(() => {});
    }
  }

  // ── Reactive Guards Integration for PWA Auto-Reload ──

  const activeSessionsQuery = useQuery(() =>
    db.workout_session
      .filter((s) => Boolean(s.started_at && !s.completed_at && !s.deleted_at))
      .toArray()
  );
  const activeSessions = $derived(activeSessionsQuery.value);
  $effect(() => {
    updateService.setActiveWorkout(Boolean(activeSessions && (activeSessions ?? []).length > 0));
  });

  $effect(() => {
    updateService.setIsSyncing(syncEngine.status !== 'idle');
  });

  // ── Auth bootstrap & SW Update Listener ──

  onMount(() => {
    seedReferenceData().catch(() => {});
    let stopBackgroundSync = () => {};

    if (!auth.token) {
      auth.setLoading(false);
      if (!isPublic) goto('/auth/login');
    } else {
      auth.setLoading(false);
      getSystemStats().catch(() => {});
      if (nativeBridge.isNative) {
        stopBackgroundSync = startBackgroundSync();
        reportDeviceSourceStatus().catch(() => {});
        biometricLock.enforce().catch(() => {});
      }
    }

    if (typeof navigator !== 'undefined' && 'serviceWorker' in navigator) {
      const off = on(navigator.serviceWorker, 'message', (event) => {
        if ((event as MessageEvent).data?.type === 'SALUS_UPDATE_AVAILABLE') {
          updateService.setUpdatePending(true);
        }
      });
      return () => {
        off();
        stopBackgroundSync();
      };
    }
    return stopBackgroundSync;
  });

  // ── Guarded Auto-Reload on Navigation or Backgrounding ──

  beforeNavigate(() => {
    updateService.triggerSafeReload();
  });

  $effect(() => {
    if (userProfile) {
      setLocaleState(userProfile.locale ?? 'en');
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(userProfile));
      localStorage.setItem('salus_user_is_admin', String(userProfile.is_admin ?? false));
      theme.applyUserProfile(userProfile);
    }
  });

  // ── Sync trigger — lazy token validation via sync pull ──

  let lastSyncKey = '';
  const sessionExpired = $derived(useOffline.sessionExpired);

  $effect(() => {
    if (
      localMode.active &&
      SERVER_ONLY_PATH_PREFIXES.some((p) => page.url.pathname.startsWith(p))
    ) {
      goto('/');
    }
  });

  $effect(() => {
    if (!auth.isAuthenticated) {
      lastSyncKey = '';
      return;
    }

    const key = `${localMode.active ? 'local' : 'server'}:${auth.token ?? ''}`;
    if (key !== lastSyncKey) {
      lastSyncKey = key;
      runSync();
    }
  });

  async function runSync() {
    await useOffline.syncAll();
    if (useOffline.sessionExpired) {
      useOffline.stopLiveSync();
      return;
    }
    syncEngine.flush().catch(() => {});
  }

  async function handleReauth() {
    useOffline.stopLiveSync();
    auth.clear();
    await goto('/auth/login');
  }

  // Global Modals State
  let isQuickLogOpen = $state(false);
  let isCmdKOpen = $state(false);
  let isNotificationsOpen = $state(false);
  let isOnboardingOpen = $state(false);

  function handleKeydown(e: KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      isCmdKOpen = !isCmdKOpen;
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<svelte:document
  onfocusin={updateFocusState}
  onfocusout={updateFocusState}
  onvisibilitychange={handleVisibilityChange}
/>

{#if isPublic}
  <div class="flex min-h-screen items-center justify-center bg-[var(--bg-canvas)] p-4">
    <PageTransition>{@render children()}</PageTransition>
  </div>
{:else if auth.isAuthenticated}
  <div
    class="relative flex min-h-screen flex-col bg-[var(--bg-canvas)] pb-32 text-[var(--text-main)] md:pb-16"
  >
    <!-- Floating Glass Navigation Dock (Desktop Sticky Capsule + Mobile Bottom Dock & Center Hub) -->
    <FloatingGlassDock
      onopenquicklog={() => (isQuickLogOpen = true)}
      onopennotifications={() => (isNotificationsOpen = true)}
      onopencmdk={() => (isCmdKOpen = true)}
      onopenonboarding={() => (isOnboardingOpen = true)}
    />

    {#if sessionExpired}
      <div class="mx-auto w-full max-w-[1440px] px-4 pt-4 md:px-10">
        <AlertBanner variant="warning" class="justify-between">
          <span class="flex flex-1 items-center justify-between gap-3">
            <span>Sitzung abgelaufen – melde dich erneut an, um zu synchronisieren.</span>
            <Btn variant="secondary" size="sm" onclick={handleReauth}>Neu anmelden</Btn>
          </span>
        </AlertBanner>
      </div>
    {/if}

    <main class="mx-auto w-full max-w-[1440px] flex-1 px-4 pt-4 pb-8 md:px-8 md:pt-6 md:pb-12">
      <PageTransition>{@render children()}</PageTransition>
    </main>

    <Toast />
    <ConflictResolver />

    <!-- Global Modals & Drawers -->
    <QuickLogModal open={isQuickLogOpen} onclose={() => (isQuickLogOpen = false)} />

    <CommandPalette open={isCmdKOpen} onclose={() => (isCmdKOpen = false)} />

    <NotificationDrawer open={isNotificationsOpen} onclose={() => (isNotificationsOpen = false)} />

    <OnboardingModal open={isOnboardingOpen} onclose={() => (isOnboardingOpen = false)} />
  </div>
  {#if biometricLock.locked}
    <!-- Biometric lock overlay -->
    <div
      class="bg-surface-0/85 fixed inset-0 z-[100] flex items-center justify-center backdrop-blur-sm"
    >
      <div class="flex flex-col items-center gap-4 text-center">
        <div class="bg-surface-100 flex h-14 w-14 items-center justify-center rounded-2xl">
          <Icon name="lock" size="2xl" class="text-surface-400" />
        </div>
        <div>
          <p class="text-surface-900 text-sm font-semibold">App entsperren</p>
          <p class="text-surface-500 mt-0.5 text-xs">Bestätige deine Identität per Biometrie.</p>
        </div>
        <Btn variant="primary" onclick={() => biometricLock.unlock()}>Entsperren</Btn>
      </div>
    </div>
  {/if}
{:else if auth.loading}
  <div class="flex min-h-screen items-center justify-center">
    <div
      class="border-primary-200 border-t-primary-600 h-8 w-8 animate-spin rounded-full border-4"
    ></div>
  </div>
{/if}
