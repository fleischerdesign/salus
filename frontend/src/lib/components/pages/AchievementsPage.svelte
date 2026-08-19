<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';

  const badges = [
    {
      id: 'a1',
      title: 'Fasten-Meister (Stufe 3)',
      desc: '30 Tage am Stück ein 16:8 Fastenfenster erfolgreich eingehalten.',
      tier: 'Gold',
      icon: 'wb-sunny',
      color: 'text-amber-400',
      unlocked: true,
      progress: '30 / 30 Tage'
    },
    {
      id: 'a2',
      title: 'Kraftpaket: 140 kg Club',
      desc: '1RM im Bankdrücken übersteigt das 1.5-fache des eigenen Körpergewichts.',
      tier: 'Platin',
      icon: 'fitness-center',
      color: 'text-cyan-400',
      unlocked: true,
      progress: '143.0 kg erreicht'
    },
    {
      id: 'a3',
      title: 'Zirkadiane Perfektion',
      desc: 'Schlafenszeit über 14 aufeinanderfolgende Tage innerhalb eines 20-Minuten-Fensters.',
      tier: 'Silber',
      icon: 'wb-sunny',
      color: 'text-slate-300',
      unlocked: true,
      progress: '14 / 14 Nächte'
    },
    {
      id: 'a4',
      title: 'Klinischer Biomarker-Champion',
      desc: 'Alle 12 Schlüssel-Laborparameter im optimalen ESC/EAS Referenzbereich.',
      tier: 'Gold',
      icon: 'science',
      color: 'text-amber-400',
      unlocked: false,
      progress: '11 / 12 Parameter (ApoB knapp)'
    }
  ];
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight text-text-main">
        Erfolge und Meilensteine
      </h1>
      <p class="mt-0.5 text-sm text-text-muted">
        Wissenschaftliche Gamification und Konsistenz-Trophäen
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="primary" class="font-mono font-bold">Level 12 • 4.850 XP</Badge>
    </div>
  </div>

  <!-- Level Progress Card -->
  <div class="rounded-2xl border border-border-subtle bg-surface-0 p-6 shadow-card">
    <div class="mb-2 flex items-center justify-between">
      <div>
        <span class="font-mono text-xs tracking-wider text-text-soft uppercase">Aktueller Rang</span
        >
        <h2 class="text-lg font-extrabold text-text-main">Biometrischer Meister (Level 12)</h2>
      </div>
      <span class="font-mono text-xs font-bold text-primary">Noch 150 XP bis Level 13</span>
    </div>
    <div
      class="my-2 h-3 w-full overflow-hidden rounded-full border border-border-subtle bg-surface-50"
    >
      <div
        class="h-full rounded-full bg-primary transition-all duration-500"
        style="width: 97%"
      ></div>
    </div>
  </div>

  <!-- Badges Grid -->
  <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
    {#each badges as b}
      <div
        class="flex items-start gap-4 rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card transition-all {b.unlocked
          ? 'hover:border-primary'
          : 'opacity-60'}"
      >
        <div
          class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-border-subtle bg-surface-50 {b.color}"
        >
          <Icon name={b.icon} size={24} />
        </div>
        <div class="min-w-0 flex-1">
          <div class="mb-1 flex items-center justify-between">
            <h3 class="truncate text-sm font-bold text-text-main">{b.title}</h3>
            <Badge variant={b.unlocked ? 'success' : 'default'} class="text-[0.625rem]"
              >{b.tier}</Badge
            >
          </div>
          <p class="mb-2 text-xs leading-relaxed text-text-muted">{b.desc}</p>
          <span
            class="font-mono text-[0.6875rem] font-bold {b.unlocked
              ? 'text-success'
              : 'text-text-soft'}"
          >
            {b.progress}
          </span>
        </div>
      </div>
    {/each}
  </div>
</div>
