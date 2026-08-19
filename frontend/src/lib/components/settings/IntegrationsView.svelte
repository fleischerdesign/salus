<script lang="ts">
  import { db } from '$lib/db/database';
  import { getSourceStats } from '$lib/db/metric-stats';
  import type { MetricDefinition, UserSourcePreference, UserSourceStatus } from '$lib/db/types';
  import { SOURCES, isSourceEnabled, type SourceStatus } from '$lib/sources';
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import SourcePriorityCard from '$components/forms/SourcePriorityCard.svelte';
  import SourceDetailsModal from '$components/forms/SourceDetailsModal.svelte';
  import { updateSourcePreferences } from '$lib/mutations/misc';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { rawGet, rawPost } from '$lib/api/client';
  import { getApiBaseUrl, getAuthHeaders } from '$lib/api/headers';

  // ═══════════════════════════════════════════════════════════════
  // 1. DATA SOURCES & HARDWARE
  // ═══════════════════════════════════════════════════════════════

  let sourceSearchQuery = $state('');
  let matrixSearchQuery = $state('');
  let selectedCategory = $state('all');
  let sourceModalOpen = $state(false);
  let selectedSource = $state<{ id: string; name: string; icon: string; color: string } | null>(
    null
  );

  let metrics = $state<MetricDefinition[]>([]);
  let preferencesMap = $state<Record<string, UserSourcePreference[]>>({});
  let sourceCounts = $state<Record<string, number>>({});
  let savingMetric = $state<string | null>(null);
  let statuses = $state<Record<string, SourceStatus>>({});
  let statusesLoading = $state(true);

  const CATEGORY_OPTIONS = [
    { value: 'all', label: 'Alle Kategorien' },
    { value: 'sleep', label: 'Schlaf & Erholung' },
    { value: 'cardio', label: 'Kardiovaskulär' },
    { value: 'activity', label: 'Aktivität & Sport' },
    { value: 'body', label: 'Körpermaße' }
  ];

  // Reactive Dexie query for synced source statuses
  const syncedStatusQuery = useQuery(() => db.user_source_status.toArray());
  const syncedStatuses = $derived(syncedStatusQuery.value ?? ([] as UserSourceStatus[]));

  async function refreshStatuses() {
    const out: Record<string, SourceStatus> = {};
    for (const src of SOURCES) {
      out[src.id] = await isSourceEnabled(src.id);
    }
    statuses = out;
    statusesLoading = false;
  }

  $effect(() => {
    void syncedStatuses;
    refreshStatuses();
  });

  const sourceDataQuery = useQuery(async () => {
    const allMetrics = await db.metric_definition.toArray();
    const allPrefs = await db.user_source_preference.toArray();
    const srcStats = await getSourceStats();

    const counts: Record<string, number> = {};
    for (const src of SOURCES) {
      counts[src.id] = srcStats[src.id]?.entry_count ?? 0;
    }

    const prefGrouped: Record<string, UserSourcePreference[]> = {};
    allPrefs.forEach((p) => {
      if (!prefGrouped[p.metric_code]) {
        prefGrouped[p.metric_code] = [];
      }
      prefGrouped[p.metric_code].push(p);
    });

    Object.keys(prefGrouped).forEach((code) => {
      prefGrouped[code].sort((a, b) => a.priority_rank - b.priority_rank);
    });

    return {
      allMetrics: allMetrics.sort((a, b) => a.name.localeCompare(b.name)),
      prefGrouped,
      counts
    };
  });

  const sourceData = $derived(sourceDataQuery.value);
  const loading = $derived(sourceDataQuery.loading);

  $effect(() => {
    const val = sourceData;
    if (val) {
      metrics = val.allMetrics;
      preferencesMap = val.prefGrouped;
      sourceCounts = val.counts;
    }
  });

  let sortedAndFilteredSources = $derived.by(() => {
    const query = sourceSearchQuery.trim().toLowerCase();
    let sources = SOURCES.filter((s) => {
      if (!query) return true;
      return s.name.toLowerCase().includes(query) || s.id.toLowerCase().includes(query);
    });

    return sources.sort((a, b) => {
      const countA = sourceCounts[a.id] ?? 0;
      const countB = sourceCounts[b.id] ?? 0;
      const activeA = statuses[a.id]?.enabled ? 1 : 0;
      const activeB = statuses[b.id]?.enabled ? 1 : 0;

      if (activeA !== activeB) return activeB - activeA;
      if (countA !== countB) return countB - countA;
      return a.name.localeCompare(b.name);
    });
  });

  function getMetricItems(metricCode: string): UserSourcePreference[] {
    return preferencesMap[metricCode] ?? [];
  }

  function matchesCategory(metricCode: string, cat: string): boolean {
    if (cat === 'all') return true;
    const lower = metricCode.toLowerCase();
    if (cat === 'sleep')
      return lower.includes('sleep') || lower.includes('hrv') || lower.includes('rem');
    if (cat === 'cardio')
      return (
        lower.includes('heart') ||
        lower.includes('pulse') ||
        lower.includes('bp') ||
        lower.includes('blood')
      );
    if (cat === 'activity')
      return (
        lower.includes('step') ||
        lower.includes('calorie') ||
        lower.includes('distance') ||
        lower.includes('vo2')
      );
    if (cat === 'body')
      return (
        lower.includes('weight') ||
        lower.includes('fat') ||
        lower.includes('waist') ||
        lower.includes('muscle')
      );
    return true;
  }

  let filteredMatrixMetrics = $derived.by(() => {
    const query = matrixSearchQuery.trim().toLowerCase();
    return metrics.filter((m) => {
      const matchesSearch =
        !query || m.name.toLowerCase().includes(query) || m.code.toLowerCase().includes(query);
      const matchesCat = matchesCategory(m.code, selectedCategory);
      return matchesSearch && matchesCat;
    });
  });

  async function handleMetricUpdate(metricCode: string, items: UserSourcePreference[]) {
    preferencesMap[metricCode] = items;
    savingMetric = metricCode;
    try {
      const payload = items.map((p, idx) => ({
        source: p.source,
        priority_rank: idx + 1,
        is_enabled: p.is_enabled
      }));
      await updateSourcePreferences(metricCode, payload);
    } finally {
      savingMetric = null;
    }
  }

  async function applyToCategory(sourceMetricCode: string) {
    const templateItems = getMetricItems(sourceMetricCode);
    const templateOrder = templateItems.map((p) => p.source);

    const sisterMetrics = metrics.filter((m) =>
      matchesCategory(m.code, selectedCategory === 'all' ? 'sleep' : selectedCategory)
    );

    for (const target of sisterMetrics) {
      const currentItems = getMetricItems(target.code);
      const currentMap = new Map(currentItems.map((i) => [i.source, i]));

      const reordered: UserSourcePreference[] = [];
      let rank = 1;
      for (const s of templateOrder) {
        const match = currentMap.get(s);
        if (match) {
          reordered.push({ ...match, priority_rank: rank++ });
          currentMap.delete(s);
        }
      }
      for (const [, remaining] of currentMap) {
        reordered.push({ ...remaining, priority_rank: rank++ });
      }

      await handleMetricUpdate(target.code, reordered);
    }
  }

  function openSourceModal(src: { id: string; name: string; icon: string; color: string }) {
    selectedSource = src;
    sourceModalOpen = true;
  }

  // ═══════════════════════════════════════════════════════════════
  // 2. PERSONAL API TOKENS & WEBHOOKS
  // ═══════════════════════════════════════════════════════════════

  interface ServerApiToken {
    id: string;
    label: string;
    token_prefix: string;
    scopes: string[];
    is_active: boolean;
    last_used_at: string | null;
    created_at: string | null;
  }

  let serverTokens = $state<ServerApiToken[]>([]);
  let tokensLoading = $state(true);
  let newTokenName = $state('');
  let newTokenScope = $state('ingest:write');
  let newlyGeneratedToken = $state<string | null>(null);
  let tokenCopied = $state(false);
  let isCreatingToken = $state(false);

  const tokenScopeOptions = [
    { value: 'ingest:write', label: 'ingest:write (Messwerte & Sensordaten schreiben)' },
    { value: 'read:metrics', label: 'read:metrics (Metriken nur lesen)' },
    { value: 'admin', label: 'Full Admin (Vollzugriff auf alle APIs)' }
  ];

  async function loadTokens() {
    tokensLoading = true;
    try {
      const res = await rawGet('/api/v1/settings/account');
      if (res.ok) {
        const data = await res.json();
        serverTokens = data.api_tokens ?? [];
      }
    } catch {
      // Offline fallback: load from Dexie db.api_token
      const local = await db.api_token.toArray();
      serverTokens = local.map((t) => ({
        id: t.id,
        label: t.label,
        token_prefix: t.token_prefix,
        scopes: Array.isArray(t.scopes)
          ? t.scopes
          : typeof t.scopes === 'string'
            ? (t.scopes as string).split(',').map((s) => s.trim())
            : [],
        is_active: t.is_active,
        last_used_at: t.last_used_at ?? null,
        created_at: t.created_at ?? null
      }));
    } finally {
      tokensLoading = false;
    }
  }

  $effect(() => {
    loadTokens();
  });

  async function createToken() {
    if (!newTokenName.trim() || isCreatingToken) return;
    isCreatingToken = true;
    try {
      const res = await rawPost('/api/v1/settings/tokens', {
        label: newTokenName.trim(),
        scopes: [newTokenScope]
      });
      if (res.ok) {
        const data = await res.json();
        newlyGeneratedToken = data.token;
        tokenCopied = false;
        newTokenName = '';
        await loadTokens();
      }
    } catch (err) {
      console.error('Failed to create token:', err);
    } finally {
      isCreatingToken = false;
    }
  }

  async function revokeToken(tokenId: string) {
    if (!confirm('Möchtest du diesen API-Token wirklich unwiderruflich deaktivieren?')) return;
    try {
      const base = getApiBaseUrl();
      await fetch(`${base}/api/v1/settings/tokens/${tokenId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      await loadTokens();
    } catch (err) {
      console.error('Failed to revoke token:', err);
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    tokenCopied = true;
    setTimeout(() => {
      tokenCopied = false;
    }, 2500);
  }

  let webhookUrl = $derived(`${getApiBaseUrl()}/api/v1/webhook`);
</script>

{#if loading}
  <div class="flex justify-center py-20"><Spinner size="lg" /></div>
{:else}
  <div class="space-y-8">
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- SECTION 1: WEARABLES & HARDWARE SENSORS                     -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div
      class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
    >
      <div
        class="flex flex-col gap-3 border-b border-[var(--border-subtle)]/60 pb-3 md:flex-row md:items-end md:justify-between"
      >
        <div>
          <div class="flex items-center gap-2 text-base font-extrabold text-[var(--text-main)]">
            <Icon name="sensors" class="text-[var(--color-primary)]" />
            <h2>Sensoren &amp; Hardware-Quellen</h2>
          </div>
          <p class="mt-0.5 text-xs text-[var(--text-muted)]">
            Direkte Schnittstellen für Wearables, Smartwatches, Labor-Importe und Umgebungssensoren
          </p>
        </div>
        <div class="w-full shrink-0 md:w-64">
          <Input icon="search" placeholder="Quellen filtern…" bind:value={sourceSearchQuery} />
        </div>
      </div>

      {#if sortedAndFilteredSources.length === 0}
        <div class="py-8">
          <EmptyState
            icon="search"
            title="Keine Datenquellen gefunden"
            description="Keine Plattformen passend zu '{sourceSearchQuery}'"
          />
        </div>
      {:else}
        <div class="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-3">
          {#each sortedAndFilteredSources as src (src.id)}
            {@const count = sourceCounts[src.id] ?? 0}
            {@const status = statuses[src.id]}
            {@const isActive = status?.enabled ?? false}
            <div
              role="button"
              tabindex="0"
              onclick={() => openSourceModal(src)}
              onkeydown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') openSourceModal(src);
              }}
              class="group cursor-pointer rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 transition-all hover:border-[var(--color-primary)]/50 hover:bg-[var(--bg-surface-100)]"
            >
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-3">
                  <div
                    class="flex h-10 w-10 items-center justify-center rounded-xl text-white shadow-xs transition-all {isActive
                      ? ''
                      : 'opacity-60 grayscale'}"
                    style="background-color: {isActive ? src.color : 'var(--text-muted)'};"
                  >
                    <Icon name={src.icon} size="md" />
                  </div>
                  <div>
                    <h3
                      class="text-xs font-bold {isActive
                        ? 'text-[var(--text-main)]'
                        : 'text-[var(--text-muted)]'}"
                    >
                      {src.name}
                    </h3>
                    <span class="font-mono text-[0.625rem] text-[var(--text-muted)]">{src.id}</span>
                  </div>
                </div>

                {#if statusesLoading}
                  <span
                    class="inline-flex items-center rounded-full border border-[var(--border-subtle)] bg-[var(--bg-surface-100)] px-2 py-0.5 text-[0.625rem] font-medium text-[var(--text-muted)]"
                  >
                    …
                  </span>
                {:else if isActive}
                  <Badge variant="success" class="text-[0.625rem]">
                    <span class="mr-1 h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    {status?.reason === 'has_data' ? 'Aktiv' : 'Verbunden'}
                  </Badge>
                {:else}
                  <Badge variant="default" class="text-[0.625rem]">
                    {status?.reason === 'missing_permissions'
                      ? 'Berechtigung fehlt'
                      : 'Nicht verbunden'}
                  </Badge>
                {/if}
              </div>

              <div
                class="mt-3 flex items-center justify-between border-t border-[var(--border-subtle)]/60 pt-2 text-[0.6875rem]"
              >
                <span class="text-[var(--text-muted)]">Erfasste Messwerte</span>
                <span
                  class="font-bold {isActive
                    ? 'text-[var(--text-main)]'
                    : 'font-normal text-[var(--text-muted)]'} tabular-nums"
                >
                  {count > 0 ? count.toLocaleString('de-DE') : '—'}
                </span>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- SECTION 2: MULTI-SOURCE PRIORITY MATRIX                     -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div
      class="space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
    >
      <div
        class="flex flex-col gap-3 border-b border-[var(--border-subtle)]/60 pb-3 md:flex-row md:items-end md:justify-between"
      >
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 text-base font-extrabold text-[var(--text-main)]">
            <Icon name="tune" class="text-[var(--color-primary)]" />
            <h2>Quellen-Prioritäts-Matrix</h2>
          </div>
          <p class="mt-0.5 text-xs text-[var(--text-muted)]">
            Automatische Konfliktlösung und Rangfolge bei Metriken mit mehreren aktiven Geräten
          </p>
        </div>

        <div class="flex shrink-0 flex-col gap-2.5 sm:flex-row sm:items-center">
          <div class="w-full sm:w-48">
            <Input icon="search" placeholder="Metriken filtern…" bind:value={matrixSearchQuery} />
          </div>
          <div class="w-full sm:w-48">
            <Select name="category" options={CATEGORY_OPTIONS} bind:value={selectedCategory} />
          </div>
        </div>
      </div>

      {#if filteredMatrixMetrics.length === 0}
        <div class="py-8">
          <EmptyState
            icon="tune"
            title="Keine Metriken gefunden"
            description="Keine Metriken passend zu deiner Suchanfrage oder Kategorie-Auswahl."
          />
        </div>
      {:else}
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {#each filteredMatrixMetrics as metric (metric.code)}
            {@const items = getMetricItems(metric.code)}
            <SourcePriorityCard
              {metric}
              {items}
              saving={savingMetric === metric.code}
              onUpdate={(newItems) => handleMetricUpdate(metric.code, newItems)}
              onApplyToCategory={() => applyToCategory(metric.code)}
            />
          {/each}
        </div>
      {/if}
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- SECTION 3: PERSONAL API TOKENS & WEBHOOKS                   -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div
      class="space-y-5 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-xs"
    >
      <div class="border-b border-[var(--border-subtle)]/60 pb-3">
        <div class="flex items-center gap-2 text-base font-extrabold text-[var(--text-main)]">
          <Icon name="key" class="text-[var(--color-primary)]" />
          <h2>Persönliche API-Tokens &amp; Webhook-Ingestion</h2>
        </div>
        <p class="mt-0.5 text-xs text-[var(--text-muted)]">
          Automatisierter Datenimport für Home Assistant, iOS Kurzbefehle, cURL und externe Skripte
        </p>
      </div>

      <!-- Token Generator Form -->
      <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4">
        <h3 class="text-xs font-extrabold tracking-wider text-[var(--text-main)] uppercase">
          Neuen API-Token erstellen
        </h3>
        <div class="mt-3 grid grid-cols-1 items-end gap-3 sm:grid-cols-12">
          <div class="sm:col-span-6">
            <Input
              label="Bezeichnung"
              placeholder="z. B. Home Assistant Schlaf-Sensor"
              bind:value={newTokenName}
            />
          </div>
          <div class="sm:col-span-4">
            <Select
              label="Berechtigungs-Scope"
              options={tokenScopeOptions}
              bind:value={newTokenScope}
            />
          </div>
          <div class="sm:col-span-2">
            <Btn
              variant="primary"
              class="w-full"
              disabled={!newTokenName.trim() || isCreatingToken}
              onclick={createToken}
            >
              {#if isCreatingToken}
                <Spinner size="sm" />
              {:else}
                <span>+ Erstellen</span>
              {/if}
            </Btn>
          </div>
        </div>

        <!-- Newly Generated Token Alert -->
        {#if newlyGeneratedToken}
          <div
            class="mt-4 space-y-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3.5"
          >
            <div class="flex items-center justify-between">
              <span class="text-xs font-extrabold text-emerald-600 dark:text-emerald-400">
                &check; Neuer API-Token erfolgreich generiert!
              </span>
              <button
                type="button"
                onclick={() => copyToClipboard(newlyGeneratedToken!)}
                class="flex cursor-pointer items-center gap-1 rounded-lg bg-emerald-600 px-2.5 py-1 text-xs font-bold text-white shadow-xs transition-all hover:bg-emerald-700"
              >
                <Icon name={tokenCopied ? 'check' : 'content-copy'} size="sm" />
                <span>{tokenCopied ? 'Kopiert!' : 'Kopieren'}</span>
              </button>
            </div>
            <div
              class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2 font-mono text-xs break-all text-[var(--text-main)] select-all"
            >
              {newlyGeneratedToken}
            </div>
            <p class="text-[0.6875rem] text-[var(--text-muted)]">
              &excl; Bitte kopiere diesen Token jetzt. Er wird aus Sicherheitsgründen nie wieder im
              Klartext angezeigt.
            </p>
          </div>
        {/if}
      </div>

      <!-- Active Tokens List -->
      <div class="space-y-3">
        <h3 class="text-xs font-extrabold tracking-wider text-[var(--text-main)] uppercase">
          Aktive API-Tokens
        </h3>

        {#if tokensLoading}
          <div class="flex justify-center py-6"><Spinner size="md" /></div>
        {:else if serverTokens.length === 0}
          <p class="text-xs text-[var(--text-muted)] italic">Noch keine API-Tokens generiert.</p>
        {:else}
          <div class="space-y-2.5">
            {#each serverTokens as token (token.id)}
              <div
                class="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5"
              >
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-extrabold text-[var(--text-main)]">{token.label}</span
                    >
                    <Badge
                      variant={token.is_active ? 'success' : 'default'}
                      class="text-[0.625rem]"
                    >
                      {token.is_active ? 'Aktiv' : 'Widerrufen'}
                    </Badge>
                  </div>
                  <div
                    class="flex flex-wrap items-center gap-2 font-mono text-[0.6875rem] text-[var(--text-muted)]"
                  >
                    <span class="rounded-md bg-[var(--bg-surface-100)] px-1.5 py-0.5"
                      >{token.token_prefix}••••</span
                    >
                    <span>&bull;</span>
                    <span>Scopes: {token.scopes?.join(', ') || 'ingest:write'}</span>
                    {#if token.last_used_at}
                      <span>&bull;</span>
                      <span
                        >Zuletzt aktiv: {new Date(token.last_used_at).toLocaleDateString(
                          'de-DE'
                        )}</span
                      >
                    {/if}
                  </div>
                </div>

                <Btn
                  variant="danger"
                  size="sm"
                  class="px-3 py-1 text-xs"
                  onclick={() => revokeToken(token.id)}
                >
                  Widerrufen
                </Btn>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Webhook Ingestion Guide -->
      <div
        class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5 text-xs font-extrabold text-[var(--text-main)]">
            <Icon name="webhook" size="sm" class="text-[var(--color-primary)]" />
            <span>Webhook-Endpunkt &amp; Ingestion-Format</span>
          </div>
          <button
            type="button"
            onclick={() => copyToClipboard(webhookUrl)}
            class="flex cursor-pointer items-center gap-1 text-xs font-bold text-[var(--color-primary)] hover:underline"
          >
            <Icon name="content-copy" size="sm" />
            <span>Endpunkt-URL kopieren</span>
          </button>
        </div>

        <div
          class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-3 font-mono text-[0.6875rem] break-all text-[var(--text-main)] select-all"
        >
          POST {webhookUrl}
        </div>

        <div class="space-y-1 text-xs text-[var(--text-muted)]">
          <p class="font-semibold text-[var(--text-main)]">Header zur Authentifizierung:</p>
          <code
            class="block rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2 font-mono text-[0.6875rem] text-[var(--text-soft)]"
          >
            X-API-Token: salus_pat_DEIN_TOKEN_HIER
          </code>
        </div>
      </div>
    </div>
  </div>
{/if}

{#if selectedSource}
  <SourceDetailsModal
    bind:open={sourceModalOpen}
    source={selectedSource}
    count={sourceCounts[selectedSource.id] ?? 0}
    onStatusChange={refreshStatuses}
  />
{/if}
