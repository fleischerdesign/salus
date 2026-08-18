<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let {
    open = false,
    initialWeight = 100,
    onapplyweight,
    onclose
  } = $props<{
    open: boolean;
    initialWeight?: number;
    onapplyweight: (weightKg: number) => void;
    onclose: () => void;
  }>();

  let targetWeight = $state(100);
  let barWeight = $state(20); // 20kg standard, 15kg, 10kg

  $effect(() => {
    if (open) {
      targetWeight = initialWeight || 100;
    }
  });

  interface PlateSpec {
    weight: number;
    color: string;
    textColor: string;
    height: number;
    width: number;
  }

  const AVAILABLE_PLATES: PlateSpec[] = [
    { weight: 25, color: '#ef4444', textColor: '#ffffff', height: 90, width: 14 },
    { weight: 20, color: '#3b82f6', textColor: '#ffffff', height: 86, width: 13 },
    { weight: 15, color: '#eab308', textColor: '#000000', height: 76, width: 11 },
    { weight: 10, color: '#10b981', textColor: '#ffffff', height: 64, width: 10 },
    { weight: 5, color: '#f8fafc', textColor: '#0f172a', height: 50, width: 8 },
    { weight: 2.5, color: '#475569', textColor: '#ffffff', height: 40, width: 7 },
    { weight: 1.25, color: '#94a3b8', textColor: '#0f172a', height: 32, width: 6 }
  ];

  let calculation = $derived.by(() => {
    const weightToLoad = Math.max(0, targetWeight - barWeight);
    const weightPerSide = weightToLoad / 2;
    let remaining = weightPerSide;
    const platesPerSide: { plate: PlateSpec; count: number }[] = [];

    for (const plate of AVAILABLE_PLATES) {
      if (remaining >= plate.weight) {
        const count = Math.floor(remaining / plate.weight);
        platesPerSide.push({ plate, count });
        remaining = Math.round((remaining - count * plate.weight) * 100) / 100;
      }
    }

    const actualLoadedSide = platesPerSide.reduce((acc, p) => acc + p.plate.weight * p.count, 0);
    const totalActualWeight = barWeight + actualLoadedSide * 2;

    return {
      weightPerSide,
      platesPerSide,
      totalActualWeight,
      isExact: Math.abs(totalActualWeight - targetWeight) < 0.01,
      remainder: remaining
    };
  });

  const quickWeights = [60, 80, 100, 120, 140, 160, 180, 200];
</script>

