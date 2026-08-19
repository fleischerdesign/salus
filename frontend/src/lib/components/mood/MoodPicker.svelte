<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import { theme } from '$stores/theme.svelte';
  import { moodGradient } from '$lib/theme/scales';

  interface Props {
    score: number;
    onSelect: (score: number) => void;
  }

  let { score, onSelect }: Props = $props();

  const moodIcons = [
    'mood-bad',
    'sentiment-dissatisfied',
    'sentiment-dissatisfied',
    'sentiment-neutral',
    'sentiment-neutral',
    'sentiment-satisfied',
    'sentiment-satisfied',
    'sentiment-very-satisfied',
    'sentiment-very-satisfied',
    'celebration'
  ];
  const labels = [
    'Terrible',
    'Awful',
    'Bad',
    'Meh',
    'Okay',
    'Alright',
    'Good',
    'Great',
    'Amazing',
    'Fantastic'
  ];
</script>

<div class="space-y-4">
  <div class="grid grid-cols-10 gap-1.5">
    {#each moodIcons as icon, i}
      {@const idx = i + 1}
      {@const selected = score === idx}
      <button
        type="button"
        class="duration-micro flex flex-col items-center gap-1 rounded-xl p-2 transition-all hover:scale-110"
        class:scale-110={selected}
        class:bg-surface-100={selected}
        class:ring-2={selected}
        class:ring-primary-400={selected}
        onclick={() => onSelect(idx)}
      >
        <Icon name={icon} size="xl" />
        <span class="text-[10px] leading-tight text-surface-500">{labels[i]}</span>
      </button>
    {/each}
  </div>
  {#if score > 0}
    <div class="flex items-center gap-3 rounded-lg bg-surface-50 px-4 py-2.5">
      <Icon name={moodIcons[score - 1]} size="lg" />
      <div class="flex-1">
        <div class="text-sm font-semibold text-surface-800">{labels[score - 1]}</div>
        <div class="h-1.5 w-full overflow-hidden rounded-full bg-surface-200">
          <div
            class="h-full rounded-full bg-gradient-to-r {moodGradient(score, theme.colorblind)}"
            style="width: {score * 10}%"
          ></div>
        </div>
      </div>
      <span class="text-sm font-bold text-surface-600">{score}/10</span>
    </div>
  {/if}
</div>

<!-- scanner hints: icon="mood-bad" icon="sentiment-dissatisfied" icon="sentiment-neutral" icon="sentiment-very-satisfied" -->
