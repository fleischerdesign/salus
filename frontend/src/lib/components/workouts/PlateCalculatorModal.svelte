<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Select from '../ui/Select.svelte';
  import Modal from '../ui/Modal.svelte';

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
  let barWeight = $state(20); // 20kg Olympia, 15kg Frauen, 10kg SZ, 0kg Maschine

  const barbellOptions = [
    { value: 20, label: 'Olympia (20 kg)' },
    { value: 15, label: 'Frauen (15 kg)' },
    { value: 10, label: 'SZ / Kurz (10 kg)' },
    { value: 0, label: 'Maschine (0 kg)' }
  ];

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

  // Official IWF / IPF Standard Color Codes & Proportions
  const AVAILABLE_PLATES: PlateSpec[] = [
    { weight: 25, color: '#dc2626', textColor: '#ffffff', height: 96, width: 14 },
    { weight: 20, color: '#2563eb', textColor: '#ffffff', height: 92, width: 13 },
    { weight: 15, color: '#eab308', textColor: '#0f172a', height: 80, width: 11 },
    { weight: 10, color: '#16a34a', textColor: '#ffffff', height: 68, width: 10 },
    { weight: 5, color: '#f8fafc', textColor: '#0f172a', height: 54, width: 8 },
    { weight: 2.5, color: '#334155', textColor: '#ffffff', height: 44, width: 7 },
    { weight: 1.25, color: '#94a3b8', textColor: '#0f172a', height: 36, width: 6 },
    { weight: 0.5, color: '#cbd5e1', textColor: '#0f172a', height: 28, width: 5 }
  ];

  interface LoadedPlateItem {
    weight: number;
    color: string;
    textColor: string;
    height: number;
    width: number;
    x: number;
  }

  let calculation = $derived.by(() => {
    const isUnderweight = targetWeight < barWeight;
    const weightToLoad = Math.max(0, targetWeight - barWeight);
    const weightPerSide = weightToLoad / 2;
    let remaining = weightPerSide;

    const platesGrouped: { plate: PlateSpec; count: number }[] = [];
    const sequentialPlates: LoadedPlateItem[] = [];

    let currentX = 74; // Starts directly against the barbell stopper collar

    if (!isUnderweight && weightToLoad > 0) {
      for (const plate of AVAILABLE_PLATES) {
        if (remaining >= plate.weight) {
          const count = Math.floor(remaining / plate.weight);
          platesGrouped.push({ plate, count });

          for (let i = 0; i < count; i++) {
            sequentialPlates.push({
              weight: plate.weight,
              color: plate.color,
              textColor: plate.textColor,
              height: plate.height,
              width: plate.width,
              x: currentX
            });
            currentX += plate.width + 2.5; // Precise gap between bumper plates
          }

          remaining = Math.round((remaining - count * plate.weight) * 100) / 100;
        }
      }
    }

    const actualLoadedSide = platesGrouped.reduce((acc, p) => acc + p.plate.weight * p.count, 0);
    const totalActualWeight = barWeight + actualLoadedSide * 2;
    const clampPosition = sequentialPlates.length > 0 ? currentX : null;

    return {
      isUnderweight,
      isExact: Math.abs(totalActualWeight - targetWeight) < 0.01,
      weightPerSide,
      platesGrouped,
      sequentialPlates,
      clampPosition,
      totalActualWeight,
      remainder: remaining
    };
  });

  function adjustTargetWeight(delta: number) {
    targetWeight = Math.max(0, Math.round((targetWeight + delta) * 100) / 100);
  }
</script>

<Modal
  {open}
  title="Hantelscheiben-Rechner"
  subtitle="Beladeplan für eine Hantelseite (Sleeve-Ansicht)"
  icon="calculate"
  size="md"
  {onclose}
