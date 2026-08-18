<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  const achievements = [
    {
      title: 'Klinische Konsistenz (30 Tage)',
      tier: 'Gold',
      desc: '30 Tage lückenlose Erfassung aller Vitalwerte ohne Unterbrechung.',
      progress: 30,
      max: 30,
      unlocked: true,
      color: 'var(--color-circadian)'
    },
    {
      title: 'ESC Lipid-Champion',
      tier: 'Platin',
      desc: 'LDL-Cholesterin erfolgreich unter 70 mg/dL gesenkt.',
      progress: 68,
      max: 70,
      unlocked: true,
      color: 'var(--color-primary)'
    },
    {
      title: 'Hydrations-Meister (100 Tage)',
      tier: 'Silber',
      desc: '100 Tage über 2.500 ml Wasser getrunken.',
      progress: 64,
      max: 100,
      unlocked: false,
      color: 'var(--color-hydrate)'
    },
    {
      title: 'Metabolische Autophagie',
      tier: 'Gold',
      desc: '50 Fasten-Sessions über 16 Stunden protokolliert.',
      progress: 38,
      max: 50,
      unlocked: false,
      color: 'var(--color-fasting)'
    }
  ];
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-4">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="sun" class="text-[var(--color-circadian)]" />
      <span>Akademische Meilensteine und Erfolge</span>
    </div>
    <Badge variant="fasting" class="!bg-[var(--color-circadian-soft)] !text-[var(--color-circadian)]">
      Tier-Level: Platin Master
    </Badge>
  </div>

  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
    {#each achievements as ach}
      <div
        class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3.5 flex flex-col justify-between {ach.unlocked ? 'border-[var(--color-circadian)]/30' : 'opacity-80'}"
      >
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-bold text-[var(--text-main)]">{ach.title}</span>
            <Badge variant={ach.unlocked ? 'success' : 'default'}>{ach.tier}</Badge>
          </div>
          <p class="text-[0.6875rem] text-[var(--text-muted)] mb-3">{ach.desc}</p>
        </div>

        <div>
          <div class="flex justify-between text-[0.6875rem] font-mono text-[var(--text-soft)] mb-1">
            <span>Fortschritt</span>
            <span>{ach.progress} / {ach.max}</span>
          </div>
          <div class="h-1.5 rounded-full bg-[var(--bg-surface-100)] overflow-hidden">
            <div
              class="h-full transition-all duration-500"
              style="width: {Math.min(100, (ach.progress / ach.max) * 100)}%; background-color: {ach.color};"
            ></div>
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>
