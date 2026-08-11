<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { getSourceStat } from '$lib/db/metric-stats';
  import { Capacitor } from '@capacitor/core';
  import { healthSyncService } from '$lib/native/health-sync';
  import Modal from '$components/ui/Modal.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Spinner from '$components/ui/Spinner.svelte';

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
  }

  let { open = $bindable(false), source, count = 0, onClose }: Props = $props();

  let loading = $state(true);
  let metricsSupplied = $state<Array<{ code: string; name: string; count: number }>>([]);
  let lastSyncTime = $state<string | null>(null);

  // Health Connect integration state
  let isNativeAndroid = $derived(Capacitor.isNativePlatform());
  let syncing = $state(false);
  let requestingPerms = $state(false);
  let healthConnectGranted = $state(false);
  let syncFeedback = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  $effect(() => {
    if (!open || !source) return;
    loading = true;
    syncFeedback = null;
    const srcId = source.id;

    if (srcId === 'health_connect' && isNativeAndroid) {
      healthSyncService.checkPermissions().then((res) => {
        healthConnectGranted = res.granted;
      });
    }

    const sub = liveQuery(async () => {
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
    }).subscribe((val) => {
      if (val) {
        metricsSupplied = val.supplied;
        lastSyncTime = val.lastTime ? new Date(val.lastTime).toLocaleString() : null;
      }
      loading = false;
    });

    return () => sub.unsubscribe();
  });

  async function handleRequestPermissions() {
    requestingPerms = true;
    syncFeedback = null;
    try {
      await healthSyncService.requestPermissions();
      const status = await healthSyncService.checkPermissions();
      healthConnectGranted = status.granted;
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
      if (res.success && res.count > 0) {
        const status = await healthSyncService.checkPermissions();
        healthConnectGranted = status.granted;
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
          class="flex items-center justify-between rounded-lg border border-surface-200 bg-surface-50 p-4 dark:border-surface-700 dark:bg-surface-800"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-11 w-11 items-center justify-center rounded-lg text-white shadow-2xs"
              style="background-color: {count > 0 ? source.color : '#9ca3af'}"
            >
              <Icon name={source.icon} size="md" />
            </div>
            <div>
              <h3 class="text-sm font-bold text-surface-900 dark:text-surface-100">
                {source.name}
              </h3>
              <span class="font-mono text-xs text-surface-400">ID: {source.id}</span>
            </div>
          </div>

          <div>
            {#if count > 0}
              <span
                class="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
              >
                <span class="h-2 w-2 rounded-full bg-emerald-500"></span> Active
              </span>
            {:else}
              <span
                class="inline-flex items-center rounded-full bg-surface-200 px-2.5 py-1 text-xs font-medium text-surface-600 dark:bg-surface-700 dark:text-surface-300"
              >
                Inactive
              </span>
            {/if}
          </div>
        </div>

        {#if syncFeedback}
          <div
            class="rounded-lg p-3 text-xs font-medium {syncFeedback.type === 'success'
              ? 'border border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-200'
              : 'border border-rose-200 bg-rose-50 text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-200'}"
          >
            {syncFeedback.text}
          </div>
        {/if}

        <!-- NATIVE HEALTH CONNECT QUICK ACTION CONTROLS -->
        {#if source.id === 'health_connect' && isNativeAndroid}
          <div
            class="dark:bg-primary-950/30 rounded-lg border border-primary-200 bg-primary-50/50 p-4 dark:border-primary-800"
          >
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-xs font-bold text-primary-900 dark:text-primary-100">
                  Android Health Connect Bridge
                </h4>
                <p class="mt-0.5 text-[11px] text-primary-700 dark:text-primary-300">
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
          </div>
        {/if}

        {#if count > 0}
          <!-- ACTIVE SOURCE DIAGNOSTICS -->
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div
                class="rounded-lg border border-surface-200 bg-surface-0 p-3 dark:border-surface-700 dark:bg-surface-900"
              >
                <span class="text-[11px] text-surface-500 dark:text-surface-400"
                  >Total Measurements</span
                >
                <div class="mt-0.5 text-base font-bold text-surface-900 dark:text-surface-100">
                  {count.toLocaleString()}
                </div>
              </div>
              <div
                class="rounded-lg border border-surface-200 bg-surface-0 p-3 dark:border-surface-700 dark:bg-surface-900"
              >
                <span class="text-[11px] text-surface-500 dark:text-surface-400"
                  >Last Data Ingest</span
                >
                <div
                  class="mt-1 truncate text-xs font-semibold text-surface-900 dark:text-surface-100"
                >
                  {lastSyncTime ?? 'Recent'}
                </div>
              </div>
            </div>

            <div>
              <h4
                class="mb-2 text-xs font-bold tracking-wider text-surface-700 uppercase dark:text-surface-300"
              >
                Metrics Supplied ({metricsSupplied.length})
              </h4>
              <div class="max-h-48 space-y-1.5 overflow-y-auto pr-1">
                {#each metricsSupplied as item (item.code)}
                  <div
                    class="flex items-center justify-between rounded-md border border-surface-200/70 bg-surface-0 px-3 py-2 text-xs dark:border-surface-700 dark:bg-surface-900"
                  >
                    <div class="flex items-center gap-2">
                      <Icon name="monitoring" size="sm" class="text-primary-600" />
                      <span class="font-semibold text-surface-900 dark:text-surface-100"
                        >{item.name}</span
                      >
                    </div>
                    <span class="font-mono text-surface-500 dark:text-surface-400"
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
            <div
              class="rounded-lg border border-surface-200 bg-surface-50 p-4 dark:border-surface-700 dark:bg-surface-800"
            >
              <div
                class="mb-1 flex items-center gap-2 text-xs font-semibold text-surface-800 dark:text-surface-200"
              >
                <Icon name="info" size="sm" class="text-surface-500" />
                Connection Status
              </div>
              <p class="text-xs leading-relaxed text-surface-600 dark:text-surface-400">
                No measurement data received from {source.name} yet. Tap Authorize / Sync Now above or
                grant permissions in system settings to start syncing.
              </p>
            </div>

            <div>
              <h4
                class="mb-2 text-xs font-bold tracking-wider text-surface-700 uppercase dark:text-surface-300"
              >
                Setup Instructions
              </h4>
              <div
                class="rounded-lg border border-surface-200 bg-surface-0 p-4 text-xs leading-relaxed text-surface-700 dark:border-surface-700 dark:bg-surface-900 dark:text-surface-300"
              >
                {INACTIVE_GUIDES[source.id] ??
                  'Connect this source in system integration settings.'}
              </div>
            </div>
          </div>
        {/if}

        <div
          class="flex items-center justify-end gap-3 border-t border-surface-200 pt-4 dark:border-surface-700"
        >
          <Btn variant="secondary" onclick={() => (open = false)}>Close</Btn>
        </div>
      </div>
    {/if}
  </Modal>
{/if}
