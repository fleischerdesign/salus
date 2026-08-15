<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import MealBlock from './MealBlock.svelte';
  import MealItemRow from './MealItemRow.svelte';
  import type { FoodItem, Meal, MealItem } from '$lib/db/types';

  interface Props {
    meals: Meal[];
    mealItemsMap: Record<string, MealItem[]>;
    foodMap: Record<string, FoodItem>;
    macroTotals: Record<string, { calories: number; protein: number; carbs: number; fat: number }>;
    onEdit: (mealId: string) => void;
    onDelete: (mealId: string) => void;
    onUpdateItems: (mealId: string, items: MealItem[]) => void;
    onAdd: (mealType: string) => void;
    onViewFood?: (food: FoodItem) => void;
  }

  let {
    meals,
    mealItemsMap,
    foodMap,
    macroTotals,
    onEdit,
    onDelete,
    onUpdateItems,
    onAdd,
    onViewFood
  }: Props = $props();

  const MEAL_TYPE_META: Record<string, { label: string; icon: string; color: string }> = {
    breakfast: { label: 'Breakfast', icon: 'wb-sunny', color: 'text-warning-600 bg-warning-50' },
    lunch: { label: 'Lunch', icon: 'lunch-dining', color: 'text-primary-600 bg-primary-50' },
    dinner: { label: 'Dinner', icon: 'dinner-dining', color: 'text-violet-600 bg-violet-50' },
    snack: { label: 'Snack', icon: 'cookie', color: 'text-success-600 bg-success-50' },
    other: { label: 'Other', icon: 'restaurant', color: 'text-surface-500 bg-surface-100' }
  };

  const MEAL_TYPE_ORDER = ['breakfast', 'lunch', 'dinner', 'snack', 'other'];

  const groups = $derived.by(() => {
    const byType = new Map<string, Meal[]>();
    for (const meal of meals) {
      const t = meal.meal_type || 'other';
      if (!byType.has(t)) byType.set(t, []);
      byType.get(t)!.push(meal);
    }
    return MEAL_TYPE_ORDER.filter((t) => byType.has(t)).map((t) => ({
      type: t,
      meals: byType.get(t)!.sort((a, b) => (a.created_at ?? '').localeCompare(b.created_at ?? ''))
    }));
  });

  function groupKcal(mealIds: string[]): number {
    return mealIds.reduce((sum, id) => sum + (macroTotals[id]?.calories ?? 0), 0);
  }
</script>

<div class="space-y-5">
  {#each groups as group (group.type)}
    {@const meta = MEAL_TYPE_META[group.type] ?? MEAL_TYPE_META.other}
    <section>
      <div class="mb-2 flex items-center gap-2">
        <span class="flex h-7 w-7 items-center justify-center rounded-lg {meta.color}">
          <Icon name={meta.icon} size="sm" />
        </span>
        <h2 class="text-sm font-semibold text-surface-800">{meta.label}</h2>
        <span class="text-xs text-surface-400 tabular-nums">
          {Math.round(groupKcal(group.meals.map((m) => m.id ?? ''))).toLocaleString()} kcal
        </span>
        <button
          type="button"
          onclick={() => onAdd(group.type)}
          class="ml-auto flex items-center gap-1 rounded-full border border-surface-200 px-2.5 py-1 text-xs font-semibold text-surface-600 transition-colors hover:border-primary-300 hover:bg-primary-50 hover:text-primary-700"
          aria-label={`Add to ${meta.label}`}
        >
          <Icon name="add" size="sm" />
          Add
        </button>
      </div>

      <div class="flex flex-col gap-2">
        {#each group.meals as meal (meal.id)}
          {@const items = mealItemsMap[meal.id ?? ''] ?? []}
          {@const macros = macroTotals[meal.id ?? ''] ?? {
            calories: 0,
            protein: 0,
            carbs: 0,
            fat: 0
          }}
          {#if meal.name}
            <MealBlock
              mealType={meal.meal_type ?? 'other'}
              name={meal.name}
              {items}
              {foodMap}
              totalCalories={macros.calories}
              totalProtein={macros.protein}
              totalCarbs={macros.carbs}
              totalFat={macros.fat}
              onEdit={() => onEdit(meal.id ?? '')}
              onDelete={() => onDelete(meal.id ?? '')}
              onUpdateItems={(next) => onUpdateItems(meal.id ?? '', next)}
              {onViewFood}
            />
          {:else}
            {#each items as item (item.id)}
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
                onRemove={() =>
                  onUpdateItems(
                    meal.id ?? '',
                    items.filter((x) => x.id !== item.id)
                  )}
                onIncrement={() =>
                  onUpdateItems(
                    meal.id ?? '',
                    items.map((x) =>
                      x.id === item.id
                        ? { ...x, servings: Math.round((x.servings + 0.5) * 2) / 2 }
                        : x
                    )
                  )}
                onDecrement={() =>
                  onUpdateItems(
                    meal.id ?? '',
                    items.map((x) =>
                      x.id === item.id
                        ? { ...x, servings: Math.max(0.25, Math.round((x.servings - 0.5) * 2) / 2) }
                        : x
                    )
                  )}
              />
            {/each}
          {/if}
        {/each}
      </div>
    </section>
  {/each}
</div>
