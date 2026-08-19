<script lang="ts">
  import HabitYearMatrix from '$components/today/HabitYearMatrix.svelte';

  interface Props {
    date?: string;
    config?: Record<string, unknown>;
    onopen?: (route: string) => void;
  }

  let { date: _date, config: _config, onopen: _onopen }: Props = $props();
</script>

<HabitYearMatrix />
