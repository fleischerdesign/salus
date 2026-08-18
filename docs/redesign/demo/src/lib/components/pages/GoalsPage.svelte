<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  interface HealthGoal {
    id: string;
    metricName: string;
    metricIcon: string;
    currentValue: string;
    targetValue: string;
    unit: string;
    direction: 'increase' | 'decrease';
    frequency: 'Täglich' | 'Wöchentlich' | 'Stichtag';
    deadline?: string;
    progressPercent: number;
    status: 'on_track' | 'off_track' | 'achieved';
    predictedValue: string;
    confInterval: string;
  }

  let goals = $state<HealthGoal[]>([
    {
      id: 'g1',
      metricName: 'Körperfettanteil (KFA)',
      metricIcon: 'chart',
      currentValue: '13.8',
      targetValue: '12.0',
      unit: '%',
      direction: 'decrease',
      frequency: 'Stichtag',
      deadline: '01. Oktober 2026',
      progressPercent: 78,
      status: 'on_track',
      predictedValue: '11.9 %',
      confInterval: '[11.5% – 12.3%]'
    },
    {
      id: 'g2',
      metricName: 'Systolischer Blutdruck',
      metricIcon: 'sun',
      currentValue: '118',
      targetValue: '120',
      unit: 'mmHg',
      direction: 'decrease',
      frequency: 'Täglich',
      progressPercent: 100,
      status: 'achieved',
      predictedValue: '117 mmHg',
      confInterval: '[114 – 121]'
    },
    {
      id: 'g3',
      metricName: 'Tägliche Schrittanzahl',
      metricIcon: 'sun',
      currentValue: '8.420',
      targetValue: '10.000',
      unit: 'Schritte',
      direction: 'increase',
      frequency: 'Täglich',
      progressPercent: 84,
      status: 'on_track',
      predictedValue: '10.450 Schritte',
      confInterval: '[9.800 – 11.100]'
    },
    {
      id: 'g4',
      metricName: 'Tägliche Proteinzufuhr',
      metricIcon: 'food',
      currentValue: '142',
      targetValue: '180',
      unit: 'g',
      direction: 'increase',
      frequency: 'Täglich',
      progressPercent: 78,
      status: 'on_track',
      predictedValue: '184 g',
      confInterval: '[172 – 195]'
    }
  ]);
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Gesundheitsziele und Prognosen</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Mathematische Zielverfolgung mit statistischen Prognosen bis zur Deadline
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Btn variant="primary" size="sm" onclick={() => alert('Neues Ziel-Formular geöffnet')}>
        + Neues Ziel anlegen
      </Btn>
    </div>
  </div>

  <!-- Goals Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    {#each goals as g}
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] flex flex-col justify-between">
        <div>
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-[var(--color-primary-soft)]/20 text-[var(--color-primary)] flex items-center justify-center">
                <Icon name={g.metricIcon} size={18} />
              </div>
              <div>
                <h2 class="text-sm font-bold text-[var(--text-main)]">{g.metricName}</h2>
                <span class="text-xs text-[var(--text-muted)]">{g.frequency} {g.deadline ? `• Frist: ${g.deadline}` : ''}</span>
              </div>
            </div>

            <Badge variant={g.status === 'achieved' ? 'success' : g.status === 'on_track' ? 'primary' : 'vital'}>
              {g.status === 'achieved' ? 'Erreicht' : g.status === 'on_track' ? 'Auf Kurs' : 'Verzögert'}
            </Badge>
          </div>

          <!-- Progress Numbers -->
          <div class="flex items-baseline gap-2 my-2 font-mono">
            <span class="text-2xl font-extrabold text-[var(--text-main)]">{g.currentValue}</span>
            <span class="text-xs text-[var(--text-muted)]">/ {g.targetValue} {g.unit}</span>
          </div>

          <!-- Progress Bar -->
          <div class="w-full bg-[var(--bg-surface-50)] h-2 rounded-full overflow-hidden my-2 border border-[var(--border-subtle)]">
            <div
              class="h-full rounded-full transition-all duration-500 {g.status === 'achieved' ? 'bg-[var(--color-success)]' : 'bg-[var(--color-primary)]'}"
              style="width: {g.progressPercent}%"
            ></div>
          </div>
        </div>

        <!-- Statistical Projection Footer -->
        <div class="mt-4 pt-3 border-t border-[var(--border-subtle)] text-xs font-mono flex items-center justify-between text-[var(--text-soft)]">
          <span>Projektion: <strong class="text-[var(--text-main)]">{g.predictedValue}</strong></span>
          <span>80% CI: {g.confInterval}</span>
        </div>
      </div>
    {/each}
  </div>
</div>
