<script lang="ts">
  import EmptyState from '$components/ui/EmptyState.svelte';
  import MealCard from './MealCard.svelte';
  import type { FoodItem, Meal, MealItem } from '$lib/db/types';

  interface Props {
    meals: Meal[];
    mealItemsMap: Record<string, MealItem[]>;
    foodMap: Record<string, FoodItem>;
    macroTotals: Record<string, { calories: number; protein: number; carbs: number; fat: number }>;
    onEdit: (mealId: string) => void;
    onDelete: (mealId: string) => void;
    onCreate: () => void;
  }

  let { meals, mealItemsMap, foodMap, macroTotals, onEdit, onDelete, onCreate }: Props = $props();
</script>

{#if meals.length === 0}
  <EmptyState icon="restaurant" title="No meals logged" description="Log your first meal to start tracking nutrition.">
    <button onclick={onCreate} class="btn btn-primary mt-4">Log Meal</button>
  </EmptyState>
{:else}
  <div class="flex flex-col gap-3">
    {#each meals as meal (meal.id)}
      {@const items = mealItemsMap[meal.id ?? ''] ?? []}
      {@const macros = macroTotals[meal.id ?? ''] ?? { calories: 0, protein: 0, carbs: 0, fat: 0 }}
      <MealCard
        mealType={meal.meal_type}
        name={meal.name}
        {items}
        {foodMap}
        totalCalories={macros.calories}
        totalProtein={macros.protein}
        totalCarbs={macros.carbs}
        totalFat={macros.fat}
        onEdit={() => onEdit(meal.id ?? '')}
        onDelete={() => onDelete(meal.id ?? '')}
      />
    {/each}
  </div>
{/if}
