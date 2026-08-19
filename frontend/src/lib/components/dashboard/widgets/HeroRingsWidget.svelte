<script lang="ts">
  import HeroProgressRings from '$components/today/HeroProgressRings.svelte';
  import { todayString } from '$lib/utils/datetime';

  interface Props {
    date?: string;
    config?: Record<string, unknown>;
    preview?: boolean;
    onopen?: (route: string) => void;
  }

  let { date = todayString(), preview = false }: Props = $props();

  const previewActivity = $derived(
    preview ? { current: 8420, target: 10000, percent: 84, label: 'Schritte' } : undefined
  );
  const previewHydration = $derived(
    preview ? { current: 2000, target: 2500, percent: 80, label: 'Wasser' } : undefined
  );
  const previewHabits = $derived(
    preview ? { current: 3, target: 4, percent: 75, label: 'Gewohnheiten' } : undefined
  );
</script>

<HeroProgressRings
  {date}
  activity={previewActivity}
  hydration={previewHydration}
  habits={previewHabits}
/>
