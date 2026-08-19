<script lang="ts">
  import SleepHypnogram from '$components/today/SleepHypnogram.svelte';
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

  const sleepQuery = useQuery(
    async () => {
      const dayStart = date + 'T00:00:00';
      const dayEnd = date + 'T23:59:59.999';

      const measurements = await db.measurement
        .where('start_time')
        .between(dayStart, dayEnd)
        .toArray();

      const valid = measurements.filter((m) => !m.deleted_at);
      const sleepDuration = valid.find((m) => m.metric_code === 'sleep_duration')?.value_numeric;
      const deep = valid.find((m) => m.metric_code === 'sleep_deep')?.value_numeric;
      const rem = valid.find((m) => m.metric_code === 'sleep_rem')?.value_numeric;
      const light = valid.find((m) => m.metric_code === 'sleep_light')?.value_numeric;
      const score = valid.find((m) => m.metric_code === 'sleep_score')?.value_numeric;
      const hrv = valid.find((m) => m.metric_code === 'hrv')?.value_numeric;

      if (!sleepDuration && !score) {
        return null;
      }

      const formatHours = (min: number | undefined) => {
        if (!min) return null;
        const h = Math.floor(min / 60);
        const m = Math.round(min % 60);
        return `${h}h ${m}m`;
      };

      return {
        duration: sleepDuration ? formatHours(sleepDuration) : null,
        score: score ? Math.round(score) : 85,
        deepSleep: deep ? formatHours(deep) : null,
        remSleep: rem ? formatHours(rem) : null,
        lightSleep: light ? formatHours(light) : null,
        hrv: hrv ? Math.round(hrv) : null
      };
    },
    () => date
  );

  const liveData = $derived(sleepQuery.value);
  const sleepData = $derived(
    liveData ??
      (preview
        ? {
            duration: '7h 45m',
            score: 88,
            deepSleep: '1h 35m',
            remSleep: '1h 50m',
            lightSleep: '4h 20m',
            hrv: 64
          }
        : null)
  );
</script>

<SleepHypnogram
  score={sleepData?.score ?? null}
  duration={sleepData?.duration ?? null}
  deepSleep={sleepData?.deepSleep ?? null}
  remSleep={sleepData?.remSleep ?? null}
  lightSleep={sleepData?.lightSleep ?? null}
  hrv={sleepData?.hrv ?? null}
/>
