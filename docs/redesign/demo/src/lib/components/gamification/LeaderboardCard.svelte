<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  const rows = [
    { rank: 1, user: 'Dr_Longevity (Charité)', streak: 142, points: '9.840', isYou: false },
    { rank: 2, user: 'Philipp (Du)', streak: 94, points: '8.920', isYou: true },
    { rank: 3, user: 'Biohacker_CH', streak: 88, points: '8.450', isYou: false },
    { rank: 4, user: 'FitPhysio_Munich', streak: 76, points: '7.820', isYou: false }
  ];
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3">
    <div>
      <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="insights" class="text-[var(--color-circadian)]" />
        <span>Föderierte Community und Konsistenz-Rangliste</span>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">Föderiert via ActivityPub • Pseudonymisiert und Opt-in</p>
    </div>
    <Badge variant="fasting" class="!bg-[var(--color-circadian-soft)] !text-[var(--color-circadian)]">
      Rang #2 (Top 1%)
    </Badge>
  </div>

  <div class="space-y-2">
    {#each rows as r}
      <div
        class="flex items-center justify-between p-3 rounded-xl border text-xs transition-all {r.isYou ? 'bg-[var(--color-primary-soft)]/20 border-[var(--color-primary)] font-bold' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)]'}"
      >
        <div class="flex items-center gap-3">
          <span class="w-6 h-6 rounded-full flex items-center justify-center font-mono font-extrabold {r.rank === 1 ? 'bg-amber-400 text-black' : r.rank === 2 ? 'bg-slate-300 text-black' : 'bg-[var(--bg-surface-100)] text-[var(--text-muted)]'}">
            {r.rank}
          </span>
          <span class="{r.isYou ? 'text-[var(--color-primary)]' : 'text-[var(--text-main)]'}">{r.user}</span>
        </div>
        <div class="flex items-center gap-4 font-mono">
          <span class="text-[var(--text-muted)]">{r.streak} Tage Streak</span>
          <span class="font-bold text-[var(--text-main)]">{r.points} Pkt</span>
        </div>
      </div>
    {/each}
  </div>
</div>
