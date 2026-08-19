<script lang="ts">
  import type { MuscleGroup } from '$lib/types/workouts';
  import { ANTERIOR_MUSCLES, POSTERIOR_MUSCLES, type AnatomicalMuscleDef } from './anatomy-data';

  interface Props {
    view?: 'anterior' | 'posterior';
    colorMap?: Partial<Record<MuscleGroup, string>>;
    selectedGroup?: MuscleGroup;
    onselect?: (group: MuscleGroup, detailedId: string) => void;
  }

  let { view = 'anterior', colorMap = {}, selectedGroup, onselect }: Props = $props();

  const muscles = $derived(view === 'anterior' ? ANTERIOR_MUSCLES : POSTERIOR_MUSCLES);
  const currentViewBox = $derived(view === 'anterior' ? '0 0 35 94' : '37 0 35 94');

  function getFillColor(muscle: AnatomicalMuscleDef): string {
    return colorMap[muscle.group] || 'var(--bg-surface-200)';
  }

  function isMuscleSelected(muscle: AnatomicalMuscleDef): boolean {
    return selectedGroup === muscle.group;
  }

  function handleMuscleClick(muscle: AnatomicalMuscleDef) {
    onselect?.(muscle.group, muscle.id);
  }

  function handleKeydown(e: KeyboardEvent, muscle: AnatomicalMuscleDef) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleMuscleClick(muscle);
    }
  }
</script>

<div class="relative flex h-full w-full items-center justify-center select-none">
  <svg
    viewBox={currentViewBox}
    class="h-full max-h-[280px] w-auto overflow-visible drop-shadow-md transition-all duration-300 select-none"
    role="img"
    aria-label={`${view === 'anterior' ? 'Vorderseite (Anterior)' : 'Rückseite (Posterior)'} Muskelkarte`}
  >
    <defs>
      <!-- Subtle Glow Filter for Active/Selected Muscle -->
      <filter id="vectorGlow" x="-30%" y="-30%" width="160%" height="160%">
        <feDropShadow
          dx="0"
          dy="0"
          stdDeviation="0.6"
          flood-color="var(--color-primary)"
          flood-opacity="0.9"
        />
      </filter>
    </defs>

    <!-- Base Anatomical Mannequin Paths -->
    {#each muscles as muscle (muscle.id)}
      <path
        d={muscle.path}
        fill={getFillColor(muscle)}
        stroke={isMuscleSelected(muscle) ? '#ffffff' : 'rgba(0, 0, 0, 0.18)'}
        stroke-width={isMuscleSelected(muscle) ? '0.45' : '0.1'}
        filter={isMuscleSelected(muscle) ? 'url(#vectorGlow)' : undefined}
        role="button"
        tabindex="0"
        aria-label={`${muscle.name} (${muscle.group})`}
        onclick={() => handleMuscleClick(muscle)}
        onkeydown={(e) => handleKeydown(e, muscle)}
        class="cursor-pointer transition-all duration-200 hover:opacity-80"
      />
    {/each}
  </svg>
</div>
