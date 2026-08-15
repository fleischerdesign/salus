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
    onDelete?: () => void;
    onUpdateItems?: (items: MealItem[]) => void;
    onViewFood?: (food: FoodItem) => void;
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
    onDelete,
    onUpdateItems,
    onViewFood
  }: Props = $props();

  let expanded = $state(false);
  let editItems = $state<MealItem[]>([]);

  $effect(() => {
    if (expanded) editItems = items;
  });

  const displayName = $derived(name ? name.replace(/^Recipe: /, '') : 'Meal');
  const isRecipe = $derived(name?.startsWith('Recipe: ') ?? false);
  const typeIcon = $derived(
    isRecipe
      ? 'menu-book'
      : ({ breakfast: 'wb-sunny', lunch: 'lunch-dining', dinner: 'dinner-dining', snack: 'cookie' }[
          mealType
        ] ?? 'restaurant')
  );

  function persist(next: MealItem[]) {
    editItems = next;
    onUpdateItems?.(next);
  }

  function incrementItem(mi: MealItem) {
    persist(
      editItems.map((x) =>
        x.id === mi.id ? { ...x, servings: Math.round((x.servings + 0.5) * 2) / 2 } : x
      )
    );
  }

  function decrementItem(mi: MealItem) {
    persist(
      editItems.map((x) =>
        x.id === mi.id
          ? { ...x, servings: Math.max(0.25, Math.round((x.servings - 0.5) * 2) / 2) }
          : x
      )
    );
  }

  function removeItem(mi: MealItem) {
    persist(editItems.filter((x) => x.id !== mi.id));
  }
</script>

<Card padding={false}>
  <div
    class="flex w-full cursor-pointer items-center justify-between px-4 py-3 hover:bg-surface-50"
    onclick={() => (expanded = !expanded)}
    onkeydown={(e) => {
      if (e.key === 'Enter') expanded = !expanded;
    }}
    role="button"
    tabindex="0"
  >
    <div class="flex min-w-0 items-center gap-3">
      <div
        class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-surface-100 text-surface-500"
      >
        <Icon name={typeIcon} size="md" />
      </div>
      <div class="min-w-0">
        <div class="truncate text-sm font-semibold text-surface-800">{displayName}</div>
        <div class="text-xs text-surface-400">
          {Math.round(totalCalories)} kcal · {Math.round(totalProtein)}P · {Math.round(totalCarbs)}C
          · {Math.round(totalFat)}F
        </div>
      </div>
    </div>
    <div class="ml-3 flex flex-shrink-0 items-center gap-1">
      <button
        onclick={(e) => {
          e.stopPropagation();
          onEdit();
        }}
        class="rounded p-1 text-surface-400 hover:bg-surface-100 hover:text-surface-600"
        aria-label="Edit meal"
      >
        <Icon name="edit" size="sm" />
      </button>
      {#if onDelete}
        <button
          onclick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          class="rounded p-1 text-surface-400 hover:bg-surface-100 hover:text-error-500"
          aria-label="Delete meal"
        >
          <Icon name="delete" size="sm" />
        </button>
      {/if}
      <Icon
        name={expanded ? 'keyboard-arrow-up' : 'expand-more'}
        size="sm"
        class="text-surface-400"
      />
    </div>
  </div>

  {#if expanded}
    <div class="border-t border-surface-100 px-4 py-3">
      <div class="flex flex-col gap-2">
        {#each editItems as item (item.id)}
          {@const food = foodMap[item.food_item_id]}
          <MealItemRow
            name={food?.name ?? 'Unknown'}
            servings={item.servings}
            servingSize={food?.serving_size ?? 1}
            servingUnit={food?.serving_unit ?? 'g'}
            calories={food ? food.calories_per_serving * item.servings : 0}
            proteinG={food ? food.protein_g * item.servings : 0}
            carbsG={food ? food.carbs_g * item.servings : 0}
            fatG={food ? food.fat_g * item.servings : 0}
            onViewFood={food && onViewFood ? () => onViewFood(food) : undefined}
            onRemove={() => removeItem(item)}
            onIncrement={() => incrementItem(item)}
            onDecrement={() => decrementItem(item)}
          />
        {:else}
          <p class="text-xs text-surface-400 py-2 text-center">No items</p>
        {/each}
      </div>
    </div>
  {/if}
</Card>
