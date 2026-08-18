<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

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

  function setCoord(v: number, a: number) {
    valence = v;
    arousal = a;
  }
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-[18px] shadow-[var(--shadow-card)] flex flex-col justify-between">
  <div class="flex items-center justify-between mb-2">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="insights" class="text-[var(--color-circadian)]" />
      <span>Psychobiometrie (Valenz & Energie)</span>
    </div>
    <Badge variant="fasting" class="!bg-[var(--color-circadian-soft)] !text-[var(--color-circadian)]">
      {label}
    </Badge>
  </div>

  <!-- 2D Russell Circumplex Grid -->
  <div class="relative w-full h-40 bg-[var(--bg-surface-50)] rounded-xl border border-[var(--border-subtle)] my-2 flex items-center justify-center overflow-hidden">
    <!-- Axes -->
    <line x1="0" y1="50%" x2="100%" y2="50%" stroke="var(--border-subtle)" stroke-width="1.5" />
    <line x1="50%" y1="0" x2="50%" y2="100%" stroke="var(--border-subtle)" stroke-width="1.5" />

    <!-- Quadrant Labels -->
    <span class="absolute top-2 right-3 text-[0.625rem] text-[var(--text-soft)] uppercase font-mono font-bold">Fokus / Flow</span>
    <span class="absolute bottom-2 right-3 text-[0.625rem] text-[var(--text-soft)] uppercase font-mono font-bold">Entspannung</span>
    <span class="absolute top-2 left-3 text-[0.625rem] text-[var(--text-soft)] uppercase font-mono font-bold">Stress</span>
    <span class="absolute bottom-2 left-3 text-[0.625rem] text-[var(--text-soft)] uppercase font-mono font-bold">Erschöpfung</span>

    <!-- Interactive Point -->
    <div
      class="absolute w-5 h-5 rounded-full bg-[var(--color-circadian)] border-2 border-white shadow-lg transition-all duration-200"
      style="left: calc(50% + {valence * 40}% - 10px); top: calc(50% - {arousal * 40}% - 10px);"
    ></div>
  </div>

  <div class="grid grid-cols-4 gap-1.5 pt-1 text-center">
    <button type="button" class="btn btn-secondary text-xs py-1.5" onclick={() => setCoord(0.8, 0.7)}>Flow</button>
    <button type="button" class="btn btn-secondary text-xs py-1.5" onclick={() => setCoord(0.7, -0.4)}>Ruhe</button>
    <button type="button" class="btn btn-secondary text-xs py-1.5" onclick={() => setCoord(-0.5, 0.6)}>Stress</button>
    <button type="button" class="btn btn-secondary text-xs py-1.5" onclick={() => setCoord(-0.6, -0.7)}>Müde</button>
  </div>
</div>
