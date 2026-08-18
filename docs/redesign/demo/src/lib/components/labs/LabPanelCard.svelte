<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  const panels = [
    {
      title: 'Lipidstoffwechsel (ESC/EAS 2024)',
      date: '14.08.2026',
      status: 'Optimal',
      markers: [
        { name: 'LDL-C', value: '68 mg/dL', ref: '< 70 mg/dL', status: 'optimal' },
        { name: 'ApoB', value: '62 mg/dL', ref: '< 65 mg/dL', status: 'optimal' },
        { name: 'Triglyceride', value: '74 mg/dL', ref: '< 150 mg/dL', status: 'optimal' }
      ]
    },
    {
      title: 'Glukosestoffwechsel und Insulin',
      date: '14.08.2026',
      status: 'Optimal',
      markers: [
        { name: 'Nüchternglukose', value: '84 mg/dL', ref: '70–99 mg/dL', status: 'optimal' },
        { name: 'HbA1c', value: '5.1 %', ref: '< 5.7 %', status: 'optimal' },
        { name: 'HOMA-IR', value: '0.8', ref: '< 1.4', status: 'optimal' }
      ]
    },
    {
      title: 'Nierenfunktion und Elektrolyte',
      date: '14.08.2026',
      status: 'Normal',
      markers: [
        { name: 'eGFR (CKD-EPI)', value: '> 90 mL/min', ref: '> 90 mL/min', status: 'optimal' },
        { name: 'Kreatinin', value: '0.94 mg/dL', ref: '0.70–1.20', status: 'optimal' },
        { name: 'Harnsäure', value: '5.2 mg/dL', ref: '3.5–7.0', status: 'optimal' }
      ]
    }
  ];
</script>

<div class="space-y-4">
  {#each panels as panel}
    <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
      <div class="flex items-center justify-between mb-3">
        <div>
          <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
            <Icon name="labs" class="text-[var(--color-primary)]" />
            <span>{panel.title}</span>
          </div>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">Befund vom {panel.date} • Dr. med. Weber</p>
        </div>
        <Badge variant="success">{panel.status}</Badge>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        {#each panel.markers as m}
          <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3">
            <div class="text-xs text-[var(--text-muted)]">{m.name}</div>
            <div class="text-base font-bold font-mono text-[var(--color-success)] mt-0.5">{m.value}</div>
            <div class="text-[0.6875rem] font-mono text-[var(--text-soft)] mt-0.5">Ziel: {m.ref}</div>
          </div>
        {/each}
      </div>
    </div>
  {/each}
</div>
