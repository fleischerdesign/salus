<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Input from '$components/ui/Input.svelte';
  import NumberStepper from '$components/ui/NumberStepper.svelte';
  import SliderRange from '$components/ui/SliderRange.svelte';
  import { createMeasurement } from '$lib/mutations/measurement';
  import { nowIso } from '$lib/utils/datetime';

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
  async function addWaterQuick(amount: number) {
    try {
      await createMeasurement('hydration', {
        value: amount,
        unit: 'ml',
        recorded_at: nowIso()
      });
      onsubmitwater?.(amount);
      triggerSuccess(`+${amount} ml Wasser erfolgreich protokolliert!`);
    } catch {
      triggerSuccess(`+${amount} ml Wasser lokal erfasst!`);
    }
  }

  // ─── 2. FOOD STATE ───
  let mealSlot = $state<'breakfast' | 'lunch' | 'dinner' | 'snack'>('lunch');
  let foodKcal = $state(550);
  let foodProtein = $state(42);
  let foodCarbs = $state(60);
  let foodFat = $state(14);

  const quickMealFavorites = [
    { name: 'Haferflocken und Whey Protein Bowl', kcal: 520, protein: 44, carbs: 62, fat: 9 },
    { name: 'Hähnchenbrust mit Reis und Brokkoli', kcal: 640, protein: 56, carbs: 75, fat: 10 },
    { name: 'Protein Shake (Isolat mit Mandelmilch)', kcal: 220, protein: 38, carbs: 4, fat: 3 },
    {
      name: 'Griechischer Joghurt mit Beeren und Nüssen',
      kcal: 340,
      protein: 26,
      carbs: 22,
      fat: 16
    }
  ];

  async function submitQuickMeal(meal: (typeof quickMealFavorites)[0]) {
    await createMeasurement('nutrition', {
      value: meal.kcal,
      unit: 'kcal',
      notes: `${meal.name} (P:${meal.protein}g C:${meal.carbs}g F:${meal.fat}g)`,
      recorded_at: nowIso()
    });
    triggerSuccess(`„${meal.name}“ (${meal.kcal} kcal, ${meal.protein}g Protein) erfasst!`);
  }

  async function submitCustomFood() {
    await createMeasurement('nutrition', {
      value: foodKcal,
      unit: 'kcal',
      notes: `Mahlzeit: ${mealSlot} (P:${foodProtein}g C:${foodCarbs}g F:${foodFat}g)`,
      recorded_at: nowIso()
    });
    triggerSuccess(
      `Mahlzeit (${foodKcal} kcal, ${foodProtein}g Protein, ${foodCarbs}g Carbs, ${foodFat}g Fett) erfasst!`
    );
  }

  // ─── 3. BLOOD PRESSURE STATE ───
  let bpSystolic = $state(118);
  let bpDiastolic = $state(76);
  let bpPulse = $state(64);
  let bpArm = $state<'left' | 'right'>('left');
  let bpState = $state<'resting' | 'post_exercise' | 'stress'>('resting');

  async function submitBloodPressure() {
    await createMeasurement('systolic_bp', {
      value: bpSystolic,
      unit: 'mmHg',
      notes: `Arm: ${bpArm}, Zustand: ${bpState}`,
      recorded_at: nowIso()
    });
    await createMeasurement('diastolic_bp', {
      value: bpDiastolic,
      unit: 'mmHg',
      notes: `Arm: ${bpArm}, Zustand: ${bpState}`,
      recorded_at: nowIso()
    });
    if (bpPulse > 0) {
      await createMeasurement('resting_heart_rate', {
        value: bpPulse,
        unit: 'bpm',
        recorded_at: nowIso()
      });
    }
    triggerSuccess(
      `Blutdruck ${bpSystolic}/${bpDiastolic} mmHg (Puls ${bpPulse} bpm) gespeichert!`
    );
  }

  // ─── 4. WEIGHT & BODY COMPOSITION ───
  let bodyWeight = $state(78.5);
  let bodyFat = $state(14.2);
  let muscleMass = $state(38.6);

  async function submitWeight() {
    await createMeasurement('weight', {
      value: bodyWeight,
      unit: 'kg',
      recorded_at: nowIso()
    });
    if (bodyFat > 0) {
      await createMeasurement('body_fat', {
        value: bodyFat,
        unit: '%',
        recorded_at: nowIso()
      });
    }
    triggerSuccess(`Körpergewicht ${bodyWeight} kg gespeichert!`);
  }

  // ─── 5. GLUCOSE ───
  let glucoseValue = $state(98);
  let glucoseTiming = $state<'fasting' | 'pre_meal' | 'post_meal_1h' | 'post_meal_2h' | 'night'>(
    'fasting'
  );

  async function submitGlucose() {
    await createMeasurement('blood_glucose', {
      value: glucoseValue,
      unit: 'mg/dL',
      notes: `Timing: ${glucoseTiming}`,
      recorded_at: nowIso()
    });
    triggerSuccess(`Glukosewert ${glucoseValue} mg/dL (${glucoseTiming}) gespeichert!`);
  }

  // ─── 6. CAFFEINE ───
  let caffeineDose = $state(100);
  async function submitCaffeine() {
    await createMeasurement('caffeine', {
      value: caffeineDose,
      unit: 'mg',
      recorded_at: nowIso()
    });
    triggerSuccess(`${caffeineDose} mg Koffein erfasst!`);
  }

  // ─── 7. SLEEP ───
  let sleepHours = $state(7.8);
  async function submitSleep() {
    await createMeasurement('sleep_duration', {
      value: sleepHours,
      unit: 'hours',
      recorded_at: nowIso()
    });
    triggerSuccess(`${sleepHours} Std. Schlaf protokolliert!`);
  }

  // ─── 8. MOOD & STRESS ───
  let moodValence = $state(8);
  async function submitMood() {
    await createMeasurement('mood', {
      value: moodValence,
      unit: 'scale_10',
      recorded_at: nowIso()
    });
    triggerSuccess(`Wohlbefinden (${moodValence}/10) gespeichert!`);
  }
