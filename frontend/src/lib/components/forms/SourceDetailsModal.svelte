<script lang="ts">
  import { useQuery } from '$lib/db/use-query.svelte';
  import { db } from '$lib/db/database';
  import { getSourceStat, scheduleStatsRefresh } from '$lib/db/metric-stats';
  import { Capacitor } from '@capacitor/core';
  import { healthSyncService, healthSyncUi, permissionLabel } from '$lib/native/health-sync.svelte';
  import { isSourceEnabled, reportDeviceSourceStatus, type SourceStatus } from '$lib/sources';
  import Modal from '$components/ui/Modal.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import StatusDot from '$components/ui/StatusDot.svelte';
  import { resolveColor } from '$lib/theme/colors';

  interface KnownSource {
    id: string;
    name: string;
    icon: string;
    color: string;
  }

  interface Props {
    open?: boolean;
    source: KnownSource | null;
    count: number;
    onClose?: () => void;
    onStatusChange?: () => void;
  }

  let { open = $bindable(false), source, count = 0, onClose, onStatusChange }: Props = $props();

  let metricsSupplied = $state<Array<{ code: string; name: string; count: number }>>([]);
  let lastSyncTime = $state<string | null>(null);
  let sourceStatus = $state<SourceStatus | null>(null);
  let refreshTick = $state(0);

  // Health Connect integration state
  let isNativeAndroid = $derived(Capacitor.isNativePlatform());
  let syncing = $state(false);
  let requestingPerms = $state(false);
  let healthConnectGranted = $state(false);
  let permissionState = $state<{ granted: number; missingLabels: string[] } | null>(null);
  let syncFeedback = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  const sourceDataQuery = useQuery(
    async () => {
      if (!open || !source) return { supplied: [], lastTime: null };
      const srcId = source.id;
      const allDefs = await db.metric_definition.toArray();
      const defNameByCode = new Map(allDefs.map((d) => [d.code, d.name]));
      const srcStat = await getSourceStat(srcId);

      const supplied: Array<{ code: string; name: string; count: number }> = [];
      if (srcStat && srcStat.metrics) {
        for (const [code, cnt] of Object.entries(srcStat.metrics)) {
          if (cnt > 0) {
            supplied.push({
              code,
              name: defNameByCode.get(code) ?? code,
              count: cnt
            });
          }
        }
      }
      supplied.sort((a, b) => b.count - a.count);

      return { supplied, lastTime: srcStat?.latest_time ?? null };
    },
    () => `${open}:${source?.id}:${refreshTick}`
  );
  const sourceData = $derived(sourceDataQuery.value);
  const loading = $derived(sourceDataQuery.loading);

  $effect(() => {
    syncFeedback = null;
    if (source?.id === 'health_connect' && isNativeAndroid) {
      loadPermissionState();
    }
  });

  async function loadPermissionState() {
    const res = await healthSyncService.checkPermissions();
    healthConnectGranted = res.granted;
    permissionState = {
      granted: res.grantedPermissions.length,
      missingLabels: res.missing.map(permissionLabel)
    };
  }

  // Permissions are granted in the system Health Connect screen; refresh when the modal
  // (re)gains focus so the status reflects the latest grant state.
  $effect(() => {
    if (!open || source?.id !== 'health_connect' || !isNativeAndroid) return;
    const refresh = () => void loadPermissionState();
    window.addEventListener('focus', refresh);
    document.addEventListener('visibilitychange', refresh);
    return () => {
      window.removeEventListener('focus', refresh);
      document.removeEventListener('visibilitychange', refresh);
    };
  });

  async function handleOpenSettings() {
    const ok = await healthSyncService.openHealthConnectSettings();
    await loadPermissionState();
    if (!ok) {
      syncFeedback = {
        type: 'error',
        text: 'Could not open Health Connect settings on this device.'
      };
    }
  }

  $effect(() => {
    const val = sourceData;
    if (val) {
      metricsSupplied = val.supplied;
      lastSyncTime = val.lastTime ? new Date(val.lastTime).toLocaleString() : null;
    }
  });

  $effect(() => {
    if (!open || !source) return;
    isSourceEnabled(source.id).then((s) => (sourceStatus = s));
  });

  // When a background history import finishes, re-run the diagnostics query with fresh stats.
  let wasSeeding = $state(false);
  $effect(() => {
    const isSeeding = healthSyncUi.seedProgress !== null;
    if (wasSeeding && !isSeeding) {
      refreshTick += 1;
    }
    wasSeeding = isSeeding;
  });

  async function refreshStatus() {
    if (!source) return;
    sourceStatus = await isSourceEnabled(source.id);
    onStatusChange?.();
  }

  async function handleRequestPermissions() {
    requestingPerms = true;
    syncFeedback = null;
    try {
      await healthSyncService.requestPermissions();
      await loadPermissionState();
      await reportDeviceSourceStatus();
      await refreshStatus();
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : String(e);
      syncFeedback = { type: 'error', text: err };
    } finally {
      requestingPerms = false;
    }
  }

  import { toast } from '$components/ui/toast-state.svelte';
  import { toastSettings } from '$stores/toast-settings.svelte';

  async function handleSyncNow() {
    syncing = true;
    syncFeedback = null;
    try {
      const res = await healthSyncService.syncNow();
      syncFeedback = {
        type: res.success ? 'success' : 'error',
        text: res.message
      };
      if (toastSettings.healthConnect) {
        toast(res.message, res.success ? (res.count > 0 ? 'success' : 'info') : 'error');
      }
      if (res.success) {
        // Refresh diagnostics once the background stats recompute lands; the button itself
        // must not block on it.
        void scheduleStatsRefresh().then(() => {
          refreshTick += 1;
        });
        if (res.count > 0) {
          await loadPermissionState();
        }
      }
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : String(e);
      syncFeedback = { type: 'error', text: err };
      if (toastSettings.healthConnect) {
        toast(`Health Connect sync failed: ${err}`, 'error');
      }
    } finally {
      syncing = false;
    }
  }

  const INACTIVE_GUIDES: Record<string, string> = {
    health_connect:
      'Open Android Settings -> Privacy -> Health Connect -> Grant Salus read permissions for Health & Fitness data.',
    apple_health:
      'Open Apple Health app on iOS -> Tapping Sharing -> Apps & Services -> Salus -> Enable All Categories.',
    samsung_health:
      'Ensure Samsung Health is connected to Health Connect on Android to sync steps and sleep automatically.',
    oura: 'Connect your Oura Ring Personal Access Token or OAuth2 account in Salus Integrations.',
    garmin: 'Authorize Salus Garmin Connect API bridge in settings.',
    manual: 'Log entries manually via the "+ New Entry" button on any Metric detail page.',
    seed: 'Use "just seed-dev" CLI command to populate dev sample data.'
  };
