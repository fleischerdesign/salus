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
    'bg-surface-100',
    'bg-[rgba(16,185,129,0.3)]',
    'bg-[rgba(16,185,129,0.6)]',
    'bg-success'
  ];
</script>

<div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-card">
  <div class="mb-3 flex items-start justify-between gap-3">
    <div class="flex min-w-0 items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
        style="background-color: color-mix(in srgb, var(--color-success) 12%, transparent); color: var(--color-success);"
      >
        <Icon name="calendar-month" size="md" />
      </div>
      <div class="min-w-0">
        <h3 class="truncate text-sm font-extrabold tracking-tight text-text-main">
          Jahres-Konsistenz &amp; Habit-Matrix
        </h3>
        <p class="truncate text-xs text-text-muted">52-Wochen Aktivitäts-Heatmap</p>
      </div>
    </div>
    <Badge variant="success" class="text-[0.625rem] font-bold">384 Check-ins</Badge>
  </div>

  <!-- Heatmap Matrix Grid -->
  <div class="flex gap-1 overflow-x-auto pb-2">
    {#each matrix as week}
      <div class="flex shrink-0 flex-col gap-1">
        {#each week as level}
          <div
            class="h-2.5 w-2.5 cursor-pointer rounded-[2px] transition-transform hover:scale-130 {levelClasses[
              level
            ]}"
            title="Aktivitäts-Level: {level}"
          ></div>
        {/each}
      </div>
    {/each}
  </div>

  <div class="mt-2 flex items-center justify-between text-[0.75rem] text-text-muted">
    <span>Konsistenz: <strong class="text-text-main">91.4%</strong> lückenlos protokolliert</span>
    <div class="flex items-center gap-1 text-[0.6875rem]">
      <span>Weniger</span>
      <div class="h-2 w-2 rounded-[2px] bg-surface-100"></div>
      <div class="h-2 w-2 rounded-[2px] bg-[rgba(16,185,129,0.3)]"></div>
      <div class="h-2 w-2 rounded-[2px] bg-[rgba(16,185,129,0.6)]"></div>
      <div class="h-2 w-2 rounded-[2px] bg-success"></div>
      <span>Mehr</span>
    </div>
  </div>
</div>
