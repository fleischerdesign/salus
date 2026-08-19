<script lang="ts">
  import HydrationWaveGlass from '$components/today/HydrationWaveGlass.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';

  interface Props {
    date?: string;
    config?: Record<string, unknown>;
    preview?: boolean;
    onopen?: (route: string) => void;
  }

  let { date = todayString(), preview = false }: Props = $props();

  const waterQuery = useQuery(
    async () => {
      const dayStart = date + 'T00:00:00';
      const dayEnd = date + 'T23:59:59.999';

      const measurements = await db.measurement
        .where('start_time')
        .between(dayStart, dayEnd)
        .toArray();

      const valid = measurements.filter((m) => !m.deleted_at);
      const totalWater = valid
        .filter((m) => m.metric_code === 'hydration' || m.metric_code === 'water')
        .reduce((sum, m) => sum + (m.value_numeric || 0), 0);

      return totalWater;
    },
    () => date
  );

  const liveWater = $derived(waterQuery.value ?? 0);
  const waterAmount = $derived(liveWater > 0 ? liveWater : preview ? 1750 : 0);
</script>

<HydrationWaveGlass currentMl={waterAmount} />
