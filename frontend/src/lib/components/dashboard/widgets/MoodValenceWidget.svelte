<script lang="ts">
  import MoodValenceSphere from '$components/today/MoodValenceSphere.svelte';
  import { todayString } from '$lib/utils/datetime';

  interface Props {
    date?: string;
    config?: Record<string, unknown>;
    preview?: boolean;
    onopen?: (route: string) => void;
  }

  let { date = todayString() }: Props = $props();
</script>

<MoodValenceSphere {date} />
