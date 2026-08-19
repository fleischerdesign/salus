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
  import Badge from '$components/ui/Badge.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import { toast } from '$components/ui/toast-state.svelte';
  import { toastSettings } from '$stores/toast-settings.svelte';

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

  $effect(() => {
    const val = sourceData;
    if (val) {
      metricsSupplied = val.supplied;
      lastSyncTime = val.lastTime;
    }
  });

  async function refreshStatus() {
    if (!source) return;
    sourceStatus = await isSourceEnabled(source.id);
    onStatusChange?.();
  }

  $effect(() => {
    if (open && source) {
      refreshStatus();
    }
  });

  async function handleOpenSettings() {
    await healthSyncService.openHealthConnectSettings();
  }

  async function handleRequestPermissions() {
    requestingPerms = true;
    syncFeedback = null;
    try {
      const granted = await healthSyncService.requestPermissions();
      healthConnectGranted = granted;
      await loadPermissionState();
      await reportDeviceSourceStatus();
      syncFeedback = {
        type: granted ? 'success' : 'error',
        text: granted
          ? 'Health Connect Berechtigungen erfolgreich erteilt.'
          : 'Einige oder alle Health Connect Berechtigungen wurden abgelehnt.'
      };
      await refreshStatus();
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : String(e);
      syncFeedback = { type: 'error', text: err };
    } finally {
      requestingPerms = false;
    }
  }

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
        toast(`Health Connect Synchronisation fehlgeschlagen: ${err}`, 'error');
      }
    } finally {
      syncing = false;
    }
  }

  const INACTIVE_GUIDES: Record<string, string> = {
    health_connect:
      'Öffne Android-Einstellungen -> Datenschutz -> Health Connect -> Gewähre Salus Lese- und Schreibzugriff für Gesundheits- und Fitnessdaten.',
    apple_health:
      'Öffne die Apple Health App auf iOS -> Tippe auf Teilen -> Apps & Dienste -> Salus -> Alle Kategorien aktivieren.',
    samsung_health:
      'Stelle sicher, dass Samsung Health mit Health Connect auf Android verbunden ist, um Schritte und Schlafdaten automatisch zu übertragen.',
    oura: 'Hinterlege deinen Oura Ring Personal Access Token oder richte den Webhook-Push in den Salus Einstellungen ein.',
    garmin:
      'Verbinde deine Garmin Connect Schnittstelle oder nutze den automatischen Health Connect Datenabgleich.',
    manual:
      'Erfasse Messwerte manuell über den Button „+ Neuer Eintrag“ auf jeder Metrik-Detailseite.',
    seed: 'Verwende den Befehl „just seed-dev“ im Terminal, um Entwicklungs-Testdaten zu generieren.',
    webhook:
      'Sende JSON-Payloads via POST /api/v1/webhook mit dem Header X-API-Token: salus_pat_...'
  };
</script>

