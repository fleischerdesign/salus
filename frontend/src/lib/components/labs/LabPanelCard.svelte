<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  const panelsQuery = useQuery(async () => {
    const [panels, results, markers] = await Promise.all([
      db.lab_panel.toArray(),
      db.lab_result.toArray(),
      db.lab_marker.toArray()
    ]);

    const validPanels = panels.filter((p) => !p.deleted_at);
    const validResults = results.filter((r) => !r.deleted_at);
    const markerMap = new Map(markers.map((m) => [m.code, m]));

    const resultsByPanel = new Map<string, typeof validResults>();
    for (const r of validResults) {
      if (!r.panel_id) continue;
      const list = resultsByPanel.get(r.panel_id) ?? [];
      list.push(r);
      resultsByPanel.set(r.panel_id, list);
    }

    return validPanels.map((p) => {
      const panelResults = resultsByPanel.get(p.id) ?? [];
      return {
        id: p.id,
        title: p.lab_name || 'Labor-Panel',
        date: new Date(p.collection_date).toLocaleDateString('de-DE'),
        labName: p.lab_name || 'Laborbefund',
        markers: panelResults.map((r) => {
          const marker = markerMap.get(r.metric_code);
          return {
            name: marker?.description || r.metric_code,
            value: `${r.value} ${r.unit || ''}`,
            ref: marker?.reference_high ? `< ${marker.reference_high} ${r.unit || ''}` : 'Standard',
            status: r.is_abnormal ? 'abnormal' : 'optimal'
          };
        })
      };
    });
  });

  const panels = $derived(panelsQuery.value ?? []);
  const loading = $derived(panelsQuery.loading);
</script>

<div class="space-y-4">
  {#if loading}
    <div class="py-8 text-center text-xs text-text-muted">Panels werden geladen...</div>
  {:else if panels.length === 0}
    <div
      class="space-y-2 rounded-2xl border border-border-subtle bg-surface-0 p-5 py-8 text-center text-xs text-text-muted shadow-card"
    >
      <Icon name="science" size="lg" class="mx-auto text-text-muted opacity-60" />
      <p class="text-xs font-bold text-text-main">Keine Labor-Panels hinterlegt</p>
      <p class="mx-auto max-w-sm text-[0.6875rem]">
        Hier werden deine strukturierten Laborpanels (z. B. Großes Blutbild, Lipidprofil,
        Schilddrüsenwerte) übersichtlich aufbereitet.
      </p>
    </div>
  {:else}
    {#each panels as panel (panel.id)}
      <div class="rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card">
        <div class="mb-3 flex items-center justify-between">
          <div>
            <div class="flex items-center gap-1.5 text-sm font-bold text-text-main">
              <Icon name="labs" class="text-primary" />
              <span>{panel.title}</span>
            </div>
            <p class="mt-0.5 text-xs text-text-muted">
              Befund vom {panel.date} • {panel.labName}
            </p>
          </div>
          <Badge variant="success">Befund erfasst</Badge>
        </div>

        <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
          {#each panel.markers as m}
            <div class="rounded-xl border border-border-subtle bg-surface-50 p-3">
              <div class="text-xs text-text-muted">{m.name}</div>
              <div class="mt-0.5 font-mono text-base font-bold text-success">
                {m.value}
              </div>
              <div class="mt-0.5 font-mono text-[0.6875rem] text-text-soft">
                Ziel: {m.ref}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/each}
  {/if}
</div>
