<script lang="ts">
  import { SELF_USER_ID } from '$lib/constants';
  import { db } from '$lib/db/database';
  import type { UserSourcePreference } from '$lib/db/types';
  import Modal from '$components/ui/Modal.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Toggle from '$components/ui/Toggle.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import { updateSourcePreferences } from '$lib/mutations/misc';
  import { useQuery } from '$lib/db/use-query.svelte';

  interface Props {
    open?: boolean;
    metricCode: string;
    metricName: string;
    onClose?: () => void;
  }

  let { open = $bindable(false), metricCode, metricName, onClose }: Props = $props();

  let preferences = $state<UserSourcePreference[]>([]);
  let saving = $state(false);

  const loadedPrefsQuery = useQuery(
    async () => {
      if (!open || !metricCode) return [] as UserSourcePreference[];
      // Fetch user preferences for this metric
      const userPrefs = await db.user_source_preference
        .where('metric_code')
        .equals(metricCode)
        .sortBy('priority_rank');

      // Fetch distinct sources present in measurement table for this metric (sample recent)
      const measurements = await db.measurement
        .where('metric_code')
        .equals(metricCode)
        .limit(100)
        .toArray();

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
            user_id: SELF_USER_ID,
            metric_code: metricCode,
            source: s,
            priority_rank: nextRank++,
            is_enabled: true,
            created_at: new Date().toISOString()
          });
        }
      }

      return combined.sort((a, b) => a.priority_rank - b.priority_rank);
    },
    () => `${open}:${metricCode}`
  );
  const loadedPrefs = $derived(loadedPrefsQuery.value);
  const loading = $derived(loadedPrefsQuery.loading);

  $effect(() => {
    preferences = loadedPrefs ?? [];
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

<Modal
  bind:open
  title={`Metrik-Einstellungen — ${metricName}`}
  subtitle="Quellen-Priorität und automatische Messwert-Auflösung"
  icon="tune"
  onclose={onClose}
  size="md"
>
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <Spinner size="lg" />
    </div>
  {:else}
    <div class="space-y-5 text-xs">
      <div>
        <div class="mb-1 flex items-center justify-between">
          <h3 class="text-xs font-bold tracking-wider text-text-main uppercase">
            Datenquellen-Priorität
          </h3>
          <span class="text-xs text-text-muted">{preferences.length} Quellen erkannt</span>
        </div>
        <p class="mb-4 text-xs text-text-muted">
          Wenn mehrere Quellen gleichzeitig Daten für diese Metrik liefern, hat die oberste Quelle
          Vorrang.
        </p>

        {#if preferences.length === 0}
          <div
            class="rounded-2xl border border-dashed border-border-subtle p-6 text-center text-xs text-text-muted"
          >
            Noch keine externen Datenquellen für {metricName} registriert.
          </div>
        {:else}
          <div class="space-y-2">
            {#each preferences as item, idx (item.source)}
              <div
                class="flex items-center justify-between rounded-2xl border border-border-subtle bg-surface-0 px-4 py-3 shadow-xs transition-colors hover:border-primary"
              >
                <div class="flex items-center gap-3">
                  <span
                    class="flex h-6 w-6 items-center justify-center rounded-full border border-border-subtle bg-surface-50 text-xs font-bold text-text-muted"
                  >
                    {idx + 1}
                  </span>
                  <div>
                    <div class="text-xs font-bold text-text-main">
                      {formatSourceLabel(item.source)}
                    </div>
                    <div class="font-mono text-[10px] text-text-muted">
                      {item.source}
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-lg text-text-muted hover:bg-surface-50 hover:text-text-main disabled:opacity-30"
                    disabled={idx === 0}
                    onclick={() => moveUp(idx)}
                    title="Priorität nach oben"
                  >
                    <Icon name="arrow-upward" size="sm" />
                  </button>
                  <button
                    type="button"
                    class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-lg text-text-muted hover:bg-surface-50 hover:text-text-main disabled:opacity-30"
                    disabled={idx === preferences.length - 1}
                    onclick={() => moveDown(idx)}
                    title="Priorität nach unten"
                  >
                    <Icon name="arrow-downward" size="sm" />
                  </button>
                  <div class="ml-1.5 border-l border-border-subtle pl-2.5">
                    <Toggle checked={item.is_enabled} onchange={() => toggleEnabled(idx)} />
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="flex items-center justify-end gap-2 border-t border-border-subtle pt-3">
        <Btn variant="secondary" size="md" onclick={() => (open = false)}>Abbrechen</Btn>
        <Btn variant="primary" size="md" onclick={handleSave} disabled={saving} loading={saving}>
          Einstellungen speichern
        </Btn>
      </div>
    </div>
  {/if}
</Modal>