{#if source}
  <Modal bind:open title="{source.name} — Quellen-Diagnose" onclose={onClose} size="md">
    {#if loading}
      <div class="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    {:else}
      <div class="space-y-5">
        <!-- Header Info Card -->
        <div
          class="flex items-center justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-11 w-11 items-center justify-center rounded-xl text-white shadow-xs"
              style="background-color: {count > 0 ? source.color : 'var(--text-muted)'};"
            >
              <Icon name={source.icon} size="md" />
            </div>
            <div>
              <h3 class="text-sm font-extrabold text-[var(--text-main)]">
                {source.name}
              </h3>
              <span class="font-mono text-xs text-[var(--text-muted)]">ID: {source.id}</span>
            </div>
          </div>

          <div>
            {#if sourceStatus?.enabled}
              <Badge variant="success" class="text-xs">
                <span class="mr-1 h-1.5 w-1.5 rounded-full bg-emerald-500"></span> Verbunden
              </Badge>
            {:else}
              <Badge variant="default" class="text-xs">
                {sourceStatus?.reason === 'missing_permissions'
                  ? 'Berechtigung fehlt'
                  : 'Nicht verbunden'}
              </Badge>
            {/if}
          </div>
        </div>

        {#if sourceStatus?.detail}
          <p
            class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3.5 py-2.5 text-xs text-[var(--text-muted)]"
          >
            {sourceStatus.detail}
          </p>
        {/if}

        {#if syncFeedback}
          <div
            class="rounded-xl border p-3.5 text-xs font-semibold {syncFeedback.type === 'success'
              ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
              : 'border-rose-500/30 bg-rose-500/10 text-rose-600 dark:text-rose-400'}"
          >
            {syncFeedback.text}
          </div>
        {/if}

        <!-- NATIVE HEALTH CONNECT CONTROLS -->
        {#if source.id === 'health_connect' && isNativeAndroid}
          <div
            class="space-y-3 rounded-2xl border border-[var(--color-primary)]/30 bg-[var(--color-primary-soft)]/10 p-4"
          >
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h4 class="text-xs font-extrabold text-[var(--text-main)]">
                  Android Health Connect Schnittstelle
                </h4>
                <p class="mt-0.5 text-[0.6875rem] text-[var(--text-muted)]">
                  Direkte native Verbindung zu Google Health Connect &amp; Samsung Health
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
                    Autorisieren
                  </Btn>
                {/if}
                <Btn variant="primary" size="sm" loading={syncing} onclick={handleSyncNow}>
                  <Icon name="sync" size="sm" class="mr-1" />
                  Jetzt synchronisieren
                </Btn>
              </div>
            </div>

            {#if permissionState && permissionState.missingLabels.length > 0}
              <div
                class="space-y-2 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-3"
              >
                <div class="flex items-center justify-between gap-2">
                  <h5 class="text-xs font-bold text-[var(--text-main)]">
                    Datenzugriff &bull; {permissionState.granted} Kategorien lesbar
                  </h5>
                  <Btn variant="secondary" size="sm" onclick={handleOpenSettings}>
                    <Icon name="settings" size="sm" class="mr-1" />
                    System-Einstellungen
                  </Btn>
                </div>
                <p class="text-[0.6875rem] leading-relaxed text-[var(--text-muted)]">
                  Kategorien, die auf diesem Smartphone nicht verfügbar sind, werden automatisch
                  übersprungen.
                </p>
                <details class="mt-1">
                  <summary
                    class="cursor-pointer text-[0.6875rem] font-bold text-[var(--color-primary)] select-none hover:underline"
                  >
                    {permissionState.missingLabels.length} übersprungene Kategorien anzeigen
                  </summary>
                  <div class="mt-2 flex flex-wrap gap-1.5">
                    {#each permissionState.missingLabels as label (label)}
                      <span
                        class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-100)] px-2 py-0.5 text-[0.625rem] font-medium text-[var(--text-muted)]"
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
          <div
            class="space-y-2 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <Spinner size="sm" />
                <h5 class="text-xs font-bold text-[var(--text-main)]">
                  Health Connect Verlauf wird importiert…
                </h5>
              </div>
              {#if (healthSyncUi.seedProgress?.done ?? 0) > 0}
                <span class="font-mono text-xs font-bold text-[var(--text-main)] tabular-nums">
                  {(healthSyncUi.seedProgress?.done ?? 0).toLocaleString('de-DE')} Messwerte
                </span>
              {/if}
            </div>
            <div class="h-1.5 w-full overflow-hidden rounded-full bg-[var(--bg-surface-200)]">
              <div class="h-1.5 w-full animate-pulse rounded-full bg-[var(--color-primary)]"></div>
            </div>
          </div>
        {/if}

        {#if count > 0}
          <!-- ACTIVE SOURCE DIAGNOSTICS -->
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div
                class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5"
              >
                <span class="text-[0.6875rem] font-bold text-[var(--text-muted)]"
                  >Gesamtzahl Messwerte</span
                >
                <div class="mt-1 text-base font-extrabold text-[var(--text-main)] tabular-nums">
                  {count.toLocaleString('de-DE')}
                </div>
              </div>
              <div
                class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5"
              >
                <span class="text-[0.6875rem] font-bold text-[var(--text-muted)]"
                  >Letzter Datenimport</span
                >
                <div class="mt-1 truncate text-xs font-semibold text-[var(--text-main)]">
                  {lastSyncTime ? new Date(lastSyncTime).toLocaleString('de-DE') : 'Kürzlich'}
                </div>
              </div>
            </div>

            <div class="space-y-2">
              <h4 class="text-xs font-extrabold tracking-wider text-[var(--text-main)] uppercase">
                Bereitgestellte Metriken ({metricsSupplied.length})
              </h4>
              <div class="max-h-48 space-y-1.5 overflow-y-auto pr-1">
                {#each metricsSupplied as item (item.code)}
                  <div
                    class="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3 py-2 text-xs"
                  >
                    <div class="flex items-center gap-2">
                      <Icon
                        name="monitoring"
                        size="sm"
                        class="shrink-0 text-[var(--color-primary)]"
                      />
                      <span class="font-semibold text-[var(--text-main)]">{item.name}</span>
                    </div>
                    <span class="font-mono text-[0.6875rem] text-[var(--text-muted)] tabular-nums">
                      {item.count.toLocaleString('de-DE')} Einträge
                    </span>
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {:else}
          <!-- INACTIVE SOURCE DIAGNOSTICS & SETUP GUIDE -->
          <div class="space-y-4">
            <div
              class="space-y-1.5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4"
            >
              <div class="flex items-center gap-2 text-xs font-bold text-[var(--text-main)]">
                <Icon name="info" size="sm" class="text-[var(--color-primary)]" />
                <span>Verbindungsstatus</span>
              </div>
              <p class="text-xs leading-relaxed text-[var(--text-muted)]">
                Bisher wurden noch keine Messdaten von {source.name} empfangen.
              </p>
            </div>

            <div class="space-y-1.5">
              <h4 class="text-xs font-extrabold tracking-wider text-[var(--text-main)] uppercase">
                Einrichtungs-Hinweise
              </h4>
              <div
                class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 text-xs leading-relaxed text-[var(--text-main)]"
              >
                {INACTIVE_GUIDES[source.id] ??
                  'Verbinde diese Quelle in den Geräteeinstellungen deines Systems.'}
              </div>
            </div>
          </div>
        {/if}

        <div class="flex items-center justify-end border-t border-[var(--border-subtle)]/60 pt-4">
          <Btn variant="secondary" onclick={() => (open = false)}>Schließen</Btn>
        </div>
      </div>
    {/if}
  </Modal>
{/if}
