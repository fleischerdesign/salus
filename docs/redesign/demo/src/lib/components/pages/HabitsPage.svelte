<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import AchievementCard from '../gamification/AchievementCard.svelte';

  const habits = [
    {
      id: '1',
      title: '3.000 ml Wasser trinken',
      category: 'Metabolismus',
      streak: 42,
      bestStreak: 65,
      frequency: 'Täglich',
      consistencyPct: 94.2,
      doneToday: true
    },
    {
      id: '2',
      title: '10.000 Schritte gehen',
      category: 'Aktivität',
      streak: 18,
      bestStreak: 45,
      frequency: 'Täglich',
      consistencyPct: 88.0,
      doneToday: true
    },
    {
      id: '3',
      title: '10 Min Morgenlicht vor 09:00 Uhr',
      category: 'Zirkadian',
      streak: 12,
      bestStreak: 30,
      frequency: 'Täglich',
      consistencyPct: 82.5,
      doneToday: true
    },
    {
      id: '4',
      title: 'Kein Koffein nach 14:30 Uhr',
      category: 'Schlafhygiene',
      streak: 6,
      bestStreak: 21,
      frequency: 'Täglich',
      consistencyPct: 76.0,
      doneToday: false
    }
  ];
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Gewohnheiten & Habit-Management</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Wissenschaftliche Verhaltensarchitektur nach der 66-Tage-Automatisierungsregel
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Durchschnittliche Konsistenz: 85.2%</Badge>
      <Btn variant="primary" size="sm" onclick={() => alert('Neuen Habit anlegen geöffnet')}>
        + Gewohnheit anlegen
      </Btn>
    </div>
  </div>

  <!-- Habit Grid -->
  <div class="space-y-4">
    {#each habits as h}
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
        <div class="flex items-center justify-between flex-wrap gap-3 mb-3">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-base font-bold text-[var(--text-main)]">{h.title}</span>
              <Badge variant="default" class="text-[0.625rem]">{h.category}</Badge>
            </div>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">Frequenz: {h.frequency} • Bester Streak: {h.bestStreak} Tage</p>
          </div>

          <div class="flex items-center gap-4 font-mono">
            <div>
              <span class="text-xs text-[var(--text-muted)] block text-right font-sans">Aktueller Streak</span>
              <span class="text-base font-bold text-[var(--color-circadian)] block text-right">{h.streak} Tage </span>
            </div>
            <Badge variant={h.doneToday ? 'success' : 'default'} class="text-xs px-3 py-1">
              {h.doneToday ? 'Heute erledigt' : 'Ausstehend'}
            </Badge>
          </div>
        </div>

        <!-- Individual Mini-Heatmap (12 Weeks) -->
        <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3">
          <div class="flex justify-between items-center text-[0.6875rem] text-[var(--text-muted)] mb-2 font-mono">
            <span>Letzte 12 Wochen (84 Tage)</span>
            <span class="text-[var(--color-success)] font-bold">{h.consistencyPct}% Erfüllungsrate</span>
          </div>
          <div class="flex gap-1 overflow-x-auto pb-1">
            {#each Array.from({ length: 12 }) as _, w}
              <div class="flex flex-col gap-1 shrink-0">
                {#each Array.from({ length: 7 }) as _, d}
                  <div
                    class="w-2.5 h-2.5 rounded-[2px] {(w * 7 + d) % 6 === 0 ? 'bg-[var(--bg-surface-100)]' : 'bg-[var(--color-success)]'}"
                  ></div>
                {/each}
              </div>
            {/each}
          </div>
        </div>
      </div>
    {/each}
  </div>

  <!-- Achievements Gallery -->
  <AchievementCard />
</div>