{#if open}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-60 flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-6 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-[var(--color-activity)]/10 text-[var(--color-activity)] flex items-center justify-center font-bold text-lg shrink-0">
            
          </div>
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Hantelscheiben-Rechner</h2>
            <p class="text-xs text-[var(--text-muted)]">Exakte Scheibenbestückung pro Seite nach IWF/IPF-Standard</p>
          </div>
        </div>

        <button
          type="button"
          onclick={onclose}
          class="w-8 h-8 rounded-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center text-lg cursor-pointer transition-colors"
          title="Schließen"
          aria-label="Schließen"
        >
          &times;
        </button>
      </div>

      <!-- Target Weight & Bar Settings -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <!-- Target Weight Input -->
        <div class="space-y-1">
          <label for="plate-target-weight" class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">
            Ziel-Gesamtgewicht
          </label>
          <div class="relative">
            <input
              id="plate-target-weight"
              type="number"
              step="0.5"
              bind:value={targetWeight}
              class="w-full px-3.5 py-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-base font-bold text-[var(--text-main)] outline-none focus:border-[var(--color-activity)] tabular-nums"
            />
            <span class="absolute right-3 top-2.5 text-xs text-[var(--text-muted)] font-bold">kg</span>
          </div>
        </div>

        <!-- Barbell Selection -->
        <div class="space-y-1">
          <label for="plate-barbell-select" class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase">
            Hantelstange
          </label>
          <select
            id="plate-barbell-select"
            bind:value={barWeight}
            class="w-full px-3.5 py-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--text-main)] outline-none focus:border-[var(--color-activity)] cursor-pointer"
          >
            <option value={20}>Olympia-Stange (20.0 kg)</option>
            <option value={15}>Frauen-Stange (15.0 kg)</option>
            <option value={10}>SZ / Kurz-Stange (10.0 kg)</option>
          </select>
        </div>
      </div>

      <!-- Quick Weight Pills -->
      <div class="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar">
        {#each quickWeights as qw}
          <button
            type="button"
            onclick={() => targetWeight = qw}
            class="px-2.5 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer tabular-nums {targetWeight === qw ? 'bg-[var(--color-activity)] text-white shadow-xs' : 'bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
          >
            {qw} kg
          </button>
        {/each}
      </div>

      <!-- VISUAL BARBELL SLEEVE GRAPHIC -->
      <div class="bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-5 flex flex-col items-center justify-center space-y-4">
        
        <div class="w-full text-center">
          <span class="text-xs text-[var(--text-muted)] block">Beladung pro Seite:</span>
          <span class="text-2xl font-extrabold text-[var(--color-activity)] tabular-nums">
            {calculation.weightPerSide.toFixed(2)} kg
          </span>
        </div>

        <!-- SVG Barbell Sleeve with loaded plates -->
        <div class="w-full overflow-x-auto py-2 flex justify-center">
          <svg class="h-28 max-w-full" viewBox="0 0 320 100">
            <!-- Center Barbell Shaft -->
            <rect x="0" y="44" width="70" height="12" fill="#64748b" rx="2" />
            <!-- Barbell Collar Stopper -->
            <rect x="70" y="25" width="12" height="50" fill="#334155" rx="3" stroke="#475569" stroke-width="1" />
            <!-- Barbell Loading Sleeve -->
            <rect x="82" y="42" width="230" height="16" fill="#94a3b8" rx="2" />

            <!-- Render Loaded Plates -->
            {#each calculation.platesPerSide as group, gIdx}
              {#each Array(group.count) as _, pIdx}
                {@const offset = 86 + (gIdx * 30) + (pIdx * (group.plate.width + 3))}
                <rect
                  x={offset}
                  y={50 - group.plate.height / 2}
                  width={group.plate.width}
                  height={group.plate.height}
                  fill={group.plate.color}
                  rx="3"
                  stroke="rgba(0,0,0,0.25)"
                  stroke-width="1.5"
                />
                <text
                  x={offset + group.plate.width / 2}
                  y="53"
                  fill={group.plate.textColor}
                  font-size="8"
                  font-weight="bold"
                  text-anchor="middle"
                  transform="rotate(-90 {offset + group.plate.width / 2} 53)"
                >
                  {group.plate.weight}
                </text>
              {/each}
            {/each}
          </svg>
        </div>

        <!-- Plates Breakdown Chips -->
        <div class="flex flex-wrap gap-2 justify-center">
          {#each calculation.platesPerSide as p}
            <div class="px-2.5 py-1 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] flex items-center gap-1.5 shadow-2xs">
              <span class="w-3 h-3 rounded-full border border-black/20" style="background-color: {p.plate.color};"></span>
              <span class="text-xs font-bold text-[var(--text-main)] tabular-nums">{p.count} &times; {p.plate.weight} kg</span>
            </div>
          {/each}
        </div>

      </div>

      <!-- Action Buttons -->
      <div class="flex items-center justify-between pt-2 border-t border-[var(--border-subtle)]">
        <Btn variant="secondary" size="sm" onclick={onclose}>
          Abbrechen
        </Btn>
        <button
          type="button"
          onclick={() => {
            onapplyweight(targetWeight);
            onclose();
          }}
          class="px-5 py-2.5 rounded-xl bg-[var(--color-activity)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md flex items-center gap-2"
        >
          <span>{targetWeight} kg übernehmen</span>
        </button>
      </div>

    </div>
  </div>
{/if}
