<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let {
    calories = { current: 1840, target: 2400 },
    protein = { current: 142, target: 180 },
    carbs = { current: 185, target: 220 },
    fat = { current: 52, target: 70 },
    fiber = { current: 32, target: 38 }
  } = $props<{
    calories?: { current: number; target: number };
    protein?: { current: number; target: number };
    carbs?: { current: number; target: number };
    fat?: { current: number; target: number };
    fiber?: { current: number; target: number };
  }>();

  let remainingKcal = $derived(Math.max(0, calories.target - calories.current));
  let caloriePercent = $derived(
    Math.min(100, Math.round((calories.current / calories.target) * 100))
  );

  let circumference = 2 * Math.PI * 62;
  let strokeDashoffset = $derived(circumference - (caloriePercent / 100) * circumference);
</script>

<div class="space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-xs">
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div>
      <div class="flex items-center gap-1.5 text-sm font-extrabold text-text-main">
        <Icon name="restaurant" class="text-activity" />
        <span>Nährwert- und Makro-Budget</span>
      </div>
      <p class="mt-0.5 text-xs text-text-muted">
        Tagesziel: 2.400 kcal (Erhaltung) &bull; 2.2g Protein / kg Körpergewicht
      </p>
    </div>
    <Badge variant="activity" class="font-bold tabular-nums">{caloriePercent}% erreicht</Badge>
  </div>

  <div
    class="grid grid-cols-1 items-center gap-5 rounded-2xl border border-border-subtle bg-surface-50 p-4 md:grid-cols-12"
  >
    <!-- Donut Hero -->
    <div class="relative mx-auto flex h-44 w-44 items-center justify-center md:col-span-5">
      <svg class="h-full w-full -rotate-90" viewBox="0 0 160 160">
        <!-- Background Track -->
        <circle
          cx="80"
          cy="80"
          r="62"
          fill="none"
          stroke="var(--bg-surface-100)"
          stroke-width="12"
        />
        <!-- Calorie Arc -->
        <circle
          cx="80"
          cy="80"
          r="62"
          fill="none"
          stroke="var(--color-activity)"
          stroke-width="12"
          stroke-linecap="round"
          stroke-dasharray={circumference}
          stroke-dashoffset={strokeDashoffset}
          class="transition-all duration-700 ease-out"
        />
      </svg>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span class="text-3xl font-extrabold text-text-main tabular-nums">{calories.current}</span>
        <span class="text-[0.625rem] font-bold text-text-muted uppercase">kcal gegessen</span>
        <span class="mt-0.5 text-xs font-bold text-activity tabular-nums"
          >Noch {remainingKcal} kcal</span
        >
      </div>
    </div>

    <!-- Macro Bars Breakdown -->
    <div class="space-y-3 md:col-span-7">
      <!-- Protein -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs">
          <span class="flex items-center gap-1 font-bold text-emerald-500">Protein (2.2g/kg)</span>
          <span class="font-bold text-text-main tabular-nums"
            >{protein.current}g / {protein.target}g ({Math.round(
              (protein.current / protein.target) * 100
            )}%)</span
          >
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-surface-100">
          <div
            class="h-full rounded-full bg-emerald-500 transition-all duration-500"
            style="width: {Math.min(100, (protein.current / protein.target) * 100)}%"
          ></div>
        </div>
      </div>

      <!-- Carbs -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs">
          <span class="flex items-center gap-1 font-bold text-amber-500">Kohlenhydrate</span>
          <span class="font-bold text-text-main tabular-nums"
            >{carbs.current}g / {carbs.target}g ({Math.round(
              (carbs.current / carbs.target) * 100
            )}%)</span
          >
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-surface-100">
          <div
            class="h-full rounded-full bg-amber-500 transition-all duration-500"
            style="width: {Math.min(100, (carbs.current / carbs.target) * 100)}%"
          ></div>
        </div>
      </div>

      <!-- Fat -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs">
          <span class="flex items-center gap-1 font-bold text-purple-500">Fette</span>
          <span class="font-bold text-text-main tabular-nums"
            >{fat.current}g / {fat.target}g ({Math.round((fat.current / fat.target) * 100)}%)</span
          >
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-surface-100">
          <div
            class="h-full rounded-full bg-purple-500 transition-all duration-500"
            style="width: {Math.min(100, (fat.current / fat.target) * 100)}%"
          ></div>
        </div>
      </div>

      <!-- Fiber -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs">
          <span class="flex items-center gap-1 font-bold text-teal-400">Ballaststoffe</span>
          <span class="font-bold text-text-main tabular-nums"
            >{fiber.current}g / {fiber.target}g ({Math.round(
              (fiber.current / fiber.target) * 100
            )}%)</span
          >
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-surface-100">
          <div
            class="h-full rounded-full bg-teal-400 transition-all duration-500"
            style="width: {Math.min(100, (fiber.current / fiber.target) * 100)}%"
          ></div>
        </div>
      </div>
    </div>
  </div>
</div>
