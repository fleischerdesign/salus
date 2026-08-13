<script lang="ts">
  import { Capacitor } from '@capacitor/core';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Toggle from '$components/ui/Toggle.svelte';
  import RadioGroup from '$components/ui/RadioGroup.svelte';
  import { db } from '$lib/db/database';
  import { getSystemStats } from '$lib/db/metric-stats';
  import { getApiBaseUrl, setApiBaseUrl, testServerConnection } from '$lib/api/headers';
  import { exportDatabase, importDatabase } from '$lib/db/export-import';
  import { theme, type ThemeMode, ACCENT_HUES } from '$stores/theme.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import HueRing from '$components/ui/HueRing.svelte';
  import { hueGradient } from '$lib/theme/hue';

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
        throw new Error(`GitHub Releases antwortete mit Status ${res.status}`);
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
        releaseNotes: data.body || 'Keine Versionshinweise vorhanden.',
        downloadUrl: apkAsset?.browser_download_url || data.html_url,
        publishedAt: data.published_at ? new Date(data.published_at).toLocaleDateString() : '',
        checked: true
      };
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Verbindung zu GitHub Releases fehlgeschlagen.';
      updateResult = {
        hasUpdate: false,
        checked: true,
        error: msg
      };
    } finally {
      checkingUpdate = false;
    }
  }

  // ── Erscheinungsbild ──
  const themeOptions = [
    { value: 'light', label: 'Hell' },
    { value: 'dark', label: 'Dunkel' },
    { value: 'system', label: 'System' }
  ];

  function setTheme(val: string) {
    theme.setMode(val as ThemeMode);
  }

  let accentPickerOpen = $state(false);
  const isCustomAccent = $derived(!ACCENT_HUES.some((a) => a.hue === theme.accentHue));

  import { toastSettings } from '$stores/toast-settings.svelte';
  import { useOffline } from '$lib/db/use-offline.svelte';

  // ── Synchronisation ──
  let batterySaverSync = $state(localStorage.getItem('salus_sync_battery_saver') === 'true');
  let isResyncing = $state(false);
  let resyncMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  function toggleBatterySaver(val: boolean) {
    batterySaverSync = val;
    localStorage.setItem('salus_sync_battery_saver', val ? 'true' : 'false');
  }

  async function handleForceResync() {
    isResyncing = true;
    resyncMessage = null;
    try {
      await useOffline.syncAll({ manual: true });
      await loadDbCounts();
      resyncMessage = { type: 'success', text: 'Synchronisation erfolgreich abgeschlossen.' };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Synchronisation fehlgeschlagen.';
      resyncMessage = { type: 'error', text: msg };
    } finally {
      isResyncing = false;
    }
  }

  // ── Lokaler Speicher ──
  let storageUsage = $state<string>('Wird berechnet…');
  let entityCounts = $state<{
    measurements: number;
    workouts: number;
    meals: number;
    habits: number;
    medications: number;
  }>({
    measurements: 0,
    workouts: 0,
    meals: 0,
    habits: 0,
    medications: 0
  });

  async function loadDbCounts() {
    try {
      const sysStats = await getSystemStats();
      const [w, f, h, med] = await Promise.all([
        db.workout_session.count(),
        db.meal.count(),
        db.habit.count(),
        db.medication.count()
      ]);
      entityCounts = {
        measurements: sysStats.total_measurements,
        workouts: w,
        meals: f,
        habits: h,
        medications: med
      };
    } catch {
      /* ignore */
    }

    if (typeof navigator !== 'undefined' && navigator.storage && navigator.storage.estimate) {
      try {
        const est = await navigator.storage.estimate();
        const usageMb = ((est.usage || 0) / (1024 * 1024)).toFixed(1);
        storageUsage = `${usageMb} MB`;
      } catch {
        storageUsage = 'Offline verfügbar';
      }
    } else {
      storageUsage = 'Offline verfügbar';
    }
  }

  // ── Gerätesicherheit (Native Android) ──
  let hapticsEnabled = $state(localStorage.getItem('salus_haptics') !== 'false');
  let biometricsEnabled = $state(localStorage.getItem('salus_biometrics') === 'true');

  // ── Lokaler Speicher: Export/Import ──
  let exporting = $state(false);
  let importing = $state(false);
  let storageMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);
  let fileInput: HTMLInputElement | undefined;

  function triggerImport() {
    fileInput?.click();
  }

  async function handleExport() {
    exporting = true;
    storageMessage = null;
    try {
      const json = await exportDatabase();
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `salus-backup-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      storageMessage = { type: 'success', text: 'Backup exportiert.' };
    } catch {
      storageMessage = { type: 'error', text: 'Export fehlgeschlagen.' };
    } finally {
      exporting = false;
    }
  }

  async function handleImport(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    importing = true;
    storageMessage = null;
    try {
      const text = await file.text();
      await importDatabase(text);
      storageMessage = { type: 'success', text: 'Backup importiert.' };
      await loadDbCounts();
    } catch {
      storageMessage = { type: 'error', text: 'Import fehlgeschlagen — ungültige Datei.' };
    } finally {
      importing = false;
      input.value = '';
    }
  }

  function toggleHaptics(val: boolean) {
    hapticsEnabled = val;
    localStorage.setItem('salus_haptics', val ? 'true' : 'false');
  }

  function toggleBiometrics(val: boolean) {
    biometricsEnabled = val;
    localStorage.setItem('salus_biometrics', val ? 'true' : 'false');
  }

  // ── Server-Adresse (Native Android) ──
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
      serverMessage = { type: 'success', text: 'Server erfolgreich verbunden und gespeichert!' };
    } else {
      serverMessage = { type: 'error', text: testRes.message };
    }
  }

  $effect(() => {
    loadDbCounts();
  });
</script>

<div class="space-y-6">
  <!-- Version & Updates -->
  <Card padding={false}>
    <div class="space-y-4 p-5">
      <div class="flex items-center justify-between">
        <h3 class="flex items-center gap-2.5 text-base font-semibold text-surface-900">
          Salus {isNative ? 'Android' : 'PWA'}
          <Badge variant="default">v{CURRENT_APP_VERSION}</Badge>
        </h3>
        <Btn variant="secondary" size="sm" loading={checkingUpdate} onclick={checkForUpdates}>
          Nach Updates suchen
        </Btn>
      </div>

      {#if updateResult.checked}
        {#if updateResult.error}
          <AlertBanner variant="error">
            {updateResult.error}
          </AlertBanner>
        {:else if updateResult.hasUpdate}
          <div class="rounded-xl border border-primary-200 bg-primary-50/60 p-4">
            <div class="flex items-start justify-between gap-4">
              <div>
                <div class="flex items-center gap-2">
                  <span
                    class="rounded-md bg-primary-600 px-2 py-0.5 text-xs font-bold text-white uppercase"
                  >
                    Neues Update verfügbar
                  </span>
                  <span class="font-mono text-xs font-bold text-primary-900">
                    {updateResult.latestVersion}
                  </span>
                  {#if updateResult.publishedAt}
                    <span class="text-[10px] text-primary-600">({updateResult.publishedAt})</span>
                  {/if}
                </div>
                <p class="text-primary-950 mt-2 text-xs leading-relaxed whitespace-pre-line">
                  {updateResult.releaseNotes}
                </p>
              </div>
              <Btn variant="primary" size="sm" href={updateResult.downloadUrl} class="shrink-0">
                Herunterladen
              </Btn>
            </div>
          </div>
        {:else}
          <AlertBanner variant="success">
            Salus ist auf dem neuesten Stand (v{CURRENT_APP_VERSION}).
          </AlertBanner>
        {/if}
      {/if}
    </div>
  </Card>

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
    <!-- Erscheinungsbild -->
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Erscheinungsbild</span>
      {/snippet}
      <div class="space-y-5 p-5">
        <div>
          <p class="mb-2 text-xs font-semibold tracking-wider text-surface-400 uppercase">
            Farbschema
          </p>
          <RadioGroup name="theme" options={themeOptions} value={theme.mode} onchange={setTheme} />
        </div>
        <div class="border-t border-surface-100 pt-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold text-surface-800">Farbenblind-Modus</p>
              <p class="text-xs text-surface-400">Farbenblindsichere Farben in der gesamten App</p>
            </div>
            <Toggle checked={theme.colorblind} onchange={(v) => theme.setColorblind(v)} />
          </div>
        </div>
        <div class="border-t border-surface-100 pt-5">
          <p class="mb-2 text-xs font-semibold tracking-wider text-surface-400 uppercase">
            Akzentfarbe
          </p>
          <div class="flex gap-2">
            {#each ACCENT_HUES as accent (accent.hue)}
              <button
                type="button"
                class="h-8 w-8 rounded-full border-2 transition-all"
                class:border-surface-300={theme.accentHue !== accent.hue}
                class:border-surface-900={theme.accentHue === accent.hue}
                class:ring-2={theme.accentHue === accent.hue}
                class:ring-primary-300={theme.accentHue === accent.hue}
                style="background-color: {accent.color}"
                aria-label={accent.label}
                onclick={() => theme.setAccentHue(accent.hue)}
              ></button>
            {/each}
            <button
              type="button"
              class="h-8 w-8 rounded-full border-2 transition-all"
              class:border-surface-300={!isCustomAccent}
              class:border-surface-900={isCustomAccent}
              class:ring-2={isCustomAccent}
              class:ring-primary-300={isCustomAccent}
              style="background: {hueGradient()}"
              aria-label="Eigene Farbe wählen"
              onclick={() => (accentPickerOpen = true)}
            ></button>
          </div>
        </div>
      </div>
    </Card>

    <Modal bind:open={accentPickerOpen} title="Akzentfarbe" size="sm">
      <div class="flex justify-center p-6">
        <HueRing
          value={theme.accentHue}
          onchange={(h) => theme.previewAccentHue(h)}
          oncommit={(h) => theme.setAccentHue(h)}
        />
      </div>
    </Modal>

    <!-- Synchronisation -->
    <Card padding={false}>
      {#snippet header()}
        <div class="flex items-center justify-between">
          <span class="text-sm font-semibold text-surface-900">Synchronisation</span>
          <span
            class="inline-flex items-center gap-1 rounded-full bg-success-50 px-2 py-0.5 text-[10px] font-bold text-success-700"
          >
            <span class="h-1.5 w-1.5 rounded-full bg-success-500"></span> Aktiv
          </span>
        </div>
      {/snippet}
      <div class="space-y-4 p-5">
        <div class="flex items-center justify-between">
          <div>
            <h5 class="text-sm font-semibold text-surface-800">Energiesparmodus</h5>
            <p class="text-xs text-surface-400">
              Synchronisationsintervall bei mobilen Daten reduzieren
            </p>
          </div>
          <Toggle checked={batterySaverSync} onchange={toggleBatterySaver} />
        </div>

        {#if resyncMessage}
          <AlertBanner variant={resyncMessage.type === 'success' ? 'success' : 'error'}>
            {resyncMessage.text}
          </AlertBanner>
        {/if}

        <div class="flex items-center justify-between border-t border-surface-100 pt-4">
          <div>
            <h5 class="text-sm font-semibold text-surface-800">Vollsync ausführen</h5>
            <p class="text-xs text-surface-400">Alle Daten frisch vom Server abgleichen</p>
          </div>
          <Btn variant="secondary" size="sm" loading={isResyncing} onclick={handleForceResync}>
            Jetzt abgleichen
          </Btn>
        </div>
      </div>
    </Card>

    <!-- Toasts & Benachrichtigungen -->
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Toasts & Benachrichtigungen</span>
      {/snippet}
      <div class="space-y-4 p-5">
        <div class="flex items-center justify-between">
          <div>
            <h5 class="text-sm font-semibold text-surface-800">Health-Connect-Import</h5>
            <p class="text-xs text-surface-400">
              Erfolgsmeldung mit Anzahl importierter Datenpunkte anzeigen
            </p>
          </div>
          <Toggle
            checked={toastSettings.healthConnect}
            onchange={(val) => toastSettings.setHealthConnect(val)}
          />
        </div>

        <div class="flex items-center justify-between border-t border-surface-100 pt-4">
          <div>
            <h5 class="text-sm font-semibold text-surface-800">Manueller Cloud-Sync</h5>
            <p class="text-xs text-surface-400">
              Fortschrittsbalken und Bestätigung bei manuellem Sync
            </p>
          </div>
          <Toggle
            checked={toastSettings.manualSync}
            onchange={(val) => toastSettings.setManualSync(val)}
          />
        </div>

        <div class="flex items-center justify-between border-t border-surface-100 pt-4">
          <div>
            <h5 class="text-sm font-semibold text-surface-800">Automatischer Hintergrund-Sync</h5>
            <p class="text-xs text-surface-400">
              Meldungen bei automatischem Hintergrund-Sync und App-Start
            </p>
          </div>
          <Toggle
            checked={toastSettings.backgroundSync}
            onchange={(val) => toastSettings.setBackgroundSync(val)}
          />
        </div>

        <div class="flex items-center justify-between border-t border-surface-100 pt-4">
          <div>
            <h5 class="text-sm font-semibold text-surface-800">Netzwerk-Status</h5>
            <p class="text-xs text-surface-400">
              Hinweise bei Verbindungsverlust und Wiederverbindung
            </p>
          </div>
          <Toggle
            checked={toastSettings.networkStatus}
            onchange={(val) => toastSettings.setNetworkStatus(val)}
          />
        </div>
      </div>
    </Card>

    <!-- Lokaler Speicher -->
    <Card padding={false}>
      {#snippet header()}
        <div class="flex items-center justify-between">
          <span class="text-sm font-semibold text-surface-900">Lokaler Speicher</span>
          <Badge variant="primary">{storageUsage}</Badge>
        </div>
      {/snippet}
      <div class="p-5">
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div
            class="flex items-center justify-between rounded-lg border border-surface-100 bg-surface-50 p-2.5"
          >
            <span class="text-surface-600">Messungen</span>
            <span class="font-bold text-surface-900">{entityCounts.measurements}</span>
          </div>
          <div
            class="flex items-center justify-between rounded-lg border border-surface-100 bg-surface-50 p-2.5"
          >
            <span class="text-surface-600">Workouts</span>
            <span class="font-bold text-surface-900">{entityCounts.workouts}</span>
          </div>
          <div
            class="flex items-center justify-between rounded-lg border border-surface-100 bg-surface-50 p-2.5"
          >
            <span class="text-surface-600">Mahlzeiten</span>
            <span class="font-bold text-surface-900">{entityCounts.meals}</span>
          </div>
          <div
            class="flex items-center justify-between rounded-lg border border-surface-100 bg-surface-50 p-2.5"
          >
            <span class="text-surface-600">Gewohnheiten</span>
            <span class="font-bold text-surface-900">{entityCounts.habits}</span>
          </div>
        </div>

        {#if storageMessage}
          <div class="mt-3">
            <AlertBanner variant={storageMessage.type}>{storageMessage.text}</AlertBanner>
          </div>
        {/if}

        <div class="mt-4 flex gap-2">
          <Btn variant="secondary" size="sm" loading={exporting} onclick={handleExport}>
            Exportieren
          </Btn>
          <Btn variant="secondary" size="sm" loading={importing} onclick={triggerImport}>
            Importieren
          </Btn>
          <input
            type="file"
            accept="application/json"
            class="hidden"
            bind:this={fileInput}
            onchange={handleImport}
          />
        </div>
      </div>
    </Card>

    {#if isNative}
      <!-- Native Android: Gerätesicherheit -->
      <Card padding={false}>
        {#snippet header()}
          <span class="text-sm font-semibold text-surface-900">Gerätesicherheit</span>
        {/snippet}
        <div class="divide-y divide-surface-100 p-5">
          <div class="flex items-center justify-between pb-4">
            <div>
              <h5 class="text-sm font-semibold text-surface-800">Biometrische Sperre</h5>
              <p class="text-xs text-surface-400">
                App-Zugriff per Fingerabdruck / FaceID schützen
              </p>
            </div>
            <Toggle checked={biometricsEnabled} onchange={toggleBiometrics} />
          </div>

          <div class="flex items-center justify-between pt-4">
            <div>
              <h5 class="text-sm font-semibold text-surface-800">Haptisches Feedback</h5>
              <p class="text-xs text-surface-400">Vibration bei Trainingssätzen</p>
            </div>
            <Toggle checked={hapticsEnabled} onchange={toggleHaptics} />
          </div>
        </div>
      </Card>

      <!-- Native Android: Server-Adresse -->
      <Card padding={false}>
        {#snippet header()}
          <span class="text-sm font-semibold text-surface-900">Server-Adresse</span>
        {/snippet}
        <form onsubmit={handleSaveServerUrl} class="space-y-4 p-5">
          <p class="text-xs text-surface-500">Ziel-URL deiner dezentralen Salus FastAPI-Instanz.</p>

          {#if serverMessage}
            <AlertBanner variant={serverMessage.type === 'success' ? 'success' : 'error'}>
              {serverMessage.text}
            </AlertBanner>
          {/if}

          <FormField label="Server URL">
            <Input
              name="serverUrl"
              bind:value={serverUrl}
              placeholder="https://salus.meine-domain.de"
            />
          </FormField>

          <div class="flex justify-end">
            <Btn variant="primary" type="submit" size="sm" loading={serverTesting}>
              Speichern & Testen
            </Btn>
          </div>
        </form>
      </Card>
    {/if}
  </div>
</div>