</script>

{#if source}
  <Modal bind:open title="{source.name} — Source Diagnostics" onclose={onClose} size="md">
    {#if loading}
      <div class="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    {:else}
      <div class="space-y-6">
        <!-- Header Info Card -->
        <div
          class="border-surface-200 bg-surface-50 flex items-center justify-between rounded-lg border p-4"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-11 w-11 items-center justify-center rounded-lg text-white shadow-2xs"
              style="background-color: {count > 0 ? resolveColor(source.color) : '#9ca3af'}"
            >
              <Icon name={source.icon} size="md" />
            </div>
            <div>
              <h3 class="text-surface-900 text-sm font-bold">
                {source.name}
              </h3>
              <span class="text-surface-400 font-mono text-xs">ID: {source.id}</span>
            </div>
          </div>

          <div>
            {#if sourceStatus?.enabled}
              <span
                class="border-success-200 bg-success-50 text-success-700 inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold"
              >
                <span class="bg-success-500 h-2 w-2 rounded-full"></span> Connected
              </span>
            {:else}
              <span
                class="bg-surface-200 text-surface-600 inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium"
              >
                Not connected
              </span>
            {/if}
          </div>
        </div>

        {#if sourceStatus?.detail}
          <p
            class="border-surface-200 bg-surface-50 text-surface-600 rounded-lg border px-3 py-2 text-xs"
          >
            {sourceStatus.detail}
          </p>
        {/if}

        {#if syncFeedback}
          <div
            class="rounded-lg p-3 text-xs font-medium {syncFeedback.type === 'success'
              ? 'border-success-200 bg-success-50 text-success-800 border'
              : 'border-error-200 bg-error-50 text-error-800 border'}"
          >
            {syncFeedback.text}
          </div>
        {/if}

        <!-- NATIVE HEALTH CONNECT QUICK ACTION CONTROLS -->
        {#if source.id === 'health_connect' && isNativeAndroid}
          <div class=" border-primary-200 bg-primary-50/50 rounded-lg border p-4">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-primary-900 text-xs font-bold">Android Health Connect Bridge</h4>
                <p class="text-primary-700 mt-0.5 text-[10px]">
                  Direct native link to Google Health Connect & Samsung Health
                </p>
              </div>
              <div class="flex items-center gap-2">
                {#if !healthConnectGranted}
                  <Btn
                    variant="secondary"
                    size="sm"
                    loading={requestingPerms}
                    onclick={handleRequestPermissions}
                  >
                    <Icon name="key" size="sm" class="mr-1" />
                    Authorize
                  </Btn>
                {/if}
                <Btn variant="primary" size="sm" loading={syncing} onclick={handleSyncNow}>
                  <Icon name="sync" size="sm" class="mr-1" />
                  Sync Now
                </Btn>
              </div>
            </div>

            {#if permissionState && permissionState.missingLabels.length > 0}
              <div class="border-surface-200 bg-surface-50 mt-3 rounded-lg border p-3">
                <div class="flex items-center justify-between gap-2">
                  <div class="flex items-center gap-2">
                    <StatusDot status="warning" size="sm" />
                    <h5 class="text-surface-900 text-xs font-bold">
                      Data access · {permissionState.granted} categories readable
                    </h5>
                  </div>
                  <Btn variant="secondary" size="sm" onclick={handleOpenSettings}>
                    <Icon name="settings" size="sm" class="mr-1" />
                    Open settings
                  </Btn>
                </div>
                <p class="text-surface-600 mt-1.5 text-[10px] leading-relaxed">
                  Categories not offered by Health Connect on this device are skipped automatically.
                  Grant everything Health Connect offers to enable all possible data.
                </p>
                <details class="mt-2">
                  <summary
                    class="text-surface-500 cursor-pointer text-[10px] font-medium select-none"
                  >
                    Show {permissionState.missingLabels.length} skipped categories
                  </summary>
                  <div class="mt-2 flex flex-wrap gap-1">
                    {#each permissionState.missingLabels as label (label)}
                      <span
                        class="border-surface-200 bg-surface-100 text-surface-600 rounded-full border px-2 py-0.5 text-[10px] font-medium"
                      >
                        {label}
                      </span>
                    {/each}
                  </div>
                </details>
              </div>
            {/if}
          </div>
        {/if}

        {#if healthSyncUi.seedProgress}
          <div class="border-surface-200 bg-surface-50 rounded-lg border p-3">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <Spinner size="sm" />
                <h5 class="text-surface-900 text-xs font-bold">Importing Health Connect history</h5>
              </div>
              {#if (healthSyncUi.seedProgress?.done ?? 0) > 0}
                <span class="text-surface-500 font-mono text-xs">
                  {(healthSyncUi.seedProgress?.done ?? 0).toLocaleString()} measurements
                </span>
              {/if}
            </div>
            <p class="text-surface-600 mt-1 text-[10px]">
              First sync imports your full history. Later syncs are instant.
            </p>
            <div class="bg-surface-100 mt-2 h-1 w-full overflow-hidden rounded-full">
              <div class="bg-primary-400 h-1 w-full animate-pulse rounded-full"></div>
            </div>
          </div>
        {/if}

        {#if count > 0}
          <!-- ACTIVE SOURCE DIAGNOSTICS -->
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div class="border-surface-200 bg-surface-0 rounded-lg border p-3">
                <span class="text-surface-500 text-[10px]">Total Measurements</span>
                <div class="text-surface-900 mt-0.5 text-base font-bold">
                  {count.toLocaleString()}
                </div>
              </div>
              <div class="border-surface-200 bg-surface-0 rounded-lg border p-3">
                <span class="text-surface-500 text-[10px]">Last Data Ingest</span>
                <div class="text-surface-900 mt-1 truncate text-xs font-semibold">
                  {lastSyncTime ?? 'Recent'}
                </div>
              </div>
            </div>

            <div>
              <h4 class="text-surface-700 mb-2 text-xs font-bold tracking-wider uppercase">
                Metrics Supplied ({metricsSupplied.length})
              </h4>
              <div class="max-h-48 space-y-1.5 overflow-y-auto pr-1">
                {#each metricsSupplied as item (item.code)}
                  <div
                    class="border-surface-200/70 bg-surface-0 flex items-center justify-between rounded-md border px-3 py-2 text-xs"
                  >
                    <div class="flex items-center gap-2">
                      <Icon name="monitoring" size="sm" class="text-primary-600" />
                      <span class="text-surface-900 font-semibold">{item.name}</span>
                    </div>
                    <span class="text-surface-500 font-mono"
                      >{item.count.toLocaleString()} entries</span
                    >
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {:else}
          <!-- INACTIVE SOURCE DIAGNOSTICS & SETUP GUIDE -->
          <div class="space-y-4">
            <div class="border-surface-200 bg-surface-50 rounded-lg border p-4">
              <div class="text-surface-800 mb-1 flex items-center gap-2 text-xs font-semibold">
                <Icon name="info" size="sm" class="text-surface-500" />
                Connection Status
              </div>
              <p class="text-surface-600 text-xs leading-relaxed">
                No measurement data received from {source.name} yet. Tap Authorize / Sync Now above or
                grant permissions in system settings to start syncing.
              </p>
            </div>

            <div>
              <h4 class="text-surface-700 mb-2 text-xs font-bold tracking-wider uppercase">
                Setup Instructions
              </h4>
              <div
                class="border-surface-200 bg-surface-0 text-surface-700 rounded-lg border p-4 text-xs leading-relaxed"
              >
                {INACTIVE_GUIDES[source.id] ??
                  'Connect this source in system integration settings.'}
              </div>
            </div>
          </div>
        {/if}

        <div class="border-surface-200 flex items-center justify-end gap-3 border-t pt-4">
          <Btn variant="secondary" onclick={() => (open = false)}>Close</Btn>
        </div>
      </div>
    {/if}
  </Modal>
{/if}
