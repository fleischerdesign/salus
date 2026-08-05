<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { UserSourcePreference } from '$lib/db/types';
  import Modal from '$components/ui/Modal.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Toggle from '$components/ui/Toggle.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import { updateSourcePreferences } from '$lib/mutations/misc';

  interface Props {
    open?: boolean;
    metricCode: string;
    metricName: string;
    onClose?: () => void;
  }

  let { open = $bindable(false), metricCode, metricName, onClose }: Props = $props();

  let loading = $state(true);
  let preferences = $state<UserSourcePreference[]>([]);
  let saving = $state(false);

  $effect(() => {
    if (!open || !metricCode) return;
    loading = true;
    const sub = liveQuery(async () => {
      // Fetch user preferences for this metric
      const userPrefs = await db.user_source_preference
        .where('metric_code')
        .equals(metricCode)
        .sortBy('priority_rank');

      // Fetch distinct sources present in measurement table for this metric
      const measurements = await db.measurement.where('metric_code').equals(metricCode).toArray();

      const knownSources = new Set<string>();
      measurements.forEach((m) => {
        if (m.source) knownSources.add(m.source);
      });

      // Combine known sources with existing preferences
      const existingSources = new Set(userPrefs.map((p) => p.source));
      const combined: UserSourcePreference[] = [...userPrefs];

      let nextRank = userPrefs.length + 1;
      for (const s of knownSources) {
        if (!existingSources.has(s)) {
          combined.push({
            id: `temp-${s}`,
            user_id: '',
            metric_code: metricCode,
            source: s,
            priority_rank: nextRank++,
            is_enabled: true,
            created_at: new Date().toISOString()
          });
        }
      }

      return combined.sort((a, b) => a.priority_rank - b.priority_rank);
    }).subscribe((v) => {
      preferences = v ?? [];
      loading = false;
    });

    return () => sub.unsubscribe();
  });

  function moveUp(index: number) {
    if (index <= 0) return;
    const items = [...preferences];
    const temp = items[index];
    items[index] = items[index - 1];
    items[index - 1] = temp;
    items.forEach((item, idx) => {
      item.priority_rank = idx + 1;
    });
    preferences = items;
  }

  function moveDown(index: number) {
    if (index >= preferences.length - 1) return;
    const items = [...preferences];
    const temp = items[index];
    items[index] = items[index + 1];
    items[index + 1] = temp;
    items.forEach((item, idx) => {
      item.priority_rank = idx + 1;
    });
    preferences = items;
  }

  function toggleEnabled(index: number) {
    preferences[index].is_enabled = !preferences[index].is_enabled;
  }

  async function handleSave() {
    saving = true;
    try {
      const payload = preferences.map((p, idx) => ({
        source: p.source,
        priority_rank: idx + 1,
        is_enabled: p.is_enabled
      }));
      await updateSourcePreferences(metricCode, payload);
      open = false;
      onClose?.();
    } finally {
      saving = false;
    }
  }

  const formatSourceLabel = (src: string) => {
    const labels: Record<string, string> = {
      oura: 'Oura Ring',
      apple_health: 'Apple Health',
      health_connect: 'Android Health Connect',
      samsung_health: 'Samsung Health',
      garmin: 'Garmin Connect',
      fitbit: 'Fitbit',
      google_fit: 'Google Fit',
      seed: 'Sample Seed Data',
      manual: 'Manual Input'
    };
    return labels[src] ?? src.replace(/_/g, ' ').toUpperCase();
  };
</script>

<Modal bind:open title="Metric Settings — {metricName}" onclose={onClose} size="md">
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <Spinner size="lg" />
    </div>
  {:else}
    <div class="space-y-6">
      <div>
        <div class="mb-1 flex items-center justify-between">
          <h3 class="text-sm font-bold tracking-wider text-surface-900 uppercase">
            Data Source Priority
          </h3>
          <span class="text-xs text-surface-500">{preferences.length} Known Sources</span>
        </div>
        <p class="mb-4 text-xs text-surface-500">
          When multiple devices record data for this metric at the same time, the top-ranked source
          takes precedence.
        </p>

        {#if preferences.length === 0}
          <div
            class="rounded-lg border border-dashed border-surface-200 p-6 text-center text-xs text-surface-500"
          >
            No external sources detected for {metricName} yet.
          </div>
        {:else}
          <div class="space-y-2">
            {#each preferences as item, idx (item.source)}
              <div
                class="flex items-center justify-between rounded-lg border border-surface-200 bg-surface-0 px-4 py-3 shadow-xs transition-colors hover:border-surface-300"
              >
                <div class="flex items-center gap-3">
                  <span
                    class="flex h-6 w-6 items-center justify-center rounded-full bg-surface-100 text-xs font-bold text-surface-600"
                  >
                    {idx + 1}
                  </span>
                  <div>
                    <div class="text-sm font-semibold text-surface-900">
                      {formatSourceLabel(item.source)}
                    </div>
                    <div class="font-mono text-[11px] text-surface-500">
                      {item.source}
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <button
                    type="button"
                    class="flex h-7 w-7 items-center justify-center rounded-md text-surface-400 hover:bg-surface-100 hover:text-surface-700 disabled:opacity-30"
                    disabled={idx === 0}
                    onclick={() => moveUp(idx)}
                    title="Move Priority Up"
                  >
                    <Icon name="arrow-upward" size="sm" />
                  </button>
                  <button
                    type="button"
                    class="flex h-7 w-7 items-center justify-center rounded-md text-surface-400 hover:bg-surface-100 hover:text-surface-700 disabled:opacity-30"
                    disabled={idx === preferences.length - 1}
                    onclick={() => moveDown(idx)}
                    title="Move Priority Down"
                  >
                    <Icon name="arrow-downward" size="sm" />
                  </button>
                  <div class="ml-2 border-l border-surface-200 pl-3">
                    <Toggle checked={item.is_enabled} onchange={() => toggleEnabled(idx)} />
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="flex items-center justify-end gap-3 border-t border-surface-200 pt-4">
        <Btn variant="secondary" onclick={() => (open = false)}>Cancel</Btn>
        <Btn variant="primary" onclick={handleSave} disabled={saving}>
          {#if saving}<Spinner size="sm" />{/if} Save Preferences
        </Btn>
      </div>
    </div>
  {/if}
</Modal>