>
  <div class="space-y-5">
    <!-- Single Unified Weight Input & Barbell Selection -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-12">
      <!-- Target Weight Input with Direct Steppers -->
      <div class="space-y-1 sm:col-span-7">
        <label
          for="plate-target-weight"
          class="text-[0.6875rem] font-bold text-text-muted uppercase"
        >
          Zielgewicht (gesamt)
        </label>
        <div class="flex items-center gap-1.5">
          <button
            type="button"
            onclick={() => adjustTargetWeight(-2.5)}
            class="h-10 w-10 shrink-0 cursor-pointer rounded-xl border border-border-subtle bg-surface-0 text-sm font-black text-text-muted transition-all hover:bg-surface-50 hover:text-text-main active:scale-95"
            title="-2.5 kg"
          >
            -2.5
          </button>
          <div class="flex-1">
            <Input type="number" step="0.5" unit="kg" bind:value={targetWeight} />
          </div>
          <button
            type="button"
            onclick={() => adjustTargetWeight(2.5)}
            class="h-10 w-10 shrink-0 cursor-pointer rounded-xl border border-border-subtle bg-surface-0 text-sm font-black text-text-muted transition-all hover:bg-surface-50 hover:text-text-main active:scale-95"
            title="+2.5 kg"
          >
            +2.5
          </button>
        </div>
      </div>

      <!-- Barbell Selection -->
      <div class="sm:col-span-5">
        <Select label="Hantelstange" bind:value={barWeight} options={barbellOptions} />
      </div>
    </div>

    <!-- VISUAL BARBELL SLEEVE GRAPHIC & BREAKDOWN -->
    <div
      class="flex flex-col items-center justify-center space-y-3.5 rounded-2xl border border-border-subtle bg-surface-50 p-4 sm:p-5"
    >
      <!-- Summary Numbers -->
      <div class="flex w-full items-center justify-between border-b border-border-subtle/60 pb-3">
        <div>
          <span class="block text-[0.6875rem] font-bold text-text-muted uppercase">Stange</span>
          <span class="text-sm font-extrabold text-text-main tabular-nums"
            >{barWeight.toFixed(1)} kg</span
          >
        </div>

        <div class="text-center">
          <span class="block text-[0.6875rem] font-bold text-primary uppercase"
            >Beladung pro Seite</span
          >
          <span class="text-2xl font-black text-primary tabular-nums">
            {calculation.weightPerSide.toFixed(2)} kg
          </span>
        </div>

        <div class="text-right">
          <span class="block text-[0.6875rem] font-bold text-text-muted uppercase"
            >Gesamtgewicht</span
          >
          <span class="text-sm font-extrabold text-text-main tabular-nums"
            >{targetWeight.toFixed(1)} kg</span
          >
        </div>
      </div>

      <!-- Warning / Edge-Case Notice -->
      {#if calculation.isUnderweight}
        <div
          class="flex w-full items-center justify-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-center text-xs font-semibold text-amber-600"
        >
          <Icon name="warning" size="sm" />
          <span>Zielgewicht liegt unter dem Eigengewicht der Stange ({barWeight} kg).</span>
        </div>
      {:else if calculation.weightPerSide === 0}
        <div
          class="flex w-full items-center justify-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-center text-xs font-semibold text-emerald-600"
        >
          <Icon name="check-circle" size="sm" />
          <span>Nur Hantelstange – keine Hantelscheiben erforderlich.</span>
        </div>
      {/if}

      <!-- HIGH-FIDELITY SVG BARBELL SLEEVE WITH REALISTIC SECTIONAL CUT -->
      <div class="no-scrollbar flex w-full justify-center overflow-x-auto py-2">
        <svg class="h-32 max-w-full" viewBox="0 0 340 120">
          <defs>
            <!-- Metallic Gradients -->
            <linearGradient id="barShaftGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#94a3b8" />
              <stop offset="40%" stop-color="#cbd5e1" />
              <stop offset="100%" stop-color="#475569" />
            </linearGradient>

            <linearGradient id="barSleeveGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#cbd5e1" />
              <stop offset="35%" stop-color="#f8fafc" />
              <stop offset="75%" stop-color="#94a3b8" />
              <stop offset="100%" stop-color="#475569" />
            </linearGradient>

            <linearGradient id="collarGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#475569" />
              <stop offset="50%" stop-color="#64748b" />
              <stop offset="100%" stop-color="#1e293b" />
            </linearGradient>

            <!-- Knurling Texture on Shaft -->
            <pattern id="knurlPattern" width="4" height="4" patternUnits="userSpaceOnUse">
              <path d="M0 4L4 0M0 0L4 4" stroke="#334155" stroke-width="0.75" opacity="0.3" />
            </pattern>
          </defs>

          <!-- 1. LEFT: Shaft Continuation to Barbell Center (with Breakline Jag) -->
          <path d="M 5 52 L 12 60 L 5 68 L 62 68 L 62 52 Z" fill="url(#barShaftGrad)" />
          <path d="M 12 52 L 19 60 L 12 68 L 62 68 L 62 52 Z" fill="url(#knurlPattern)" />

          <!-- Architecture Directional Text -->
          <text
            x="36"
            y="44"
            font-size="7"
            fill="var(--text-soft)"
            text-anchor="middle"
            font-weight="900"
            letter-spacing="0.5"
          >
            &larr; MITTE
          </text>

          <!-- 2. BARBELL COLLAR STOPPER (Anschlagring / Bund) -->
          <rect
            x="62"
            y="24"
            width="12"
            height="72"
            fill="url(#collarGrad)"
            rx="3"
            stroke="#334155"
            stroke-width="1.2"
          />
          <line x1="68" y1="26" x2="68" y2="94" stroke="rgba(255,255,255,0.2)" stroke-width="1" />

          <!-- 3. BARBELL LOADING SLEEVE (50mm Hülse) -->
          <rect
            x="74"
            y="50"
            width="240"
            height="20"
            fill="url(#barSleeveGrad)"
            rx="2"
            stroke="#64748b"
            stroke-width="1"
          />

          <!-- Sleeve End Cap (Außenkappe) -->
          <rect
            x="310"
            y="48"
            width="8"
            height="24"
            fill="#334155"
            rx="3"
            stroke="#1e293b"
            stroke-width="1"
          />
          <circle cx="314" cy="60" r="3.5" fill="#64748b" />

          <!-- 4. RENDER SEQUENTIALLY LOADED PLATES -->
          {#each calculation.sequentialPlates as plate}
            <!-- Plate Shadow -->
            <rect
              x={plate.x + 1}
              y={60 - plate.height / 2 + 1}
              width={plate.width}
              height={plate.height}
              fill="rgba(0,0,0,0.25)"
              rx="3"
            />
            <!-- Plate Outer Bumper Body -->
            <rect
              x={plate.x}
              y={60 - plate.height / 2}
              width={plate.width}
              height={plate.height}
              fill={plate.color}
              rx="3"
              stroke="rgba(0,0,0,0.35)"
              stroke-width="1.2"
            />
            <!-- Inner Chrome Hub Ring -->
            <rect
              x={plate.x + 0.5}
              y="53"
              width={plate.width - 1}
              height="14"
              fill="#e2e8f0"
              opacity="0.85"
              rx="1"
            />
            <!-- Embossed Weight Text -->
            <text
              x={plate.x + plate.width / 2}
              y="63"
              fill={plate.textColor}
              font-size="8.5"
              font-weight="900"
              text-anchor="middle"
              transform="rotate(-90 {plate.x + plate.width / 2} 63)"
            >
              {plate.weight}
            </text>
          {/each}

          <!-- 5. QUICK-LOCK BARBELL CLAMP / VERSCHLUSS (Hält die Scheiben fest) -->
          {#if calculation.clampPosition}
            <g transform="translate({calculation.clampPosition}, 0)">
              <!-- Clamp Body -->
              <rect
                x="0"
                y="42"
                width="10"
                height="36"
                fill="#0f172a"
                rx="2.5"
                stroke="#334155"
                stroke-width="1"
              />
              <rect x="2" y="45" width="6" height="30" fill="#3b82f6" rx="1.5" />
              <!-- Clamp Quick-Release Lever -->
              <path d="M 5 42 L 5 32 L 8 32 L 8 42 Z" fill="#94a3b8" />
            </g>
          {/if}
        </svg>
      </div>

      <!-- Explanatory Legend / Hint -->
      <div
        class="flex items-center gap-1.5 rounded-full border border-border-subtle bg-surface-0/80 px-3 py-1 text-[0.6875rem] font-bold text-text-muted"
      >
        <Icon name="tune" size="sm" class="text-primary" />
        <span>Auf beiden Seiten der Hantelstange identisch aufstecken</span>
      </div>

      <!-- Plates Breakdown Chips -->
      {#if calculation.platesGrouped.length > 0}
        <div class="flex flex-wrap justify-center gap-2 pt-1">
          {#each calculation.platesGrouped as p}
            <div
              class="flex items-center gap-1.5 rounded-xl border border-border-subtle bg-surface-0 px-2.5 py-1 shadow-2xs"
            >
              <span
                class="h-3 w-3 shrink-0 rounded-full border border-black/20"
                style="background-color: {p.plate.color};"
              ></span>
              <span class="text-xs font-black text-text-main tabular-nums"
                >{p.count} &times; {p.plate.weight} kg</span
              >
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-end gap-2 border-t border-border-subtle pt-3">
      <Btn variant="secondary" size="md" onclick={onclose}>Abbrechen</Btn>
      <Btn
        variant="primary"
        size="md"
        onclick={() => {
          onapplyweight(targetWeight);
          onclose();
        }}
      >
        {targetWeight} kg übernehmen
      </Btn>
    </div>
  </div>
</Modal>
