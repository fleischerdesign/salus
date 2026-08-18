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

<div
  class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
>
  <div class="mb-3 flex items-center justify-between">
    <div>
      <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
        <Icon name="insights" class="text-[var(--color-circadian)]" />
        <span>Föderierte Community und Konsistenz-Rangliste</span>
      </div>
      <p class="mt-0.5 text-xs text-[var(--text-muted)]">
        Föderiert via ActivityPub • Pseudonymisiert und Opt-in
      </p>
    </div>
    <Badge
      variant="fasting"
      class="!bg-[var(--color-circadian-soft)] !text-[var(--color-circadian)]"
    >
      Rang #2 (Top 1%)
    </Badge>
  </div>

  <div class="space-y-2">
    {#each rows as r}
      <div
        class="flex items-center justify-between rounded-xl border p-3 text-xs transition-all {r.isYou
          ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)]/20 font-bold'
          : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)]'}"
      >
        <div class="flex items-center gap-3">
          <span
            class="flex h-6 w-6 items-center justify-center rounded-full font-mono font-extrabold {r.rank ===
            1
              ? 'bg-amber-400 text-black'
              : r.rank === 2
                ? 'bg-slate-300 text-black'
                : 'bg-[var(--bg-surface-100)] text-[var(--text-muted)]'}"
          >
            {r.rank}
          </span>
          <span class={r.isYou ? 'text-[var(--color-primary)]' : 'text-[var(--text-main)]'}
            >{r.user}</span
          >
        </div>
        <div class="flex items-center gap-4 font-mono">
          <span class="text-[var(--text-muted)]">{r.streak} Tage Streak</span>
          <span class="font-bold text-[var(--text-main)]">{r.points} Pkt</span>
        </div>
      </div>
    {/each}
  </div>
</div>
