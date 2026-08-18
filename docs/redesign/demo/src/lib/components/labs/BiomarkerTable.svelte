<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let unitMode = $state<'mg/dL' | 'mmol/L'>('mg/dL');

  interface BiomarkerItem {
    name: string;
    reference: string;
    valCurrent: { mg: number; mmol: number; unit: string; mmolUnit: string };
    valOld1: { mg: number; mmol: number; warning?: boolean };
    valOld2: { mg: number; mmol: number; warning?: boolean };
    trend: string;
    trendType: 'success' | 'vital' | 'default';
  }

  const rows: BiomarkerItem[] = [
    {
      name: 'LDL-Cholesterin',
      reference: '< 70 mg/dL (ESC Ziel)',
      valCurrent: { mg: 68, mmol: 1.76, unit: 'mg/dL', mmolUnit: 'mmol/L' },
      valOld1: { mg: 76, mmol: 1.96, warning: true },
      valOld2: { mg: 84, mmol: 2.17, warning: true },
      trend: '↘ -16.0 (-19%)',
      trendType: 'success'
    },
    {
      name: 'Nüchternglukose',
      reference: '70–99 mg/dL (ADA)',
      valCurrent: { mg: 84, mmol: 4.66, unit: 'mg/dL', mmolUnit: 'mmol/L' },
      valOld1: { mg: 88, mmol: 4.88 },
      valOld2: { mg: 92, mmol: 5.10 },
      trend: '↘ -8.0 (-8.7%)',
      trendType: 'success'
    },
    {
      name: 'Triglyzeride',
      reference: '< 150 mg/dL',
      valCurrent: { mg: 74, mmol: 0.84, unit: 'mg/dL', mmolUnit: 'mmol/L' },
      valOld1: { mg: 88, mmol: 0.99 },
      valOld2: { mg: 104, mmol: 1.17 },
      trend: '↘ -30.0 (-28%)',
      trendType: 'success'
    },
    {
      name: 'hs-CRP (Entzündung)',
      reference: '< 1.0 mg/L',
      valCurrent: { mg: 0.4, mmol: 0.4, unit: 'mg/L', mmolUnit: 'mg/L' },
      valOld1: { mg: 0.6, mmol: 0.6 },
      valOld2: { mg: 0.9, mmol: 0.9 },
      trend: '↘ -0.5 (-55%)',
      trendType: 'success'
    }
  ];

  function toggleUnits() {
    unitMode = unitMode === 'mg/dL' ? 'mmol/L' : 'mg/dL';
  }
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-[var(--radius-lg)] p-4 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="labs" class="text-[var(--color-primary)]" />
      <span>Klinische Biomarker-Verlaufsmatrix (Multi-Draw)</span>
    </div>
    <div class="flex items-center gap-2">
      <Btn variant="secondary" size="sm" onclick={toggleUnits}>
        Einheit: <span class="font-mono font-bold">{unitMode}</span>
      </Btn>
      <Btn variant="primary" size="sm" onclick={() => alert('PDF-Arztbericht wird nach ISO/DIN generiert...')}>
        Arztbericht exportieren
      </Btn>
    </div>
  </div>

  <div class="w-full overflow-x-auto">
    <table class="w-full text-left text-xs border-collapse">
      <thead>
        <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.6875rem] whitespace-nowrap">
          <th class="py-2.5 px-3">Biomarker</th>
          <th class="py-2.5 px-3">Referenzbereich</th>
          <th class="py-2.5 px-3">14.08.2026 (Aktuell)</th>
          <th class="py-2.5 px-3">12.02.2026 (-6M)</th>
          <th class="py-2.5 px-3">10.08.2025 (-1J)</th>
          <th class="py-2.5 px-3">1-Jahres Trend</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-[var(--border-subtle)] whitespace-nowrap">
        {#each rows as row}
          <tr class="text-[var(--text-main)] hover:bg-[var(--bg-surface-50)] transition-colors">
            <td class="py-3 px-3 font-bold">{row.name}</td>
            <td class="py-3 px-3 text-[var(--text-muted)] font-mono">{row.reference}</td>
            <td class="py-3 px-3 font-mono font-bold text-[var(--color-success)]">
              {unitMode === 'mg/dL' ? `${row.valCurrent.mg} ${row.valCurrent.unit}` : `${row.valCurrent.mmol} ${row.valCurrent.mmolUnit}`}
            </td>
            <td class="py-3 px-3 font-mono">
              {unitMode === 'mg/dL' ? `${row.valOld1.mg} ${row.valCurrent.unit}` : `${row.valOld1.mmol} ${row.valCurrent.mmolUnit}`}
              {#if row.valOld1.warning}
                <span class="text-[var(--color-vital)] font-bold ml-0.5">!</span>
              {/if}
            </td>
            <td class="py-3 px-3 font-mono">
              {unitMode === 'mg/dL' ? `${row.valOld2.mg} ${row.valCurrent.unit}` : `${row.valOld2.mmol} ${row.valCurrent.mmolUnit}`}
              {#if row.valOld2.warning}
                <span class="text-[var(--color-vital)] font-bold ml-0.5">!</span>
              {/if}
            </td>
            <td class="py-3 px-3">
              <Badge variant={row.trendType}>{row.trend}</Badge>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
