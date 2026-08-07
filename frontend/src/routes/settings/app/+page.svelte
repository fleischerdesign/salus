<script lang="ts">
  import { onMount } from 'svelte';
  import { Capacitor } from '@capacitor/core';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Toggle from '$components/ui/Toggle.svelte';
  import { getApiBaseUrl, setApiBaseUrl, testServerConnection } from '$lib/api/headers';

  const CURRENT_APP_VERSION = '0.1.0';

  let isNative = $state(Capacitor.isNativePlatform());

  // ── Version & GitHub Releases State ──
  let checkingUpdate = $state(false);
  let updateResult = $state<{
    hasUpdate: boolean;
    latestVersion?: string;
    releaseNotes?: string;
    downloadUrl?: string;
    publishedAt?: string;
    checked: boolean;
    error?: string;
  }>({ hasUpdate: false, checked: false });

  async function checkForUpdates() {
    checkingUpdate = true;
    updateResult = { hasUpdate: false, checked: false };

    try {
      const res = await fetch(
        'https://api.github.com/repos/fleischerdesign/salus/releases/latest',
        {
          headers: { Accept: 'application/vnd.github.v3+json' }
        }
      );
      if (!res.ok) {
        throw new Error(`GitHub Releases responded with status ${res.status}`);
      }
      const data = await res.json();
      const tagName = (data.tag_name || '').replace(/^v/, '');
      const isNewer = tagName && tagName !== CURRENT_APP_VERSION;

      const apkAsset = Array.isArray(data.assets)
        ? data.assets.find((a: { name?: string }) => a.name?.endsWith('.apk'))
        : null;

      updateResult = {
        hasUpdate: Boolean(isNewer),
        latestVersion: data.tag_name || 'v0.1.0',
        releaseNotes: data.body || 'No release notes provided.',
        downloadUrl: apkAsset?.browser_download_url || data.html_url,
        publishedAt: data.published_at ? new Date(data.published_at).toLocaleDateString() : '',
        checked: true
      };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to reach GitHub Releases API.';
      updateResult = {
        hasUpdate: false,
        checked: true,
        error: msg
      };
    } finally {
      checkingUpdate = false;
    }
  }

  // ── Hardware & Device-Local Settings ──
  let hapticsEnabled = $state(localStorage.getItem('salus_haptics') !== 'false');
  let biometricsEnabled = $state(localStorage.getItem('salus_biometrics') === 'true');
  let storageUsage = $state<string>('Calculating…');

  function toggleHaptics(val: boolean) {
    hapticsEnabled = val;
    localStorage.setItem('salus_haptics', val ? 'true' : 'false');
  }

  function toggleBiometrics(val: boolean) {
    biometricsEnabled = val;
    localStorage.setItem('salus_biometrics', val ? 'true' : 'false');
  }

  async function calculateStorage() {
    if (typeof navigator !== 'undefined' && navigator.storage && navigator.storage.estimate) {
      try {
        const est = await navigator.storage.estimate();
        const usageMb = ((est.usage || 0) / (1024 * 1024)).toFixed(2);
        const quotaMb = ((est.quota || 0) / (1024 * 1024)).toFixed(0);
        storageUsage = `${usageMb} MB used of ${quotaMb} MB available`;
      } catch {
        storageUsage = 'IndexedDB storage available';
      }
    } else {
      storageUsage = 'Local IndexedDB storage';
    }
  }

  onMount(() => {
    calculateStorage();
  });

  // ── Server Host Configuration ──
  let serverUrl = $state(getApiBaseUrl());
  let serverTesting = $state(false);
  let serverMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  async function handleSaveServerUrl(e: Event) {
    e.preventDefault();
    serverTesting = true;
    serverMessage = null;

    const testRes = await testServerConnection(serverUrl);
    serverTesting = false;

    if (testRes.success) {
      const saved = setApiBaseUrl(serverUrl);
      serverUrl = saved;
      serverMessage = { type: 'success', text: 'Server host verified and saved successfully!' };
    } else {
      serverMessage = { type: 'error', text: testRes.message };
    }
  }
</script>

