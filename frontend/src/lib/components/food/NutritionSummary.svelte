<script lang="ts">
  import Card from '$components/ui/Card.svelte';
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    totalCalories: number;
    totalProtein: number;
    totalCarbs: number;
    totalFat: number;
    mealCount: number;
  }

  let { totalCalories, totalProtein, totalCarbs, totalFat, mealCount }: Props = $props();

  const proteinCals = $derived(totalProtein * 4);
  const carbsCals = $derived(totalCarbs * 4);
  const fatCals = $derived(totalFat * 9);
  const totalMacroCals = $derived(proteinCals + carbsCals + fatCals);
</script>

<Card>
  <div class="flex items-center gap-3 mb-4">
    <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-600">
      <Icon name="whatshot" size="lg" />
    </div>
    <div>
      <div class="text-lg font-bold text-surface-900">{Math.round(totalCalories).toLocaleString()} kcal</div>
      <div class="text-xs text-surface-400">{mealCount} meal{mealCount !== 1 ? 's' : ''} logged</div>
    </div>
  </div>

  <div class="flex flex-col gap-2">
    <div class="flex items-center gap-2">
      <span class="w-8 text-xs font-medium text-surface-500">P</span>
      <div class="h-2 flex-1 rounded-full bg-surface-100 overflow-hidden">
        <div class="h-full rounded-full bg-blue-500" style="width: {totalMacroCals > 0 ? Math.min((proteinCals / totalMacroCals) * 100, 100) : 0}%"></div>
      </div>
      <span class="w-16 text-right text-xs font-medium text-surface-600">{Math.round(totalProtein)}g</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-8 text-xs font-medium text-surface-500">C</span>
      <div class="h-2 flex-1 rounded-full bg-surface-100 overflow-hidden">
        <div class="h-full rounded-full bg-amber-500" style="width: {totalMacroCals > 0 ? Math.min((carbsCals / totalMacroCals) * 100, 100) : 0}%"></div>
      </div>
      <span class="w-16 text-right text-xs font-medium text-surface-600">{Math.round(totalCarbs)}g</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-8 text-xs font-medium text-surface-500">F</span>
      <div class="h-2 flex-1 rounded-full bg-surface-100 overflow-hidden">
        <div class="h-full rounded-full bg-red-400" style="width: {totalMacroCals > 0 ? Math.min((fatCals / totalMacroCals) * 100, 100) : 0}%"></div>
      </div>
      <span class="w-16 text-right text-xs font-medium text-surface-600">{Math.round(totalFat)}g</span>
    </div>
  </div>
</Card>
