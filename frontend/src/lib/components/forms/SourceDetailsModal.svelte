<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { Measurement } from '$lib/db/types';
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

  $effect(() => {
    if (!open || !source) return;
    loading = true;
    const srcId = source.id;

    const sub = liveQuery(async () => {
      const measurements = await db.measurement.filter((m) => m.source === srcId).toArray();
      if (measurements.length === 0) {
        return { supplied: [], lastTime: null };
      }

      // Sort by created_at to find latest
      measurements.sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      const latest = measurements[0]?.created_at ?? null;

      // Group counts per metric code
      const metricMap: Record<string, number> = {};
      measurements.forEach((m) => {
        const code = m.metric_code || m.data_type;
        metricMap[code] = (metricMap[code] ?? 0) + 1;
      });

      const allDefs = await db.metric_definition.toArray();
      const defMap = new Map(allDefs.map((d) => [d.code, d.name]));

      const supplied = Object.entries(metricMap).map(([code, cnt]) => ({
        code,
        name: defMap.get(code) ?? code.replace(/_/g, ' ').toUpperCase(),
        count: cnt
      }));

      supplied.sort((a, b) => b.count - a.count);

      return { supplied, lastTime: latest };
    }).subscribe((val) => {
      if (val) {
        metricsSupplied = val.supplied;
        lastSyncTime = val.lastTime ? new Date(val.lastTime).toLocaleString() : null;
      }
      loading = false;
    });

    return () => sub.unsubscribe();
  });

  const INACTIVE_GUIDES: Record<string, string> = {
    health_connect:
      'Open Android Settings -> Privacy -> Health Connect -> Grant Salus read & write permissions for Health & Fitness data.',
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
          class="flex items-center justify-between rounded-lg border border-surface-200 bg-surface-50 p-4"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-11 w-11 items-center justify-center rounded-lg text-white shadow-2xs"
              style="background-color: {count > 0 ? source.color : '#9ca3af'}"
            >
              <Icon name={source.icon} size="md" />
            </div>
            <div>
              <h3 class="text-sm font-bold text-surface-900">{source.name}</h3>
              <span class="font-mono text-xs text-surface-400">ID: {source.id}</span>
            </div>
          </div>

          <div>
            {#if count > 0}
              <span
                class="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700"
              >
                <span class="h-2 w-2 rounded-full bg-emerald-500"></span> Active
              </span>
            {:else}
              <span
                class="inline-flex items-center rounded-full bg-surface-200 px-2.5 py-1 text-xs font-medium text-surface-600"
              >
                Inactive
              </span>
            {/if}
          </div>
        </div>

        {#if count > 0}
          <!-- ACTIVE SOURCE DIAGNOSTICS -->
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-lg border border-surface-200 bg-surface-0 p-3">
                <span class="text-[11px] text-surface-500">Total Measurements</span>
                <div class="mt-0.5 text-base font-bold text-surface-900">
                  {count.toLocaleString()}
                </div>
              </div>
              <div class="rounded-lg border border-surface-200 bg-surface-0 p-3">
                <span class="text-[11px] text-surface-500">Last Data Ingest</span>
                <div class="mt-1 truncate text-xs font-semibold text-surface-900">
                  {lastSyncTime ?? 'Recent'}
                </div>
              </div>
            </div>

            <div>
              <h4 class="mb-2 text-xs font-bold tracking-wider text-surface-700 uppercase">
                Metrics Supplied ({metricsSupplied.length})
              </h4>
              <div class="max-h-48 space-y-1.5 overflow-y-auto pr-1">
                {#each metricsSupplied as item (item.code)}
                  <div
                    class="flex items-center justify-between rounded-md border border-surface-200/70 bg-surface-0 px-3 py-2 text-xs"
                  >
                    <div class="flex items-center gap-2">
                      <Icon name="monitoring" size="sm" class="text-primary-600" />
                      <span class="font-semibold text-surface-900">{item.name}</span>
                    </div>
                    <span class="font-mono text-surface-500"
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
            <div class="rounded-lg border border-surface-200 bg-surface-50 p-4">
              <div class="mb-1 flex items-center gap-2 text-xs font-semibold text-surface-800">
                <Icon name="info" size="sm" class="text-surface-500" />
                Connection Status
              </div>
              <p class="text-xs leading-relaxed text-surface-600">
                No measurement data received from {source.name} yet. Once connected, incoming health data
                will automatically appear here.
              </p>
            </div>

            <div>
              <h4 class="mb-2 text-xs font-bold tracking-wider text-surface-700 uppercase">
                Setup Instructions
              </h4>
              <div
                class="rounded-lg border border-surface-200 bg-surface-0 p-4 text-xs leading-relaxed text-surface-700"
              >
                {INACTIVE_GUIDES[source.id] ??
                  'Connect this source in system integration settings.'}
              </div>
            </div>
          </div>
        {/if}

        <div class="flex items-center justify-end gap-3 border-t border-surface-200 pt-4">
          <Btn variant="secondary" onclick={() => (open = false)}>Close</Btn>
        </div>
      </div>
    {/if}
  </Modal>
{/if}
