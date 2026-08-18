<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { createMoodEntry } from '$lib/mutations/wellness';

  let valence = $state(0.7); // -1.0 (unangenehm) bis +1.0 (angenehm)
  let arousal = $state(0.5); // -1.0 (müde/passiv) bis +1.0 (energetisch)

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
    // Map valence/arousal to a 1-5 mood score and 1-5 energy level
    const moodScore = Math.min(5, Math.max(1, Math.round(((v + 1) / 2) * 4 + 1)));
    const energyLevel = Math.min(5, Math.max(1, Math.round(((a + 1) / 2) * 4 + 1)));
    await createMoodEntry({
      entry_date: todayString(),
      mood_score: moodScore,
      energy_level: energyLevel
    });
  }
</script>

<div
  class="flex flex-col justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-[18px] shadow-[var(--shadow-card)]"
>
  <div class="mb-2 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-[var(--text-main)]">
      <Icon name="insights" class="text-[var(--color-circadian)]" />
      <span>Psychobiometrie (Valenz & Energie)</span>
    </div>
    <Badge
      variant="fasting"
      class="!bg-[var(--color-circadian-soft)] !text-[var(--color-circadian)]"
    >
      {label}
    </Badge>
  </div>

  <!-- 2D Russell Circumplex Grid -->
  <div
    class="relative my-2 flex h-40 w-full items-center justify-center overflow-hidden rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)]"
  >
    <!-- Axes -->
    <div class="absolute inset-x-0 top-1/2 h-[1px] bg-[var(--border-subtle)]"></div>
    <div class="absolute inset-y-0 left-1/2 w-[1px] bg-[var(--border-subtle)]"></div>

    <!-- Quadrant Labels -->
    <span
      class="absolute top-2 right-3 font-mono text-[0.625rem] font-bold text-[var(--text-soft)] uppercase"
      >Fokus / Flow</span
    >
    <span
      class="absolute right-3 bottom-2 font-mono text-[0.625rem] font-bold text-[var(--text-soft)] uppercase"
      >Entspannung</span
    >
    <span
      class="absolute top-2 left-3 font-mono text-[0.625rem] font-bold text-[var(--text-soft)] uppercase"
      >Stress</span
    >
    <span
      class="absolute bottom-2 left-3 font-mono text-[0.625rem] font-bold text-[var(--text-soft)] uppercase"
      >Erschöpfung</span
    >

    <!-- Interactive Point -->
    <div
      class="absolute h-5 w-5 rounded-full border-2 border-white bg-[var(--color-circadian)] shadow-lg transition-all duration-200"
      style="left: calc(50% + {valence * 40}% - 10px); top: calc(50% - {arousal * 40}% - 10px);"
    ></div>
  </div>

  <div class="grid grid-cols-4 gap-1.5 pt-1 text-center">
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2 py-1.5 text-xs font-semibold text-[var(--text-main)] transition-colors hover:bg-[var(--bg-surface-100)]"
      onclick={() => setCoord(0.8, 0.7)}>Flow</button
    >
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2 py-1.5 text-xs font-semibold text-[var(--text-main)] transition-colors hover:bg-[var(--bg-surface-100)]"
      onclick={() => setCoord(0.7, -0.4)}>Ruhe</button
    >
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2 py-1.5 text-xs font-semibold text-[var(--text-main)] transition-colors hover:bg-[var(--bg-surface-100)]"
      onclick={() => setCoord(-0.5, 0.6)}>Stress</button
    >
    <button
      type="button"
      class="cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2 py-1.5 text-xs font-semibold text-[var(--text-main)] transition-colors hover:bg-[var(--bg-surface-100)]"
      onclick={() => setCoord(-0.6, -0.7)}>Müde</button
    >
  </div>
</div>
