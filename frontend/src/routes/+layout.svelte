<script lang="ts">
  import '../app.css';
  import '@fontsource/manrope/400.css';
  import '@fontsource/manrope/500.css';
  import '@fontsource/manrope/600.css';
  import '@fontsource/manrope/700.css';
  import '@fontsource/manrope/800.css';
  import { addCollection } from '@iconify/svelte/dist/offline-functions.js';
  import icons from '$lib/icons.json';
  addCollection(icons);
  import { auth } from '$stores/auth.svelte';
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { setLocaleState } from '$lib/api/headers';
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { useOffline } from '$lib/db/use-offline.svelte';
  import TopAppBar from '$components/layout/TopAppBar.svelte';
  import OfflineIndicator from '$components/feedback/OfflineIndicator.svelte';
  import ConflictResolver from '$components/feedback/ConflictResolver.svelte';

  let { children } = $props();

  const publicPaths = ['/auth/login', '/auth/register'];
  let isPublic = $derived(publicPaths.includes(page.url.pathname));

  let userProfiles = liveQuery(() => db.user_profile.toArray());
  let userProfile = $derived($userProfiles && $userProfiles.length > 0 ? $userProfiles[0] : null);

  // ── Auth bootstrap: assume valid token → app renders instantly ──

  onMount(async () => {
    if (!auth.token) {
      auth.setLoading(false);
      if (!isPublic) await goto('/auth/login');
      return;
    }

    auth.setLoading(false);
  });

  // ── Locale from Dexie (updates reactive, persists to localStorage for headers.ts) ──

  $effect(() => {
    if (userProfile) {
      setLocaleState(userProfile.locale ?? 'en');
      localStorage.setItem('salus_user', JSON.stringify(userProfile));
      localStorage.setItem('salus_user_is_admin', String(userProfile.is_admin ?? false));
    }
  });

  // ── Sync trigger — lazy token validation via sync pull ──

  let synced = false;
  let sessionExpired = $state(false);

  $effect(() => {
    if (auth.isAuthenticated && !synced) {
      synced = true;
      runSync();
    }
  });

  async function runSync() {
    await useOffline.syncAll();
    if (useOffline.sessionExpired) {
      useOffline.stopLiveSync();
      sessionExpired = true;
      setTimeout(async () => {
        auth.clear();
        await goto('/auth/login');
      }, 2000);
    }
  }
</script>

{#if isPublic}
  <div class="flex min-h-screen items-center justify-center bg-surface-50 p-4">
    {@render children()}
  </div>
{:else if auth.isAuthenticated}
  {#if sessionExpired}
    <!-- Session expired overlay -->
    <div class="fixed inset-0 z-[100] flex items-center justify-center bg-surface-0/85 backdrop-blur-sm">
      <div class="flex flex-col items-center gap-4 text-center">
        <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-surface-100">
          <span class="material-symbols-outlined text-3xl text-surface-400">vpn_key_off</span>
        </div>
        <div>
          <p class="text-sm font-semibold text-surface-900">Session expired</p>
          <p class="mt-0.5 text-xs text-surface-500">Redirecting to login…</p>
        </div>
        <div class="h-1 w-32 overflow-hidden rounded-full bg-surface-100">
          <div class="h-full animate-shrink origin-left rounded-full bg-surface-300"></div>
        </div>
      </div>
    </div>
  {:else}
    <div class="flex min-h-screen flex-col bg-surface-50">
      <TopAppBar />
      <main class="mx-auto w-full max-w-[1440px] flex-1 px-6 py-10 md:px-10">
        {@render children()}
      </main>
      <OfflineIndicator />
      <ConflictResolver />
    </div>
  {/if}
{:else if auth.loading}
  <div class="flex min-h-screen items-center justify-center">
    <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600"></div>
  </div>
{/if}

<style>
  @keyframes shrink {
    from { width: 100%; }
    to   { width: 0%; }
  }
  .animate-shrink {
    animation: shrink 2s ease-in forwards;
  }
</style>
