<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  const days = [
    { day: 'Mo', title: 'Push Day A', focus: 'Brust, Schultern, Trizeps', completed: true, active: false },
    { day: 'Di', title: 'Pull Day A', focus: 'Rücken, Bizeps, Hintere Schulter', completed: false, active: true },
    { day: 'Mi', title: 'Rest & Zone 2', focus: '45 Min Spaziergang + Mobility', completed: false, active: false },
    { day: 'Do', title: 'Legs & Core', focus: 'Quadrizeps, Hamstrings, Waden', completed: false, active: false },
    { day: 'Fr', title: 'Upper Hypertrophy', focus: 'Ganzkörper Oberkörper', completed: false, active: false },
    { day: 'Sa', title: 'Active Recovery', focus: 'Sauna + Dehnen', completed: false, active: false },
    { day: 'So', title: 'Rest Day', focus: 'Vollständige Regeneration', completed: false, active: false }
  ];
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="dumbbell" class="text-[var(--color-primary)]" />
      <span>Wöchentlicher Trainings-Split (4er PPL-Upper)</span>
    </div>
    <Badge variant="activity">4 Einheiten / Woche</Badge>
  </div>

  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
    {#each days as d}
      <div
        class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-3 flex flex-col justify-between {d.active ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)]/20 shadow-xs' : ''} {d.completed ? 'opacity-70' : ''}"
      >
        <div>
          <div class="flex items-center justify-between mb-1">
            <span class="font-mono font-bold text-xs px-1.5 py-0.5 rounded bg-[var(--bg-surface-0)] text-[var(--text-main)]">
              {d.day}
            </span>
            {#if d.completed}
              <Badge variant="success">Erledigt</Badge>
            {:else if d.active}
              <Badge variant="primary">Heute</Badge>
            {/if}
          </div>
          <div class="text-xs font-bold text-[var(--text-main)] mt-1">{d.title}</div>
          <p class="text-[0.6875rem] text-[var(--text-muted)] mt-0.5">{d.focus}</p>
        </div>
      </div>
    {/each}
  </div>
</div>
