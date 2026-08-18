<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import TextInput from '../ui/TextInput.svelte';
  import NumberStepper from '../ui/NumberStepper.svelte';
  import SliderRange from '../ui/SliderRange.svelte';

  export type QuickLogCategory =
    | 'water'
    | 'food'
    | 'blood_pressure'
    | 'weight'
    | 'glucose'
    | 'caffeine'
    | 'medications'
    | 'sleep'
    | 'mood';

  let {
    open = false,
    initialCategory = 'water',
    onclose,
    onsubmitwater,
    onopenbarcode
  } = $props<{
    open: boolean;
    initialCategory?: QuickLogCategory;
    onclose: () => void;
    onsubmitwater?: (amountMl: number) => void;
    onopenbarcode?: () => void;
  }>();

  let activeCategory = $state<QuickLogCategory>('water');

  $effect(() => {
    if (open) {
      activeCategory = initialCategory || 'water';
      successToast = '';
    }
  });

  // Success Feedback Message
  let successToast = $state<string>('');

  function triggerSuccess(msg: string) {
    successToast = msg;
    setTimeout(() => {
      successToast = '';
      onclose();
    }, 900);
  }

  // ─── 1. WATER STATE ───
  let waterCurrentInput = $state(250);
  function addWaterQuick(amount: number) {
    onsubmitwater?.(amount);
    triggerSuccess(`+${amount} ml Wasser erfolgreich protokolliert!`);
  }

  // ─── 2. FOOD STATE (ERNÄHRUNG & SCHNELL-MAHLZEITEN) ───
  let mealSlot = $state<'breakfast' | 'lunch' | 'dinner' | 'snack'>('lunch');
  let foodKcal = $state(550);
  let foodProtein = $state(42);
  let foodCarbs = $state(60);
  let foodFat = $state(14);

  const quickMealFavorites = [
    { name: 'Haferflocken und Whey Protein Bowl', kcal: 520, protein: 44, carbs: 62, fat: 9, icon: '' },
    { name: 'Hähnchenbrust mit Reis und Brokkoli', kcal: 640, protein: 56, carbs: 75, fat: 10, icon: '' },
    { name: 'Protein Shake (Isolat mit Mandelmilch)', kcal: 220, protein: 38, carbs: 4, fat: 3, icon: '' },
    { name: 'Griechischer Joghurt mit Beeren und Nüssen', kcal: 340, protein: 26, carbs: 22, fat: 16, icon: '' }
  ];

  function submitQuickMeal(meal: typeof quickMealFavorites[0]) {
    triggerSuccess(`„${meal.name}“ (${meal.kcal} kcal, ${meal.protein}g Protein) erfasst!`);
  }

  function submitCustomFood() {
    triggerSuccess(`Mahlzeit (${foodKcal} kcal, ${foodProtein}g Protein, ${foodCarbs}g Carbs, ${foodFat}g Fett) erfasst!`);
  }

  // ─── 3. BLOOD PRESSURE STATE ───
  let systolic = $state(118);
  let diastolic = $state(76);
  let pulse = $state(64);

  let bpCategory = $derived.by(() => {
    if (systolic < 120 && diastolic < 80) return { label: 'Optimal (ESC 2024)', color: 'text-emerald-500', bg: 'bg-emerald-500/10 border-emerald-500/20' };
    if (systolic <= 129 && diastolic <= 84) return { label: 'Normal', color: 'text-teal-400', bg: 'bg-teal-400/10 border-teal-400/20' };
    if (systolic <= 139 || diastolic <= 89) return { label: 'Hoch-Normal', color: 'text-amber-400', bg: 'bg-amber-400/10 border-amber-400/20' };
    return { label: 'Hypertonie Grad 1', color: 'text-rose-500', bg: 'bg-rose-500/10 border-rose-500/20' };
  });

  function submitBloodPressure() {
    triggerSuccess(`Blutdruck ${systolic}/${diastolic} mmHg (${pulse} bpm) gespeichert!`);
  }

  // ─── 4. WEIGHT STATE ───
  let weightKg = $state(81.8);

  function adjustWeight(delta: number) {
    weightKg = Math.round((weightKg + delta) * 10) / 10;
  }

  function submitWeight() {
    triggerSuccess(`Körpergewicht ${weightKg.toFixed(1)} kg protokolliert!`);
  }

  // ─── 5. GLUCOSE STATE ───
  let glucoseVal = $state(94);
  let glucoseTiming = $state<'fasting' | 'pre_meal' | 'post_meal' | 'bedtime'>('fasting');

  function submitGlucose() {
    triggerSuccess(`Blutzucker ${glucoseVal} mg/dL erfasst!`);
  }

  // ─── 6. CAFFEINE STATE ───
  let caffeineCustomMg = $state(80);

  const caffeinePresets = [
    { name: 'Espresso', mg: 65, icon: '' },
    { name: 'Doppelter Espresso', mg: 130, icon: '' },
    { name: 'Filterkaffee (große Tasse)', mg: 110, icon: '' },
    { name: 'Grüner Tee (Matcha)', mg: 35, icon: '' },
    { name: 'Pre-Workout Booster', mg: 200, icon: '' }
  ];

  function submitCaffeine(mg: number, name: string) {
    triggerSuccess(`${name} (${mg} mg Koffein) protokolliert!`);
  }

  // ─── 7. MEDICATIONS & SUPPLEMENTS STATE ───
  interface MedScheduleItem {
    id: string;
    name: string;
    dose: string;
    time: string;
    taken: boolean;
  }

  let medsList = $state<MedScheduleItem[]>([
    { id: 'm1', name: 'L-Thyroxin', dose: '50 µg', time: 'Morgens (Nüchtern)', taken: true },
    { id: 'm2', name: 'Telmisartan', dose: '20 mg', time: 'Morgens', taken: true },
    { id: 'm3', name: 'Kreatin Monohydrat', dose: '5 g', time: 'Mittags', taken: false },
    { id: 'm4', name: 'Omega-3 EPA/DHA', dose: '2.000 mg', time: 'Mittags', taken: false },
    { id: 'm5', name: 'Magnesium-Bisglycinat', dose: '400 mg', time: 'Abends', taken: false }
  ]);

  function toggleMed(id: string) {
    const item = medsList.find(m => m.id === id);
    if (item) {
      item.taken = !item.taken;
    }
  }

  function submitAllDueMeds() {
    const count = medsList.filter(m => m.taken).length;
    triggerSuccess(`${count} Medikamente und Dosen als eingenommen bestätigt!`);
  }

  // ─── 8. SLEEP STATE ───
  let sleepHours = $state(7);
  let sleepMinutes = $state(45);
  let sleepQuality = $state(4); // 1-5

  function submitSleep() {
    triggerSuccess(`Schlaf ${sleepHours}h ${sleepMinutes}m (Qualität ${sleepQuality}/5) erfasst!`);
  }

  // ─── 9. MOOD & ENERGY STATE ───
  let moodScore = $state(4);
  let energyLevel = $state(8);

  const moodLevels = [
    { score: 1, label: 'Erschöpft' },
    { score: 2, label: 'Gestresst' },
    { score: 3, label: 'Neutral' },
    { score: 4, label: 'Gut' },
    { score: 5, label: 'Exzellent' }
  ];

  function submitMood() {
    triggerSuccess(`Stimmung und Energie (${energyLevel}/10) erfolgreich erfasst!`);
  }

  const categoryTabs: { id: QuickLogCategory; label: string }[] = [
    { id: 'water', label: 'Wasser' },
    { id: 'food', label: 'Ernährung' },
    { id: 'blood_pressure', label: 'Blutdruck' },
    { id: 'weight', label: 'Gewicht' },
    { id: 'glucose', label: 'Glukose' },
    { id: 'caffeine', label: 'Koffein' },
    { id: 'medications', label: 'Medikamente' },
    { id: 'sleep', label: 'Schlaf' },
    { id: 'mood', label: 'Stimmung' }
  ];
