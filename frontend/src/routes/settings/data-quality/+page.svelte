<script lang="ts">
  import { db } from '$lib/db/database';
  import type { DataQualityFlag, MetricDefinition, UserProfile } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Toggle from '$components/ui/Toggle.svelte';
  import EmptyState from '$components/ui/EmptyState.svelte';
  import { toast } from '$components/ui/toast-state.svelte';
  import { runDataQualityCheck, acknowledgeDataQualityFlag } from '$lib/mutations/data-quality';
  import { updateProfile } from '$lib/mutations/account';
  import { useQuery } from '$lib/db/use-query.svelte';

  const flagsQuery = useQuery(() => db.data_quality_flag.toArray());
  const flags = $derived(flagsQuery.value);
  const loading = $derived(flagsQuery.loading);

  const definitionsQuery = useQuery(() => db.metric_definition.toArray());
  const definitions = $derived(definitionsQuery.value);

  const profileQuery = useQuery(() => db.user_profile.toArray());
  const profile = $derived<Partial<UserProfile>>(profileQuery.value?.[0] ?? {});

  let checking = $state(false);

  const sortedFlags = $derived(
    (flags ?? []).sort((a, b) => (b.created_at ?? '').localeCompare(a.created_at ?? ''))
  );

  const definitionMap = $derived.by(() => {
    const map: Record<string, MetricDefinition> = {};
    for (const d of definitions ?? []) map[d.code] = d;
    return map;
  });

  const boundedMetrics = $derived(
    (definitions ?? [])
      .filter((d) => d.min_value != null || d.max_value != null)
      .sort((a, b) => a.name.localeCompare(b.name))
  );

  const KIND_LABELS: Record<string, string> = {
    hard_bound: 'Hard bound',
    cross_source: 'Cross-source',
    anomaly: 'Anomaly'
  };

  const KIND_VARIANTS: Record<string, 'warning' | 'error'> = {
    hard_bound: 'warning',
    cross_source: 'warning',
    anomaly: 'error'
  };

  const TOGGLES: { key: keyof UserProfile; label: string }[] = [
    { key: 'dq_notify_hard_bound', label: 'Hard-bound alerts' },
    { key: 'dq_notify_cross_source', label: 'Cross-source alerts' },
    { key: 'dq_notify_anomaly', label: 'Anomaly alerts' }
  ];

  function metricName(flag: DataQualityFlag): string {
    if (!flag.metric_code) return '';
    return definitionMap[flag.metric_code]?.name ?? flag.metric_code;
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  }

  async function handleCheck() {
    checking = true;
    const { ok, error } = await runDataQualityCheck();
    checking = false;
    if (ok) toast('Data quality check completed', 'success');
    else toast(error ?? 'Check failed', 'error');
  }

  async function handleToggle(key: keyof UserProfile, value: boolean) {
    const { ok } = await updateProfile({ [key]: value });
    if (!ok) toast('Failed to save preference', 'error');
  }

  async function handleAcknowledge(flagId: string) {
    const { ok, error } = await acknowledgeDataQualityFlag(flagId);
    if (!ok) toast(error ?? 'Failed to mark as seen', 'error');
  }
</script>

<div class="space-y-6">
  <Card title="Steuerung">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="max-w-xl space-y-2 text-sm text-surface-600">
        <p>
          Salus prüft eingehende Messwerte auf Plausibilität und weist dich auf mögliche
          Fehleingaben oder Sensorfehler hin — ohne deine Daten zu blockieren.
        </p>
        <ul class="list-disc pl-5 text-xs text-surface-500">
          <li><strong>Hard bounds</strong> — Werte außerhalb plausibler Grenzen.</li>
          <li>
            <strong>Cross-source</strong> — widersprüchliche Werte aus verschiedenen Quellen am selben
            Tag.
          </li>
          <li><strong>Anomalie</strong> — Sprünge gegen deine persönliche Baseline.</li>
        </ul>
      </div>
      <Btn variant="primary" onclick={handleCheck} loading={checking}>
        <Icon name="refresh" size="sm" /> Jetzt prüfen
      </Btn>
    </div>
  </Card>

  <Card title="Benachrichtigungen">
    <div class="space-y-3">
      {#each TOGGLES as toggle}
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-sm font-medium text-surface-900">{toggle.label}</p>
            <p class="text-xs text-surface-500">
              {profile[toggle.key] === false
                ? 'Benachrichtigung deaktiviert.'
                : 'Bei Auffälligkeiten benachrichtigen.'}
            </p>
          </div>
          <Toggle
            name={toggle.key}
            checked={profile[toggle.key] !== false}
            onchange={(v) => handleToggle(toggle.key, v)}
          />
        </div>
      {/each}
    </div>
  </Card>

  <Card title="Befunde" padding={false} class="overflow-hidden">
    {#if loading}
      <div class="flex justify-center py-16">
        <Spinner />
      </div>
    {:else if sortedFlags.length === 0}
      <EmptyState
        icon="health-and-safety"
        title="Keine Auffälligkeiten"
        description="Bisher wurden keine unplausiblen Messwerte erkannt."
      />
    {:else}
      <div class="divide-y divide-surface-100">
        {#each sortedFlags as flag (flag.id)}
          <div
            class="flex items-start justify-between gap-3 px-6 py-3 {flag.resolved_at
              ? 'opacity-60'
              : ''}"
          >
            <div class="min-w-0 space-y-1">
              <div class="flex items-center gap-2">
                <Badge variant={KIND_VARIANTS[flag.kind] ?? 'warning'}>
                  {KIND_LABELS[flag.kind] ?? flag.kind}
                </Badge>
                {#if metricName(flag)}
                  <span class="text-sm font-semibold text-surface-900">{metricName(flag)}</span>
                {/if}
                {#if flag.resolved_at}
                  <span class="inline-flex items-center gap-1 text-xs text-surface-400">
                    <Icon name="check" size="sm" /> Gesehen
                  </span>
                {/if}
              </div>
              <p class="text-sm text-surface-600">{flag.message}</p>
            </div>
            <div class="flex shrink-0 items-center gap-2">
              <span class="text-xs text-surface-400">{formatDate(flag.created_at)}</span>
              {#if !flag.resolved_at}
                <button
                  class="rounded-md px-2 py-1 text-xs font-semibold text-primary-600 transition-colors hover:bg-primary-50"
                  onclick={() => handleAcknowledge(flag.id)}
                >
                  Als gesehen
                </button>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </Card>

  {#if boundedMetrics.length > 0}
    <Card title="Geprüfte Metriken" padding={false} class="overflow-hidden">
      <div class="divide-y divide-surface-100">
        {#each boundedMetrics as metric (metric.code)}
          <div class="flex items-center justify-between gap-3 px-6 py-3">
            <span class="text-sm text-surface-800">{metric.name}</span>
            <span class="text-xs text-surface-500">
              {metric.min_value ?? '−∞'}–{metric.max_value ?? '∞'}
              {metric.unit}
            </span>
          </div>
        {/each}
      </div>
    </Card>
  {/if}
</div>