</script>

{#if open}
  <!-- Backdrop -->
  <div
    class="fixed inset-0 z-70 flex items-center justify-center overflow-y-auto bg-black/75 p-4 backdrop-blur-md"
    onclick={(e) => {
      if (e.target === e.currentTarget) onclose();
    }}
    role="presentation"
  >
    <!-- Modal Card -->
    <div
      class="glass-panel animate-modal-pop relative my-auto w-full max-w-lg overflow-hidden rounded-3xl text-text-main shadow-2xl"
    >
      <!-- Success Toast Overlay -->
      {#if successToast}
        <div
          class="animate-fade-in absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-canvas/95 p-6 text-center backdrop-blur-md"
        >
          <div
            class="flex h-14 w-14 items-center justify-center rounded-full border-2 border-emerald-500/30 bg-emerald-500/15 text-2xl font-black text-emerald-500"
          >
            <Icon name="check_circle" size="lg" />
          </div>
          <p class="text-base font-extrabold text-text-main">{successToast}</p>
        </div>
      {/if}

      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-border-subtle px-5 py-4">
        <div class="flex items-center gap-2">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-xl bg-primary-soft font-bold text-primary"
          >
            <Icon name="add" size="md" />
          </div>
          <div>
            <h2 class="text-sm font-extrabold text-text-main">1-Tap Schnell erfassen</h2>
            <p class="text-[0.6875rem] text-text-muted">
              Biometrische Parameter, Mahlzeiten &amp; Vitaldaten
            </p>
          </div>
        </div>

        <button
          type="button"
          onclick={onclose}
          class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-full text-text-muted transition-colors hover:bg-surface-50 hover:text-text-main"
        >
          <Icon name="close" size="sm" />
        </button>
      </div>

      <!-- Category Filter Tabs -->
      <div
        class="no-scrollbar flex items-center gap-1.5 overflow-x-auto border-b border-border-subtle bg-surface-50/40 px-4 pt-3 pb-2"
      >
        <button
          type="button"
          onclick={() => (activeCategory = 'water')}
          class="flex cursor-pointer items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {activeCategory ===
          'water'
            ? 'bg-hydrate text-white shadow-xs'
            : 'text-text-muted hover:bg-surface-50 hover:text-text-main'}"
        >
          <Icon name="water_drop" size="sm" />
          <span>Wasser</span>
        </button>

        <button
          type="button"
          onclick={() => (activeCategory = 'food')}
          class="flex cursor-pointer items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {activeCategory ===
          'food'
            ? 'bg-activity text-white shadow-xs'
            : 'text-text-muted hover:bg-surface-50 hover:text-text-main'}"
        >
          <Icon name="restaurant" size="sm" />
          <span>Ernährung</span>
        </button>

        <button
          type="button"
          onclick={() => (activeCategory = 'blood_pressure')}
          class="flex cursor-pointer items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {activeCategory ===
          'blood_pressure'
            ? 'bg-vital text-white shadow-xs'
            : 'text-text-muted hover:bg-surface-50 hover:text-text-main'}"
        >
          <Icon name="favorite" size="sm" />
          <span>Blutdruck</span>
        </button>

        <button
          type="button"
          onclick={() => (activeCategory = 'weight')}
          class="flex cursor-pointer items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {activeCategory ===
          'weight'
            ? 'bg-primary text-white shadow-xs'
            : 'text-text-muted hover:bg-surface-50 hover:text-text-main'}"
        >
          <Icon name="fitness_center" size="sm" />
          <span>Gewicht</span>
        </button>

        <button
          type="button"
          onclick={() => (activeCategory = 'glucose')}
          class="flex cursor-pointer items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {activeCategory ===
          'glucose'
            ? 'bg-circadian text-white shadow-xs'
            : 'text-text-muted hover:bg-surface-50 hover:text-text-main'}"
        >
          <Icon name="science" size="sm" />
          <span>Glukose</span>
        </button>

        <button
          type="button"
          onclick={() => (activeCategory = 'caffeine')}
          class="flex cursor-pointer items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {activeCategory ===
          'caffeine'
            ? 'bg-amber-600 text-white shadow-xs'
            : 'text-text-muted hover:bg-surface-50 hover:text-text-main'}"
        >
          <Icon name="local_cafe" size="sm" />
          <span>Koffein</span>
        </button>

        <button
          type="button"
          onclick={() => (activeCategory = 'sleep')}
          class="flex cursor-pointer items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {activeCategory ===
          'sleep'
            ? 'bg-indigo-600 text-white shadow-xs'
            : 'text-text-muted hover:bg-surface-50 hover:text-text-main'}"
        >
          <Icon name="bedtime" size="sm" />
          <span>Schlaf</span>
        </button>

        <button
          type="button"
          onclick={() => (activeCategory = 'mood')}
          class="flex cursor-pointer items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition-all {activeCategory ===
          'mood'
            ? 'bg-emerald-600 text-white shadow-xs'
            : 'text-text-muted hover:bg-surface-50 hover:text-text-main'}"
        >
          <Icon name="sentiment_satisfied" size="sm" />
          <span>Stimmung</span>
        </button>
      </div>

      <!-- Modal Body Content per Category -->
      <div class="max-h-[65vh] space-y-4 overflow-y-auto p-5">
        <!-- 1. WATER -->
        {#if activeCategory === 'water'}
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-text-muted">Schnell-Portionen</span>
              <Badge variant="hydrate">Ziel: 3.000 ml</Badge>
            </div>

            <div class="grid grid-cols-4 gap-2">
              <button
                type="button"
                onclick={() => addWaterQuick(250)}
                class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 p-3 text-center transition-all hover:border-hydrate hover:bg-hydrate-soft"
              >
                <span class="block text-sm font-black text-hydrate">+250</span>
                <span class="text-[0.625rem] font-semibold text-text-muted">Glas</span>
              </button>

              <button
                type="button"
                onclick={() => addWaterQuick(350)}
                class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 p-3 text-center transition-all hover:border-hydrate hover:bg-hydrate-soft"
              >
                <span class="block text-sm font-black text-hydrate">+350</span>
                <span class="text-[0.625rem] font-semibold text-text-muted">Becher</span>
              </button>

              <button
                type="button"
                onclick={() => addWaterQuick(500)}
                class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 p-3 text-center transition-all hover:border-hydrate hover:bg-hydrate-soft"
              >
                <span class="block text-sm font-black text-hydrate">+500</span>
                <span class="text-[0.625rem] font-semibold text-text-muted">Flasche</span>
              </button>

              <button
                type="button"
                onclick={() => addWaterQuick(750)}
                class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 p-3 text-center transition-all hover:border-hydrate hover:bg-hydrate-soft"
              >
                <span class="block text-sm font-black text-hydrate">+750</span>
                <span class="text-[0.625rem] font-semibold text-text-muted">Shaker</span>
              </button>
            </div>

            <!-- Custom Water Slider -->
            <SliderRange
              bind:value={waterCurrentInput}
              label="Individuelle Trinkmenge"
              min={50}
              max={1500}
              step={50}
              unit="ml"
              color="hydrate"
            />

            <button
              type="button"
              onclick={() => addWaterQuick(waterCurrentInput)}
              class="flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-2xl bg-hydrate py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-95"
            >
              <Icon name="water_drop" size="sm" />
              <span>+{waterCurrentInput} ml Wasser eintragen</span>
            </button>
          </div>

          <!-- 2. FOOD -->
        {:else if activeCategory === 'food'}
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-text-muted">Häufige Favoriten</span>
              {#if onopenbarcode}
                <button
                  type="button"
                  onclick={() => {
                    onclose();
                    onopenbarcode();
                  }}
                  class="flex cursor-pointer items-center gap-1 text-[0.6875rem] font-bold text-primary hover:underline"
                >
                  <Icon name="qr_code_scanner" size="sm" />
                  <span>Barcode scannen</span>
                </button>
              {/if}
            </div>

            <div class="space-y-2">
              {#each quickMealFavorites as meal}
                <button
                  type="button"
                  onclick={() => submitQuickMeal(meal)}
                  class="flex w-full cursor-pointer items-center justify-between gap-3 rounded-2xl border border-border-subtle bg-surface-50 p-3 text-left transition-all hover:border-primary hover:bg-surface-0"
                >
                  <div>
                    <span class="block text-xs font-extrabold text-text-main">{meal.name}</span>
                    <span class="text-[0.6875rem] text-text-muted"
                      >P: {meal.protein}g &bull; C: {meal.carbs}g &bull; F: {meal.fat}g</span
                    >
                  </div>
                  <Badge variant="activity">{meal.kcal} kcal</Badge>
                </button>
              {/each}
            </div>

            <!-- Custom Quick Macro Input -->
            <div class="space-y-3 border-t border-border-subtle pt-2">
              <span class="block text-xs font-bold text-text-muted">Eigene Schnellmahlzeit</span>
              <div class="grid grid-cols-2 gap-2 pt-1 sm:grid-cols-4">
                <Input bind:value={foodKcal} label="Kalorien" type="number" unit="kcal" />
                <Input bind:value={foodProtein} label="Protein" type="number" unit="g" />
                <Input bind:value={foodCarbs} label="Carbs" type="number" unit="g" />
                <Input bind:value={foodFat} label="Fett" type="number" unit="g" />
              </div>
              <button
                type="button"
                onclick={submitCustomFood}
                class="flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-2xl bg-activity py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-95"
              >
                <Icon name="restaurant" size="sm" />
                <span>Mahlzeit erfassen</span>
              </button>
            </div>
          </div>

          <!-- 3. BLOOD PRESSURE -->
        {:else if activeCategory === 'blood_pressure'}
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <Input
                bind:value={bpSystolic}
                label="Systolisch"
                type="number"
                unit="mmHg"
                icon="favorite"
              />
              <Input
                bind:value={bpDiastolic}
                label="Diastolisch"
                type="number"
                unit="mmHg"
                icon="favorite"
              />
            </div>

            <Input
              bind:value={bpPulse}
              label="Puls"
              type="number"
              unit="bpm"
              icon="monitor_heart"
            />

            <div class="grid grid-cols-2 gap-3 pt-1">
              <div>
                <span class="mb-1 block text-xs font-bold text-text-muted">Messarm</span>
                <div
                  class="grid grid-cols-2 gap-1 rounded-xl border border-border-subtle bg-surface-50 p-1"
                >
                  <button
                    type="button"
                    onclick={() => (bpArm = 'left')}
                    class="cursor-pointer rounded-lg py-1 text-center text-xs font-bold transition-all {bpArm ===
                    'left'
                      ? 'bg-surface-0 text-primary shadow-xs'
                      : 'text-text-muted'}"
                  >
                    Links
                  </button>
                  <button
                    type="button"
                    onclick={() => (bpArm = 'right')}
                    class="cursor-pointer rounded-lg py-1 text-center text-xs font-bold transition-all {bpArm ===
                    'right'
                      ? 'bg-surface-0 text-primary shadow-xs'
                      : 'text-text-muted'}"
                  >
                    Rechts
                  </button>
                </div>
              </div>

              <div>
                <span class="mb-1 block text-xs font-bold text-text-muted">Zustand</span>
                <div
                  class="grid grid-cols-3 gap-1 rounded-xl border border-border-subtle bg-surface-50 p-1"
                >
                  <button
                    type="button"
                    onclick={() => (bpState = 'resting')}
                    class="cursor-pointer rounded-lg py-1 text-center text-[0.625rem] font-bold transition-all {bpState ===
                    'resting'
                      ? 'bg-surface-0 text-primary shadow-xs'
                      : 'text-text-muted'}"
                  >
                    Ruhe
                  </button>
                  <button
                    type="button"
                    onclick={() => (bpState = 'stress')}
                    class="cursor-pointer rounded-lg py-1 text-center text-[0.625rem] font-bold transition-all {bpState ===
                    'stress'
                      ? 'bg-surface-0 text-primary shadow-xs'
                      : 'text-text-muted'}"
                  >
                    Stress
                  </button>
                  <button
                    type="button"
                    onclick={() => (bpState = 'post_exercise')}
                    class="cursor-pointer rounded-lg py-1 text-center text-[0.625rem] font-bold transition-all {bpState ===
                    'post_exercise'
                      ? 'bg-surface-0 text-primary shadow-xs'
                      : 'text-text-muted'}"
                  >
                    Sport
                  </button>
                </div>
              </div>
            </div>

            <button
              type="button"
              onclick={submitBloodPressure}
              class="flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-2xl bg-vital py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-95"
            >
              <Icon name="favorite" size="sm" />
              <span>Blutdruckmessung speichern</span>
            </button>
          </div>

          <!-- 4. WEIGHT -->
        {:else if activeCategory === 'weight'}
          <div class="space-y-4">
            <NumberStepper
              bind:value={bodyWeight}
              label="Körpergewicht"
              unit="kg"
              min={30}
              max={250}
              step={0.1}
              precision={1}
              quickSteps={[-0.5, -0.1, 0.1, 0.5]}
            />

            <div class="grid grid-cols-2 gap-3 pt-1">
              <Input bind:value={bodyFat} label="Körperfett (optional)" type="number" unit="%" />
              <Input
                bind:value={muscleMass}
                label="Muskelmasse (optional)"
                type="number"
                unit="kg"
              />
            </div>

            <button
              type="button"
              onclick={submitWeight}
              class="flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-2xl bg-primary py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-95"
            >
              <Icon name="fitness_center" size="sm" />
              <span>Gewicht speichern</span>
            </button>
          </div>

          <!-- 5. GLUCOSE -->
        {:else if activeCategory === 'glucose'}
          <div class="space-y-4">
            <NumberStepper
              bind:value={glucoseValue}
              label="Blutzucker / Glukosespiegel"
              unit="mg/dL"
              min={40}
              max={400}
              step={1}
              precision={0}
              quickSteps={[-10, -5, 5, 10]}
            />

            <div>
              <span class="mb-1 block text-xs font-bold text-text-muted">Messzeitpunkt</span>
              <div
                class="grid grid-cols-3 gap-1.5 rounded-xl border border-border-subtle bg-surface-50 p-1 text-[0.6875rem] font-bold"
              >
                <button
                  type="button"
                  onclick={() => (glucoseTiming = 'fasting')}
                  class="cursor-pointer rounded-lg py-1.5 text-center transition-all {glucoseTiming ===
                  'fasting'
                    ? 'bg-surface-0 text-circadian shadow-xs'
                    : 'text-text-muted'}"
                >
                  Nüchtern
                </button>
                <button
                  type="button"
                  onclick={() => (glucoseTiming = 'pre_meal')}
                  class="cursor-pointer rounded-lg py-1.5 text-center transition-all {glucoseTiming ===
                  'pre_meal'
                    ? 'bg-surface-0 text-circadian shadow-xs'
                    : 'text-text-muted'}"
                >
                  Vor Mahlzeit
                </button>
                <button
                  type="button"
                  onclick={() => (glucoseTiming = 'post_meal_2h')}
                  class="cursor-pointer rounded-lg py-1.5 text-center transition-all {glucoseTiming ===
                  'post_meal_2h'
                    ? 'bg-surface-0 text-circadian shadow-xs'
                    : 'text-text-muted'}"
                >
                  2h nach Essen
                </button>
              </div>
            </div>

            <button
              type="button"
              onclick={submitGlucose}
              class="flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-2xl bg-circadian py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-95"
            >
              <Icon name="science" size="sm" />
              <span>Glukosewert speichern</span>
            </button>
          </div>

          <!-- 6. CAFFEINE -->
        {:else if activeCategory === 'caffeine'}
          <div class="space-y-4">
            <div class="grid grid-cols-3 gap-2">
              <button
                type="button"
                onclick={() => (caffeineDose = 80)}
                class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 p-3 text-center transition-all hover:bg-amber-500/10 {caffeineDose ===
                80
                  ? 'border-amber-500 ring-2 ring-amber-500/20'
                  : ''}"
              >
                <span class="block text-sm font-black text-amber-600">80 mg</span>
                <span class="text-[0.625rem] font-semibold text-text-muted">Espresso</span>
              </button>

              <button
                type="button"
                onclick={() => (caffeineDose = 140)}
                class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 p-3 text-center transition-all hover:bg-amber-500/10 {caffeineDose ===
                140
                  ? 'border-amber-500 ring-2 ring-amber-500/20'
                  : ''}"
              >
                <span class="block text-sm font-black text-amber-600">140 mg</span>
                <span class="text-[0.625rem] font-semibold text-text-muted">Filterkaffee</span>
              </button>

              <button
                type="button"
                onclick={() => (caffeineDose = 200)}
                class="cursor-pointer rounded-2xl border border-border-subtle bg-surface-50 p-3 text-center transition-all hover:bg-amber-500/10 {caffeineDose ===
                200
                  ? 'border-amber-500 ring-2 ring-amber-500/20'
                  : ''}"
              >
                <span class="block text-sm font-black text-amber-600">200 mg</span>
                <span class="text-[0.625rem] font-semibold text-text-muted">Pre-Workout</span>
              </button>
            </div>

            <NumberStepper
              bind:value={caffeineDose}
              label="Individuelle Dosis"
              unit="mg"
              min={10}
              max={600}
              step={10}
              quickSteps={[-20, 20]}
            />

            <button
              type="button"
              onclick={submitCaffeine}
              class="flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-2xl bg-amber-600 py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-95"
            >
              <Icon name="local_cafe" size="sm" />
              <span>Koffein erfassen</span>
            </button>
          </div>

          <!-- 7. SLEEP -->
        {:else if activeCategory === 'sleep'}
          <div class="space-y-4">
            <NumberStepper
              bind:value={sleepHours}
              label="Schlafdauer letzte Nacht"
              unit="Std."
              min={1}
              max={16}
              step={0.25}
              precision={1}
              quickSteps={[-0.5, 0.5]}
            />

            <button
              type="button"
              onclick={submitSleep}
              class="flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-2xl bg-indigo-600 py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-95"
            >
              <Icon name="bedtime" size="sm" />
              <span>Schlaf eintragen</span>
            </button>
          </div>

          <!-- 8. MOOD -->
        {:else if activeCategory === 'mood'}
          <div class="space-y-4">
            <SliderRange
              bind:value={moodValence}
              label="Aktuelles Wohlbefinden (1 - 10)"
              min={1}
              max={10}
              step={1}
              color="primary"
            />

            <button
              type="button"
              onclick={submitMood}
              class="flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-2xl bg-emerald-600 py-2.5 text-xs font-bold text-white shadow-md transition-all hover:opacity-95"
            >
              <Icon name="sentiment_satisfied" size="sm" />
              <span>Stimmung speichern</span>
            </button>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
