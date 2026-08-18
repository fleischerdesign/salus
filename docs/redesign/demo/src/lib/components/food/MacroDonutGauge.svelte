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
  let caloriePercent = $derived(Math.min(100, Math.round((calories.current / calories.target) * 100)));

  let circumference = 2 * Math.PI * 62;
  let strokeDashoffset = $derived(
    circumference - (caloriePercent / 100) * circumference
  );
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-3xl p-5 shadow-xs space-y-4">
  
  <div class="flex items-center justify-between flex-wrap gap-2">
    <div>
      <div class="text-sm font-extrabold flex items-center gap-1.5 text-[var(--text-main)]">
        <Icon name="food" class="text-[var(--color-activity)]" />
        <span>Nährwert- und Makro-Budget</span>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-0.5">Tagesziel: 2.400 kcal (Erhaltung) &bull; 2.2g Protein / kg Körpergewicht</p>
    </div>
    <Badge variant="activity" class="font-bold tabular-nums">{caloriePercent}% erreicht</Badge>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-12 gap-5 items-center bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl p-4">
    
    <!-- Donut Hero -->
    <div class="md:col-span-5 relative w-44 h-44 mx-auto flex items-center justify-center">
      <svg class="w-full h-full -rotate-90" viewBox="0 0 160 160">
        <!-- Background Track -->
        <circle cx="80" cy="80" r="62" fill="none" stroke="var(--bg-surface-100)" stroke-width="12" />
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
        <span class="text-3xl font-extrabold tabular-nums text-[var(--text-main)]">{calories.current}</span>
        <span class="text-[0.625rem] font-bold text-[var(--text-muted)] uppercase">kcal gegessen</span>
        <span class="text-xs font-bold text-[var(--color-activity)] mt-0.5 tabular-nums">Noch {remainingKcal} kcal</span>
      </div>
    </div>

    <!-- Macro Bars Breakdown -->
    <div class="md:col-span-7 space-y-3">
      
      <!-- Protein -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs">
          <span class="text-emerald-500 font-bold flex items-center gap-1">Protein (2.2g/kg)</span>
          <span class="font-bold text-[var(--text-main)] tabular-nums">{protein.current}g / {protein.target}g ({Math.round((protein.current/protein.target)*100)}%)</span>
        </div>
        <div class="h-2 rounded-full bg-[var(--bg-surface-100)] overflow-hidden">
          <div class="h-full bg-emerald-500 rounded-full transition-all duration-500" style="width: {Math.min(100, (protein.current/protein.target)*100)}%"></div>
        </div>
      </div>

      <!-- Carbs -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs">
          <span class="text-amber-500 font-bold flex items-center gap-1">Kohlenhydrate</span>
          <span class="font-bold text-[var(--text-main)] tabular-nums">{carbs.current}g / {carbs.target}g ({Math.round((carbs.current/carbs.target)*100)}%)</span>
        </div>
        <div class="h-2 rounded-full bg-[var(--bg-surface-100)] overflow-hidden">
          <div class="h-full bg-amber-500 rounded-full transition-all duration-500" style="width: {Math.min(100, (carbs.current/carbs.target)*100)}%"></div>
        </div>
      </div>

      <!-- Fat -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs">
          <span class="text-purple-500 font-bold flex items-center gap-1">Fette</span>
          <span class="font-bold text-[var(--text-main)] tabular-nums">{fat.current}g / {fat.target}g ({Math.round((fat.current/fat.target)*100)}%)</span>
        </div>
        <div class="h-2 rounded-full bg-[var(--bg-surface-100)] overflow-hidden">
          <div class="h-full bg-purple-500 rounded-full transition-all duration-500" style="width: {Math.min(100, (fat.current/fat.target)*100)}%"></div>
        </div>
      </div>

      <!-- Fiber -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs">
          <span class="text-teal-400 font-bold flex items-center gap-1">Ballaststoffe</span>
          <span class="font-bold text-[var(--text-main)] tabular-nums">{fiber.current}g / {fiber.target}g ({Math.round((fiber.current/fiber.target)*100)}%)</span>
        </div>
        <div class="h-2 rounded-full bg-[var(--bg-surface-100)] overflow-hidden">
          <div class="h-full bg-teal-400 rounded-full transition-all duration-500" style="width: {Math.min(100, (fiber.current/fiber.target)*100)}%"></div>
        </div>
      </div>

    </div>
  </div>
</div>
