<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { createMoodEntry } from '$lib/mutations/wellness';

  interface Props {
    date?: string;
  }

  let { date = todayString() }: Props = $props();

  let valence = $state(0.7); // -1.0 (unangenehm) bis +1.0 (angenehm)
  let arousal = $state(0.5); // -1.0 (müde/passiv) bis +1.0 (energetisch)

  const moodQuery = useQuery(
    async () => {
      const entry = await db.mood_entry.where('entry_date').equals(date).first();
      return entry ?? null;
    },
    () => date
  );

  $effect(() => {
    const entry = moodQuery.value;
    if (entry) {
      // Map 1-5 score back to coordinates
      valence = ((entry.mood_score - 1) / 4) * 2 - 1;
      arousal = (((entry.energy_level ?? 3) - 1) / 4) * 2 - 1;
    }
  });

  let label = $derived(
    valence > 0.3 && arousal > 0.3
      ? 'Fokussiert & Vital'
      : valence > 0.3 && arousal <= 0.3
        ? 'Entspannt & Gelassen'
        : valence <= 0.3 && arousal > 0.3
          ? 'Gestresst / Angespannt'
          : 'Erschöpft & Kraftlos'
  );

  async function setCoord(v: number, a: number) {
    valence = v;
    arousal = a;
    const moodScore = Math.min(5, Math.max(1, Math.round(((v + 1) / 2) * 4 + 1)));
    const energyLevel = Math.min(5, Math.max(1, Math.round(((a + 1) / 2) * 4 + 1)));
    await createMoodEntry({
      entry_date: date,
      mood_score: moodScore,
      energy_level: energyLevel
    });
  }
</script>

<div
  class="flex flex-col justify-between rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-card"
>
  <div class="mb-2 flex items-start justify-between gap-3">
    <div class="flex min-w-0 items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
        style="background-color: color-mix(in srgb, var(--color-circadian) 12%, transparent); color: var(--color-circadian);"
      >
        <Icon name="insights" size="md" />
      </div>
      <div class="min-w-0">
        <h3 class="truncate text-sm font-extrabold tracking-tight text-text-main">
          Psychobiometrie (Stimmung)
        </h3>
        <p class="truncate text-xs text-text-muted">Valenz &amp; Erregung</p>
      </div>
    </div>
    <Badge variant="fasting" class="!bg-circadian-soft text-[0.625rem] font-bold !text-circadian">
      {label}
    </Badge>
  </div>

  <!-- 2D Russell Circumplex Grid -->
  <div
    class="relative my-2 flex h-40 w-full items-center justify-center overflow-hidden rounded-2xl border border-border-subtle bg-surface-50"
  >
    <!-- Axes -->
    <div class="absolute inset-x-0 top-1/2 h-[1px] bg-border-subtle"></div>
    <div class="absolute inset-y-0 left-1/2 w-[1px] bg-border-subtle"></div>

    <!-- Quadrant Labels -->
    <span
      class="absolute top-2 right-3 font-mono text-[0.625rem] font-bold text-text-muted uppercase"
      >Fokus / Flow</span
    >
    <span
      class="absolute right-3 bottom-2 font-mono text-[0.625rem] font-bold text-text-muted uppercase"
      >Entspannung</span
    >
    <span
      class="absolute top-2 left-3 font-mono text-[0.625rem] font-bold text-text-muted uppercase"
      >Stress</span
    >
    <span
      class="absolute bottom-2 left-3 font-mono text-[0.625rem] font-bold text-text-muted uppercase"
      >Erschöpfung</span
    >

    <!-- Interactive Point -->
    <div
      class="absolute h-5 w-5 rounded-full border-2 border-white bg-circadian shadow-lg transition-all duration-200"
      style="left: calc(50% + {valence * 40}% - 10px); top: calc(50% - {arousal * 40}% - 10px);"
    ></div>
  </div>

  <div class="grid grid-cols-4 gap-2 pt-1 text-center">
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-2 py-1.5 text-xs font-bold text-text-main transition-colors hover:bg-surface-100"
      onclick={() => setCoord(0.8, 0.7)}>Flow</button
    >
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-2 py-1.5 text-xs font-bold text-text-main transition-colors hover:bg-surface-100"
      onclick={() => setCoord(0.7, -0.4)}>Ruhe</button
    >
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-2 py-1.5 text-xs font-bold text-text-main transition-colors hover:bg-surface-100"
      onclick={() => setCoord(-0.5, 0.6)}>Stress</button
    >
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-2 py-1.5 text-xs font-bold text-text-main transition-colors hover:bg-surface-100"
      onclick={() => setCoord(-0.6, -0.7)}>Müde</button
    >
  </div>
</div>
