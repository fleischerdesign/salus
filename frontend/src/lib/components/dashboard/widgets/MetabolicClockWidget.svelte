<script lang="ts">
  import FastingMetabolicClock from '$components/today/FastingMetabolicClock.svelte';

  interface Props {
    date?: string;
    config?: Record<string, unknown>;
    onopen?: (route: string) => void;
  }

  let { onopen }: Props = $props();
</script>

<FastingMetabolicClock onopenfood={() => onopen?.('/food')} />