<div class="space-y-6">
  <!-- System & Version Card -->
  <Card padding={false}>
    {#snippet header()}
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold text-surface-900">Salus App & Version</span>
        {#if isNative}
          <span
            class="inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700"
          >
            <Icon name="smartphone" size="sm" /> Android APK
          </span>
        {:else}
          <span
            class="inline-flex items-center gap-1.5 rounded-full border border-surface-200 bg-surface-100 px-2.5 py-0.5 text-xs font-semibold text-surface-700"
          >
            <Icon name="language" size="sm" /> Web / PWA
          </span>
        {/if}
      </div>
    {/snippet}

    <div class="space-y-4 p-5">
      <div class="flex items-center justify-between">
        <div>
          <h4 class="text-base font-semibold text-surface-900">
            Salus Client v{CURRENT_APP_VERSION}
          </h4>
          <p class="text-xs text-surface-500">
            Decentralized health data tracker with offline-first Dexie engine.
          </p>
        </div>
        <Btn variant="secondary" size="sm" loading={checkingUpdate} onclick={checkForUpdates}>
          Check for Updates
        </Btn>
      </div>

      {#if updateResult.checked}
        {#if updateResult.error}
          <AlertBanner variant="error">
            {updateResult.error}
          </AlertBanner>
        {:else if updateResult.hasUpdate}
          <div class="rounded-xl border border-indigo-200 bg-indigo-50/60 p-4">
            <div class="flex items-start justify-between gap-4">
              <div>
                <div class="flex items-center gap-2">
                  <span
                    class="rounded-md bg-indigo-600 px-2 py-0.5 text-xs font-bold text-white uppercase"
                  >
                    New Release Available
                  </span>
                  <span class="font-mono text-xs font-bold text-indigo-900">
                    {updateResult.latestVersion}
                  </span>
                  {#if updateResult.publishedAt}
                    <span class="text-[11px] text-indigo-600">({updateResult.publishedAt})</span>
                  {/if}
                </div>
                <p class="mt-2 text-xs leading-relaxed whitespace-pre-line text-indigo-950">
                  {updateResult.releaseNotes}
                </p>
              </div>
              <Btn variant="primary" size="sm" href={updateResult.downloadUrl} class="shrink-0">
                Download Update
              </Btn>
            </div>
          </div>
        {:else}
          <AlertBanner variant="success">
            Salus is currently running the latest release (v{CURRENT_APP_VERSION}).
          </AlertBanner>
        {/if}
      {/if}
    </div>
  </Card>

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
    <!-- Decentralized Server Host -->
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Decentralized Server Host</span>
      {/snippet}
      <form onsubmit={handleSaveServerUrl} class="space-y-4 p-5">
        <p class="text-xs text-surface-500">
          Target FastAPI instance for real-time synchronization, auth, and exports.
        </p>

        {#if serverMessage}
          <AlertBanner variant={serverMessage.type === 'success' ? 'success' : 'error'}>
            {serverMessage.text}
          </AlertBanner>
        {/if}

        <FormField label="Server URL">
          <Input
            name="serverUrl"
            bind:value={serverUrl}
            placeholder="https://salus.my-domain.com"
          />
        </FormField>

        <div class="flex justify-end">
          <Btn variant="primary" type="submit" size="sm" loading={serverTesting}>
            Test & Save Host
          </Btn>
        </div>
      </form>
    </Card>

    <!-- Device & Hardware Capabilities -->
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Hardware & Device Options</span>
      {/snippet}
      <div class="divide-y divide-surface-100 p-5">
        <div class="flex items-center justify-between pb-4">
          <div>
            <h5 class="text-sm font-semibold text-surface-800">Haptic Vibration</h5>
            <p class="text-xs text-surface-400">
              Tactile pulses for workout set logging and rest timer
            </p>
          </div>
          <Toggle checked={hapticsEnabled} onchange={toggleHaptics} />
        </div>

        <div class="flex items-center justify-between py-4">
          <div>
            <h5 class="text-sm font-semibold text-surface-800">Biometric App Lock</h5>
            <p class="text-xs text-surface-400">Require Fingerprint or FaceID when opening Salus</p>
          </div>
          <Toggle checked={biometricsEnabled} onchange={toggleBiometrics} />
        </div>

        <div class="pt-4">
          <div class="flex items-center justify-between">
            <div>
              <h5 class="text-sm font-semibold text-surface-800">Local Offline Cache</h5>
              <p class="font-mono text-xs text-surface-400">{storageUsage}</p>
            </div>
            <Btn variant="secondary" size="sm" onclick={calculateStorage}>Inspect Storage</Btn>
          </div>
        </div>
      </div>
    </Card>
  </div>
</div>
