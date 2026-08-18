<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  let unitMode = $state<'mg/dL' | 'mmol/L'>('mg/dL');

  const labQuery = useQuery(async () => {
    const [results, markers] = await Promise.all([
      db.lab_result.toArray(),
      db.lab_marker.toArray()
    ]);

    const validResults = results.filter((r) => !r.deleted_at);
    const markerMap = new Map(markers.map((m) => [m.code, m]));

    // Group by metric_code
    const byMarker = new Map<string, typeof validResults>();
    for (const res of validResults) {
      const list = byMarker.get(res.metric_code) ?? [];
      list.push(res);
      byMarker.set(res.metric_code, list);
    }

    const rows = [];
    for (const [code, list] of byMarker.entries()) {
      const marker = markerMap.get(code);
      list.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      const latest = list[0];
      const prev1 = list[1];
      const prev2 = list[2];

      rows.push({
        name: marker?.description || code,
        reference: marker?.reference_high
          ? `< ${marker.reference_high} ${latest.unit || ''}`
          : 'Standard',
        valCurrent: {
          val: latest.value,
          unit: latest.unit || ''
        },
        valOld1: prev1 ? { val: prev1.value, unit: prev1.unit || '' } : null,
        valOld2: prev2 ? { val: prev2.value, unit: prev2.unit || '' } : null,
        status: latest.is_abnormal ? 'abnormal' : 'normal'
      });
    }

    return rows;
  });

  const rows = $derived(labQuery.value ?? []);
  const loading = $derived(labQuery.loading);

  function toggleUnits() {
    unitMode = unitMode === 'mg/dL' ? 'mmol/L' : 'mg/dL';
  }
</script>

<div
  class="rounded-[var(--radius-lg)] border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-4 shadow-[var(--shadow-card)]"
>
  <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
      <Icon name="labs" class="text-[var(--color-primary)]" />
      <span>Klinische Biomarker-Verlaufsmatrix (Multi-Draw)</span>
    </div>
    <div class="flex items-center gap-2">
      <Btn variant="secondary" size="sm" onclick={toggleUnits}>
        Einheit: <span class="font-mono font-bold">{unitMode}</span>
      </Btn>
      <Btn
        variant="primary"
        size="sm"
        onclick={() => alert('PDF-Arztbericht wird nach ISO/DIN generiert...')}
      >
        Arztbericht exportieren
      </Btn>
    </div>
  </div>

  {#if loading}
    <div class="py-8 text-center text-xs text-[var(--text-muted)]">
      Laborwerte werden geladen...
    </div>
  {:else if rows.length === 0}
    <div class="space-y-2 py-8 text-center text-xs text-[var(--text-muted)]">
      <Icon name="science" size="lg" class="mx-auto text-[var(--text-muted)] opacity-60" />
      <p class="text-xs font-bold text-[var(--text-main)]">Keine Laborwerte hinterlegt</p>
      <p class="mx-auto max-w-sm text-[0.6875rem]">
        Erfasse deine Blut- und Laborergebnisse manuell oder importiere deinen Arztbericht.
      </p>
    </div>
  {:else}
    <div class="w-full overflow-x-auto">
      <table class="w-full border-collapse text-left text-xs">
        <thead>
          <tr
            class="border-b border-[var(--border-subtle)] text-[0.6875rem] tracking-wider whitespace-nowrap text-[var(--text-muted)] uppercase"
          >
            <th class="px-3 py-2.5">Biomarker</th>
            <th class="px-3 py-2.5">Referenzbereich</th>
            <th class="px-3 py-2.5">Aktuellster Wert</th>
            <th class="px-3 py-2.5">Vorheriger Wert</th>
            <th class="px-3 py-2.5">Vorheriger Wert 2</th>
            <th class="px-3 py-2.5">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border-subtle)] whitespace-nowrap">
          {#each rows as row}
            <tr class="text-[var(--text-main)] transition-colors hover:bg-[var(--bg-surface-50)]">
              <td class="px-3 py-3 font-bold">{row.name}</td>
              <td class="px-3 py-3 font-mono text-[var(--text-muted)]">{row.reference}</td>
              <td class="px-3 py-3 font-mono font-bold text-[var(--color-success)]">
                {row.valCurrent.val}
                {row.valCurrent.unit}
              </td>
              <td class="px-3 py-3 font-mono">
                {row.valOld1 ? `${row.valOld1.val} ${row.valOld1.unit}` : '—'}
              </td>
              <td class="px-3 py-3 font-mono">
                {row.valOld2 ? `${row.valOld2.val} ${row.valOld2.unit}` : '—'}
              </td>
              <td class="px-3 py-3">
                <Badge variant={row.status === 'normal' ? 'success' : 'vital'}>{row.status}</Badge>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>
