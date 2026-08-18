<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  const weeks = 52;
  const daysPerWeek = 7;

  // Generate deterministic activity levels (0, 1, 2, 3)
  const matrix = Array.from({ length: weeks }, (_, w) =>
    Array.from({ length: daysPerWeek }, (_, d) => {
      const v = (w * 7 + d) % 5;
      return v === 0 ? 0 : v === 1 ? 1 : v === 2 ? 2 : 3;
    })
  );

  const levelClasses = [
    'bg-[var(--bg-surface-100)]',
    'bg-[rgba(16,185,129,0.3)]',
    'bg-[rgba(16,185,129,0.6)]',
    'bg-[var(--color-success)]'
  ];
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-[16px_20px] shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3">
    <div class="text-[0.8125rem] font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="check" class="text-[var(--color-success)]" />
      <span>Jahres-Konsistenz & Habit-Matrix (52 Wochen)</span>
    </div>
    <Badge variant="success">384 Check-ins</Badge>
  </div>

  <!-- Heatmap Matrix Grid -->
  <div class="flex gap-1 overflow-x-auto pb-2">
    {#each matrix as week}
      <div class="flex flex-col gap-1 shrink-0">
        {#each week as level}
          <div
            class="w-2.5 h-2.5 rounded-[2px] cursor-pointer hover:scale-130 transition-transform {levelClasses[level]}"
            title="Aktivitäts-Level: {level}"
          ></div>
        {/each}
      </div>
    {/each}
  </div>

  <div class="flex justify-between items-center text-[0.75rem] text-[var(--text-muted)] mt-2">
    <span>Konsistenz: <strong class="text-[var(--text-main)]">91.4%</strong> lückenlos protokolliert</span>
    <div class="flex items-center gap-1 text-[0.6875rem]">
      <span>Weniger</span>
      <div class="w-2 h-2 rounded-[2px] bg-[var(--bg-surface-100)]"></div>
      <div class="w-2 h-2 rounded-[2px] bg-[rgba(16,185,129,0.3)]"></div>
      <div class="w-2 h-2 rounded-[2px] bg-[rgba(16,185,129,0.6)]"></div>
      <div class="w-2 h-2 rounded-[2px] bg-[var(--color-success)]"></div>
      <span>Mehr</span>
    </div>
  </div>
</div>
