<script lang="ts">
  import CircadianSunArc from '$components/today/CircadianSunArc.svelte';
  import { todayString } from '$lib/utils/datetime';

  interface Props {
    date?: string;
    config?: Record<string, unknown>;
    preview?: boolean;
    onopen?: (route: string) => void;
  }

  let { date = todayString() }: Props = $props();
</script>

<CircadianSunArc {date} />
