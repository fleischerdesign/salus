<script lang="ts">
  import Card from '$components/ui/Card.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import MealItemRow from './MealItemRow.svelte';
  import type { FoodItem, MealItem } from '$lib/db/types';

  interface Props {
    mealType: string;
    name: string | null;
    items: MealItem[];
    foodMap: Record<string, FoodItem>;
    totalCalories: number;
    totalProtein: number;
    totalCarbs: number;
    totalFat: number;
    onEdit: () => void;
  }

  let {
    mealType,
    name,
    items,
    foodMap,
    totalCalories,
    totalProtein,
    totalCarbs,
    totalFat,
    onEdit,
  }: Props = $props();

  let expanded = $state(false);

  const mealTypeLabel = $derived(
    mealType.charAt(0).toUpperCase() + mealType.slice(1)
  );
</script>

<Card padding={false}>
  <div
    class="flex w-full items-center justify-between px-4 py-3 hover:bg-surface-50 cursor-pointer"
    onclick={() => (expanded = !expanded)}
    onkeydown={(e) => { if (e.key === 'Enter') expanded = !expanded; }}
    role="button"
    tabindex="0"
  >
    <div class="flex items-center gap-3 min-w-0">
      <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-surface-100 text-surface-500">
        <Icon name="restaurant" size="md" />
      </div>
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <span class="text-xs font-medium text-surface-400 uppercase">{mealTypeLabel}</span>
          {#if name}
            <span class="text-sm font-medium text-surface-700 truncate">{name}</span>
          {/if}
        </div>
        <div class="text-xs text-surface-400">
          {Math.round(totalCalories)} kcal · {Math.round(totalProtein)}P · {Math.round(totalCarbs)}C · {Math.round(totalFat)}F
        </div>
      </div>
    </div>
    <div class="flex items-center gap-1 flex-shrink-0 ml-3">
      <button onclick={(e) => { e.stopPropagation(); onEdit(); }} class="rounded p-1 text-surface-400 hover:bg-surface-100 hover:text-surface-600">
        <Icon name="edit" size="sm" />
      </button>
      <Icon name={expanded ? 'keyboard-arrow-up' : 'expand-more'} size="sm" class="text-surface-400" />
    </div>
  </div>

  {#if expanded}
    <div class="border-t border-surface-100 px-4 py-3">
      <div class="flex flex-col gap-2">
        {#each items as item (item.id)}
          {@const food = foodMap[item.food_item_id]}
          <MealItemRow
            name={food?.name ?? 'Unknown'}
            servings={item.servings}
            amountG={item.amount_g}
            calories={food ? food.calories_per_serving * item.servings : 0}
            proteinG={food ? food.protein_g * item.servings : 0}
            carbsG={food ? food.carbs_g * item.servings : 0}
            fatG={food ? food.fat_g * item.servings : 0}
            onRemove={() => {}}
            onIncrement={() => {}}
            onDecrement={() => {}}
          />
        {:else}
          <p class="text-xs text-surface-400 py-2 text-center">No items</p>
        {/each}
      </div>
    </div>
  {/if}
</Card>
