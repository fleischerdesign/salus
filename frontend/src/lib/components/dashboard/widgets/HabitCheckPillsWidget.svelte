<script lang="ts">
  import HabitCheckPills from '$components/today/HabitCheckPills.svelte';
  import { todayString } from '$lib/utils/datetime';

  interface Props {
    date?: string;
    config?: Record<string, unknown>;
    preview?: boolean;
    onopen?: (route: string) => void;
  }

  let { date = todayString() }: Props = $props();
</script>

<HabitCheckPills {date} />
