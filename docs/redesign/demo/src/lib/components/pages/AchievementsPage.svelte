<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  const badges = [
    {
      id: 'a1',
      title: 'Fasten-Meister (Stufe 3)',
      desc: '30 Tage am Stück ein 16:8 Fastenfenster erfolgreich eingehalten.',
      tier: 'Gold',
      icon: 'sun',
      color: 'text-amber-400',
      unlocked: true,
      progress: '30 / 30 Tage'
    },
    {
      id: 'a2',
      title: 'Kraftpaket: 140 kg Club',
      desc: '1RM im Bankdrücken übersteigt das 1.5-fache des eigenen Körpergewichts.',
      tier: 'Platin',
      icon: 'dumbbell',
      color: 'text-cyan-400',
      unlocked: true,
      progress: '143.0 kg erreicht'
    },
    {
      id: 'a3',
      title: 'Zirkadiane Perfektion',
      desc: 'Schlafenszeit über 14 aufeinanderfolgende Tage innerhalb eines 20-Minuten-Fensters.',
      tier: 'Silber',
      icon: 'sun',
      color: 'text-slate-300',
      unlocked: true,
      progress: '14 / 14 Nächte'
    },
    {
      id: 'a4',
      title: 'Klinischer Biomarker-Champion',
      desc: 'Alle 12 Schlüssel-Laborparameter im optimalen ESC/EAS Referenzbereich.',
      tier: 'Gold',
      icon: 'labs',
      color: 'text-amber-400',
      unlocked: false,
      progress: '11 / 12 Parameter (ApoB knapp)'
    }
  ];
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Erfolge und Meilensteine</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Wissenschaftliche Gamification und Konsistenz-Trophäen
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="primary" class="font-mono font-bold">Level 12 • 4.850 XP</Badge>
    </div>
  </div>

  <!-- Level Progress Card -->
  <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-6 shadow-[var(--shadow-card)]">
    <div class="flex items-center justify-between mb-2">
      <div>
        <span class="text-xs font-mono text-[var(--text-soft)] uppercase tracking-wider">Aktueller Rang</span>
        <h2 class="text-lg font-extrabold text-[var(--text-main)]">Biometrischer Meister (Level 12)</h2>
      </div>
      <span class="text-xs font-mono font-bold text-[var(--color-primary)]">Noch 150 XP bis Level 13</span>
    </div>
    <div class="w-full bg-[var(--bg-surface-50)] h-3 rounded-full overflow-hidden border border-[var(--border-subtle)] my-2">
      <div class="h-full bg-[var(--color-primary)] rounded-full transition-all duration-500" style="width: 97%"></div>
    </div>
  </div>

  <!-- Badges Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    {#each badges as b}
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)] flex items-start gap-4 transition-all {b.unlocked ? 'hover:border-[var(--color-primary)]' : 'opacity-60'}">
        <div class="w-12 h-12 rounded-2xl bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] flex items-center justify-center shrink-0 {b.color}">
          <Icon name={b.icon} size={24} />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-1">
            <h3 class="text-sm font-bold text-[var(--text-main)] truncate">{b.title}</h3>
            <Badge variant={b.unlocked ? 'success' : 'default'} class="text-[0.625rem]">{b.tier}</Badge>
          </div>
          <p class="text-xs text-[var(--text-muted)] leading-relaxed mb-2">{b.desc}</p>
          <span class="text-[0.6875rem] font-mono font-bold {b.unlocked ? 'text-[var(--color-success)]' : 'text-[var(--text-soft)]'}">
            {b.unlocked ? '' : ''}{b.progress}
          </span>
        </div>
      </div>
    {/each}
  </div>
</div>