</script>

{#if open}
  <div
    class="fixed inset-0 bg-black/75 backdrop-blur-md z-70 flex items-center justify-center p-4 overflow-y-auto"
    onclick={(e) => {
      if (e.target === e.currentTarget) onclose();
    }}
    role="presentation"
  >
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-7 max-w-lg w-full shadow-2xl space-y-5 animate-[fadeIn_0.2s_ease-out] relative">
      
      <!-- SUCCESS TOAST OVERLAY -->
      {#if successToast}
        <div class="absolute inset-0 bg-[var(--glass-dock-bg)]/95 backdrop-blur-2xl rounded-3xl flex flex-col items-center justify-center p-6 text-center z-50 animate-[scaleIn_0.15s_ease-out]">
          <div class="w-14 h-14 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center text-3xl mb-2">
           
          </div>
          <h3 class="text-base font-extrabold text-[var(--text-main)]">Gespeichert!</h3>
          <p class="text-xs font-semibold text-[var(--text-muted)] mt-1">{successToast}</p>
        </div>
      {/if}

      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold text-lg shrink-0">
            
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-extrabold text-[var(--text-main)]">1-Tap Schnellerfassung</h2>
              <Badge variant="primary" class="text-[0.5625rem] font-bold">Taste L</Badge>
            </div>
            <p class="text-xs text-[var(--text-muted)] mt-0.5">Biometrische Werte sekundenschnell protokollieren</p>
          </div>
        </div>

        <button
          type="button"
          onclick={onclose}
          class="w-8 h-8 rounded-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center text-lg cursor-pointer transition-colors"
          title="Schließen (Escape)"
          aria-label="Schließen"
        >
          &times;
        </button>
      </div>

      <!-- Fluid Horizontal Category Pills with Soft Mask Fades -->
      <div class="relative w-full overflow-hidden">
        <div class="flex gap-2 overflow-x-auto py-1 px-1 no-scrollbar scroll-mask-x select-none">
          {#each categoryTabs as tab}
            <button
              type="button"
              onclick={() => activeCategory = tab.id}
              class="px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap cursor-pointer transition-all shrink-0 flex items-center gap-1.5 {activeCategory === tab.id ? 'bg-[var(--color-primary)] text-white shadow-xs' : 'bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
            >
              <span>{tab.label}</span>
            </button>
          {/each}
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- 1. WASSER & HYDRATION (1-TAP CARDS)                         -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if activeCategory === 'water'}
        <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
          <span class="text-xs font-extrabold text-[var(--text-main)] block">
            Wähle eine Portionsgröße mit 1 Tap:
          </span>

          <!-- 4 Big Tactile Quick Tap Cards -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <button
              type="button"
              onclick={() => addWaterQuick(250)}
              class="p-3.5 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] hover:border-[var(--color-hydrate)] hover:bg-[var(--color-hydrate)]/5 flex flex-col items-center justify-center text-center cursor-pointer transition-all active:scale-95 group shadow-2xs"
            >
              <span class="text-2xl mb-1 group-hover:scale-110 transition-transform"></span>
              <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums">+250 ml</span>
              <span class="text-[0.625rem] text-[var(--text-muted)]">Glas Wasser</span>
            </button>

            <button
              type="button"
              onclick={() => addWaterQuick(500)}
              class="p-3.5 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] hover:border-[var(--color-hydrate)] hover:bg-[var(--color-hydrate)]/5 flex flex-col items-center justify-center text-center cursor-pointer transition-all active:scale-95 group shadow-2xs"
            >
              <span class="text-2xl mb-1 group-hover:scale-110 transition-transform"></span>
              <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums">+500 ml</span>
              <span class="text-[0.625rem] text-[var(--text-muted)]">Flasche</span>
            </button>

            <button
              type="button"
              onclick={() => addWaterQuick(750)}
              class="p-3.5 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] hover:border-[var(--color-hydrate)] hover:bg-[var(--color-hydrate)]/5 flex flex-col items-center justify-center text-center cursor-pointer transition-all active:scale-95 group shadow-2xs"
            >
              <span class="text-2xl mb-1 group-hover:scale-110 transition-transform"></span>
              <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums">+750 ml</span>
              <span class="text-[0.625rem] text-[var(--text-muted)]">Sport-Shaker</span>
            </button>

            <button
              type="button"
              onclick={() => addWaterQuick(1000)}
              class="p-3.5 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] hover:border-[var(--color-hydrate)] hover:bg-[var(--color-hydrate)]/5 flex flex-col items-center justify-center text-center cursor-pointer transition-all active:scale-95 group shadow-2xs"
            >
              <span class="text-2xl mb-1 group-hover:scale-110 transition-transform"></span>
              <span class="text-sm font-extrabold text-[var(--text-main)] tabular-nums">+1.000 ml</span>
              <span class="text-[0.625rem] text-[var(--text-muted)]">Karaffe</span>
            </button>
          </div>

          <!-- Custom Amount Slider -->
          <div class="p-3.5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-3">
            <SliderRange
              label="Individuelle Trinkmenge"
              min={50}
              max={1500}
              step={50}
              unit="ml"
              color="hydrate"
              bind:value={waterCurrentInput}
            />
            <div class="flex justify-end">
              <button
                type="button"
                onclick={() => addWaterQuick(waterCurrentInput)}
                class="px-4 py-2 rounded-xl bg-[var(--color-hydrate)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs"
              >
                {waterCurrentInput} ml protokollieren
              </button>
            </div>
          </div>
        </div>
      {/if}

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- 2. ERNÄHRUNG & FOOD (SCHNELL-MAHLZEITEN & BARCODE)         -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if activeCategory === 'food'}
        <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
          
          <!-- Barcode Scanner Fast Action -->
          <button
            type="button"
            onclick={() => {
              onclose();
              onopenbarcode?.();
            }}
            class="w-full p-3 rounded-2xl bg-[var(--color-primary)]/10 border border-[var(--color-primary)]/30 hover:bg-[var(--color-primary)]/15 text-[var(--color-primary)] font-bold text-xs flex items-center justify-center gap-2 cursor-pointer transition-all shadow-2xs"
          >
            <span> Barcode-Scanner öffnen</span>
          </button>

          <!-- Quick Meal Favorites (1-Tap) -->
          <div class="space-y-1.5">
            <span class="text-xs font-extrabold text-[var(--text-main)] block">Häufige Mahlzeiten (1-Tap):</span>
            <div class="space-y-1.5">
              {#each quickMealFavorites as meal}
                <button
                  type="button"
                  onclick={() => submitQuickMeal(meal)}
                  class="w-full p-2.5 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] hover:border-[var(--color-activity)] hover:bg-[var(--color-activity)]/5 flex items-center justify-between text-left cursor-pointer transition-all group shadow-2xs"
                >
                  <div class="flex items-center gap-2.5">
                    <span class="text-xl">{meal.icon}</span>
                    <div>
                      <span class="text-xs font-bold text-[var(--text-main)] block">{meal.name}</span>
                      <span class="text-[0.625rem] text-[var(--text-muted)]">{meal.protein}g Protein &bull; {meal.carbs}g Carbs &bull; {meal.fat}g Fett</span>
                    </div>
                  </div>
                  <Badge variant="activity" class="text-[0.625rem] font-bold tabular-nums">+{meal.kcal} kcal</Badge>
                </button>
              {/each}
            </div>
          </div>

          <!-- Quick Calorie & Macro Stepper Form -->
          <div class="p-3.5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-3">
            <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase block">Manuelle Schnelleingabe:</span>
            
            <div class="grid grid-cols-4 gap-2 text-center text-xs">
              <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-2">
                <span class="text-[0.625rem] text-[var(--text-muted)] block">Kalorien</span>
                <input type="number" bind:value={foodKcal} class="w-full text-center font-extrabold text-sm text-[var(--color-activity)] bg-transparent outline-none tabular-nums" />
                <span class="text-[0.5625rem] text-[var(--text-soft)]">kcal</span>
              </div>
              <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-2">
                <span class="text-[0.625rem] text-[var(--text-muted)] block">Protein</span>
                <input type="number" bind:value={foodProtein} class="w-full text-center font-extrabold text-sm text-emerald-500 bg-transparent outline-none tabular-nums" />
                <span class="text-[0.5625rem] text-[var(--text-soft)]">g</span>
              </div>
              <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-2">
                <span class="text-[0.625rem] text-[var(--text-muted)] block">Kohlenhydrate</span>
                <input type="number" bind:value={foodCarbs} class="w-full text-center font-extrabold text-sm text-amber-500 bg-transparent outline-none tabular-nums" />
                <span class="text-[0.5625rem] text-[var(--text-soft)]">g</span>
              </div>
              <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-2">
                <span class="text-[0.625rem] text-[var(--text-muted)] block">Fett</span>
                <input type="number" bind:value={foodFat} class="w-full text-center font-extrabold text-sm text-purple-500 bg-transparent outline-none tabular-nums" />
                <span class="text-[0.5625rem] text-[var(--text-soft)]">g</span>
              </div>
            </div>

            <button
              type="button"
              onclick={submitCustomFood}
              class="w-full py-2 rounded-xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs"
            >
              Mahlzeit ({foodKcal} kcal) protokollieren
            </button>
          </div>

        </div>
      {/if}

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- 3. BLUTDRUCK & PULS                                         -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if activeCategory === 'blood_pressure'}
        <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
          <div class="p-3 rounded-2xl border flex items-center justify-between {bpCategory.bg}">
            <div>
              <span class="text-[0.6875rem] text-[var(--text-muted)] font-bold uppercase block">Klinische Einstufung:</span>
              <span class="text-sm font-extrabold {bpCategory.color}">{bpCategory.label}</span>
            </div>
            <span class="text-xl font-extrabold tabular-nums {bpCategory.color}">
              {systolic} / {diastolic} <span class="text-xs font-semibold">mmHg</span>
            </span>
          </div>

          <div class="grid grid-cols-3 gap-3">
            <TextInput
              label="Systolisch"
              type="number"
              unit="mmHg"
              bind:value={systolic}
            />

            <TextInput
              label="Diastolisch"
              type="number"
              unit="mmHg"
              bind:value={diastolic}
            />

            <TextInput
              label="Puls"
              type="number"
              unit="bpm"
              bind:value={pulse}
            />
          </div>

          <button
            type="button"
            onclick={submitBloodPressure}
            class="w-full py-2.5 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md"
          >
            Messung speichern
          </button>
        </div>
      {/if}

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- 4. GEWICHT & KÖRPERZUSAMMENSETZUNG                          -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if activeCategory === 'weight'}
        <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
          <div class="p-4 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-3">
            <NumberStepper
              label="Körpergewicht"
              unit="kg"
              min={30}
              max={300}
              step={0.1}
              precision={1}
              quickSteps={[-0.5, -0.2, 0.2, 0.5]}
              bind:value={weightKg}
            />
          </div>

          <button
            type="button"
            onclick={submitWeight}
            class="w-full py-2.5 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md"
          >
            Gewicht {weightKg.toFixed(1)} kg speichern
          </button>
        </div>
      {/if}

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- 5. BLUTZUCKER (GLUKOSE)                                     -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if activeCategory === 'glucose'}
        <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
          <div class="p-4 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-3">
            <NumberStepper
              label="Glukose-Messwert"
              unit="mg/dL"
              min={30}
              max={500}
              step={1}
              precision={0}
              quickSteps={[-10, -5, 5, 10]}
              bind:value={glucoseVal}
            />

            <div class="text-center">
              {#if glucoseVal >= 70 && glucoseVal <= 140}
                <span class="text-xs font-bold text-emerald-500">Im optimalen Zielkorridor (70–140 mg/dL)</span>
              {:else if glucoseVal < 70}
                <span class="text-xs font-bold text-amber-500">Hypoglykämie (&lt; 70 mg/dL)</span>
              {:else}
                <span class="text-xs font-bold text-rose-500">Postprandialer Spike (&gt; 140 mg/dL)</span>
              {/if}
            </div>
          </div>

          <div class="space-y-1.5">
            <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase block">Mess-Zeitpunkt:</span>
            <div class="grid grid-cols-2 gap-2">
              <button
                type="button"
                onclick={() => glucoseTiming = 'fasting'}
                class="px-3 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer {glucoseTiming === 'fasting' ? 'bg-[var(--color-primary)] text-white border-transparent shadow-xs' : 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
              >
                Nüchtern (Morgen)
              </button>
              <button
                type="button"
                onclick={() => glucoseTiming = 'pre_meal'}
                class="px-3 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer {glucoseTiming === 'pre_meal' ? 'bg-[var(--color-primary)] text-white border-transparent shadow-xs' : 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
              >
                Vor Mahlzeit
              </button>
              <button
                type="button"
                onclick={() => glucoseTiming = 'post_meal'}
                class="px-3 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer {glucoseTiming === 'post_meal' ? 'bg-[var(--color-primary)] text-white border-transparent shadow-xs' : 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
              >
                1h Postprandial
              </button>
              <button
                type="button"
                onclick={() => glucoseTiming = 'bedtime'}
                class="px-3 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer {glucoseTiming === 'bedtime' ? 'bg-[var(--color-primary)] text-white border-transparent shadow-xs' : 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
              >
                Vor dem Schlafen
              </button>
            </div>
          </div>

          <button
            type="button"
            onclick={submitGlucose}
            class="w-full py-2.5 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md"
          >
            Glukosewert speichern
          </button>
        </div>
      {/if}

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- 6. KOFFEIN (DEDIZIERTE PHARMAKOKINETIK-ERFASSUNG)           -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if activeCategory === 'caffeine'}
        <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
          <span class="text-xs font-extrabold text-[var(--text-main)] block">Koffein-Dosis mit 1 Tap erfassen:</span>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {#each caffeinePresets as cp}
              <button
                type="button"
                onclick={() => submitCaffeine(cp.mg, cp.name)}
                class="p-3 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] hover:border-[var(--color-activity)] hover:bg-[var(--color-activity)]/5 flex items-center justify-between text-left cursor-pointer transition-all active:scale-95 group shadow-2xs"
              >
                <div class="flex items-center gap-2.5">
                  <span class="text-xl">{cp.icon}</span>
                  <div>
                    <span class="text-xs font-bold text-[var(--text-main)] block">{cp.name}</span>
                    <span class="text-[0.625rem] text-[var(--text-muted)]">CYP1A2 Clearance: ~5.5h</span>
                  </div>
                </div>
                <Badge variant="activity" class="text-[0.625rem] font-bold tabular-nums">+{cp.mg} mg</Badge>
              </button>
            {/each}
          </div>

          <!-- Custom Caffeine Slider -->
          <div class="p-3.5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-2">
            <div class="flex justify-between items-center text-xs">
              <span class="font-bold text-[var(--text-main)]">Individuelle Dosis:</span>
              <span class="text-sm font-extrabold text-[var(--color-activity)] tabular-nums">{caffeineCustomMg} mg</span>
            </div>
            <input
              type="range"
              min="10"
              max="400"
              step="10"
              bind:value={caffeineCustomMg}
              class="w-full accent-[var(--color-activity)] cursor-pointer"
            />
            <div class="pt-1 flex justify-end">
              <button
                type="button"
                onclick={() => submitCaffeine(caffeineCustomMg, 'Individuelles Koffein')}
                class="px-4 py-1.5 rounded-xl bg-[var(--color-activity)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs"
              >
                {caffeineCustomMg} mg erfassen
              </button>
            </div>
          </div>
        </div>
      {/if}

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- 7. MEDIKAMENTE & SUPPLEMENTE (TAGESPLAN-CHECKLISTE)         -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if activeCategory === 'medications'}
        <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold text-[var(--text-main)] block">Heutiger Medikamenten- und Einnahmeplan:</span>
            <span class="text-[0.6875rem] text-[var(--text-muted)] font-semibold">1-Tap Bestätigung</span>
          </div>

          <div class="space-y-2 max-h-[42vh] overflow-y-auto pr-1">
            {#each medsList as med}
              <button
                type="button"
                onclick={() => toggleMed(med.id)}
                class="w-full p-3 rounded-2xl border flex items-center justify-between text-left cursor-pointer transition-all {med.taken ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-700 dark:text-emerald-300 shadow-2xs' : 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
              >
                <div class="flex items-center gap-2.5">
                  <span class="w-6 h-6 rounded-lg flex items-center justify-center font-bold text-xs {med.taken ? 'bg-emerald-500 text-white' : 'bg-[var(--bg-surface-50)] text-[var(--text-muted)] border border-[var(--border-subtle)]'}">
                    {med.taken ? '' : '○'}
                  </span>
                  <div>
                    <span class="text-xs font-extrabold text-[var(--text-main)] block">{med.name}</span>
                    <span class="text-[0.625rem] text-[var(--text-muted)]">{med.dose} &bull; {med.time}</span>
                  </div>
                </div>

                <Badge variant={med.taken ? 'success' : 'default'} class="text-[0.625rem] font-bold">
                  {med.taken ? 'Eingenommen' : 'Ausstehend'}
                </Badge>
              </button>
            {/each}
          </div>

          <button
            type="button"
            onclick={submitAllDueMeds}
            class="w-full py-2.5 rounded-2xl bg-emerald-500 text-white text-xs font-bold hover:bg-emerald-600 transition-all cursor-pointer shadow-md"
          >
            Einnahmen bestätigen
          </button>
        </div>
      {/if}

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- 8. SCHLAF & ERHOLUNG                                        -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if activeCategory === 'sleep'}
        <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
          <div class="p-4 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl text-center space-y-2">
            <span class="text-[0.6875rem] text-[var(--text-muted)] font-bold uppercase block">Schlafdauer</span>
            <div class="flex items-center justify-center gap-3">
              <div class="flex items-center gap-1">
                <input
                  type="number"
                  min="0"
                  max="16"
                  bind:value={sleepHours}
                  class="w-12 text-center text-2xl font-extrabold text-[var(--text-main)] bg-transparent outline-none tabular-nums"
                />
                <span class="text-xs font-bold text-[var(--text-muted)]">Std</span>
              </div>
              <span class="text-lg font-bold text-[var(--text-soft)]">:</span>
              <div class="flex items-center gap-1">
                <input
                  type="number"
                  min="0"
                  max="59"
                  step="5"
                  bind:value={sleepMinutes}
                  class="w-12 text-center text-2xl font-extrabold text-[var(--text-main)] bg-transparent outline-none tabular-nums"
                />
                <span class="text-xs font-bold text-[var(--text-muted)]">Min</span>
              </div>
            </div>
          </div>

          <!-- Quality Rating -->
          <div class="space-y-1.5">
            <span class="text-[0.6875rem] font-bold text-[var(--text-muted)] uppercase block">Schlafqualität:</span>
            <div class="flex justify-between gap-1.5">
              {#each [1, 2, 3, 4, 5] as star}
                <button
                  type="button"
                  onclick={() => sleepQuality = star}
                  class="flex-1 py-2 rounded-xl border text-sm font-bold transition-all cursor-pointer {sleepQuality === star ? 'bg-[var(--color-primary)] text-white border-transparent shadow-xs' : 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                >
                  {'Stern'.repeat(star)}
                </button>
              {/each}
            </div>
          </div>

          <button
            type="button"
            onclick={submitSleep}
            class="w-full py-2.5 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md"
          >
            Schlafdaten speichern
          </button>
        </div>
      {/if}

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- 9. STIMMUNG & ENERGIE                                       -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if activeCategory === 'mood'}
        <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
          <span class="text-xs font-extrabold text-[var(--text-main)] block">Wie fühlst du dich aktuell?</span>
          
          <div class="grid grid-cols-5 gap-2">
            {#each moodLevels as ml}
              <button
                type="button"
                onclick={() => moodScore = ml.score}
                class="p-3 rounded-2xl border flex flex-col items-center justify-center text-center cursor-pointer transition-all active:scale-95 {moodScore === ml.score ? 'bg-[var(--color-primary)] text-white border-transparent shadow-xs' : 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
              >
                <span class="text-sm font-extrabold mb-1 tabular-nums">{ml.score}</span>
                <span class="text-[0.625rem] font-bold">{ml.label}</span>
              </button>
            {/each}
          </div>

          <div class="p-3.5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-2">
            <div class="flex justify-between items-center text-xs">
              <span class="font-bold text-[var(--text-main)]">Energie-Level:</span>
              <span class="text-sm font-extrabold text-[var(--color-activity)] tabular-nums">{energyLevel} / 10</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              bind:value={energyLevel}
              class="w-full accent-[var(--color-activity)] cursor-pointer"
            />
          </div>

          <button
            type="button"
            onclick={submitMood}
            class="w-full py-2.5 rounded-2xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-md"
          >
            Stimmung erfassen
          </button>
        </div>
      {/if}

    </div>
  </div>
{/if}
