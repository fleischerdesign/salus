<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import Input from '$components/ui/Input.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import MealItemRow from './MealItemRow.svelte';
  import type { FoodItem } from '$lib/db/types';

  interface FoodSelection {
    foodItemId: string;
    servings: number;
    name: string;
    calories: number;
    proteinG: number;
    carbsG: number;
    fatG: number;
  }

  interface Props {
    open: boolean;
    foodItems: FoodItem[];
    onSave: (data: {
      meal_type: string;
      name: string;
      notes: string;
      items: { food_item_id: string; servings: number }[];
    }) => void;
    onClose: () => void;
    saving?: boolean;
  }

  let { open, foodItems, onSave, onClose, saving = false }: Props = $props();

  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack', 'other'];

  let mealType = $state('snack');
  let name = $state('');
  let notes = $state('');
  let search = $state('');
  let selections = $state<FoodSelection[]>([]);

  function reset() {
    mealType = 'snack';
    name = '';
    notes = '';
    search = '';
    selections = [];
  }

  $effect(() => {
    if (!open) reset();
  });

  const filteredItems = $derived(
    search.trim()
      ? foodItems.filter(
          (f) =>
            f.name.toLowerCase().includes(search.toLowerCase()) &&
            !f.deleted_at
        )
      : []
  );

  const showSearch = $derived(search.trim().length > 0);

  const totalCalories = $derived(
    selections.reduce((sum, s) => sum + s.calories * s.servings, 0)
  );

  function addItem(food: FoodItem) {
    const existing = selections.find((s) => s.foodItemId === food.id);
    if (existing) {
      existing.servings += 1;
      selections = [...selections];
    } else {
      selections = [
        ...selections,
        {
          foodItemId: food.id ?? '',
          servings: 1,
          name: food.name,
          calories: food.calories_per_serving,
          proteinG: food.protein_g,
          carbsG: food.carbs_g,
          fatG: food.fat_g
        }
      ];
    }
    search = '';
  }

  function incrementItem(foodItemId: string) {
    const s = selections.find((s) => s.foodItemId === foodItemId);
    if (s) {
      s.servings = Math.round((s.servings + 0.5) * 2) / 2;
      selections = [...selections];
    }
  }

  function decrementItem(foodItemId: string) {
    const s = selections.find((s) => s.foodItemId === foodItemId);
    if (s) {
      s.servings = Math.max(0.25, Math.round((s.servings - 0.5) * 2) / 2);
      selections = [...selections];
    }
  }

  function removeItem(foodItemId: string) {
    selections = selections.filter((s) => s.foodItemId !== foodItemId);
  }

  const canSave = $derived(selections.length > 0);

  function handleSubmit() {
    if (!canSave) return;
    onSave({
      meal_type: mealType,
      name: name.trim() || '',
      notes: notes.trim() || '',
      items: selections.map((s) => ({
        food_item_id: s.foodItemId,
        servings: s.servings
      }))
    });
  }
</script>

<Modal open={open} onclose={onClose} title="Log Meal" size="md">
  <div class="flex flex-col gap-4">
    <div class="grid grid-cols-5 gap-2">
      {#each mealTypes as mt}
        <button
          type="button"
          onclick={() => (mealType = mt)}
          class="rounded-lg border px-2 py-2 text-xs font-medium transition-colors text-center"
          class:border-primary-500={mealType === mt}
          class:bg-primary-50={mealType === mt}
          class:text-primary-700={mealType === mt}
          class:border-surface-200={mealType !== mt}
          class:text-surface-600={mealType !== mt}
        >
          {mt.charAt(0).toUpperCase() + mt.slice(1)}
        </button>
      {/each}
    </div>

    <FormField label="Name (optional)">
      <Input name="meal_name" placeholder="e.g. Porridge with banana" bind:value={name} />
    </FormField>

    <FormField label="Add Food Items">
      <Input
        name="food_search"
        placeholder="Search food database..."
        bind:value={search}
      />
    </FormField>

    {#if showSearch && filteredItems.length > 0}
      <div class="max-h-40 overflow-y-auto rounded-lg border border-surface-200">
        {#each filteredItems.slice(0, 10) as food (food.id)}
          <button
            onclick={() => addItem(food)}
            class="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-surface-50 border-b border-surface-100 last:border-b-0"
          >
            <div>
              <div class="text-sm font-medium text-surface-700">{food.name}</div>
              <div class="text-xs text-surface-400">
                {food.calories_per_serving} kcal · {food.protein_g}P · {food.carbs_g}C · {food.fat_g}F
              </div>
            </div>
            <Icon name="add-circle" size="sm" class="text-primary-500" />
          </button>
        {/each}
      </div>
    {:else if showSearch}
      <p class="text-sm text-surface-400 text-center py-2">No items found. Create one in the Food Database.</p>
    {/if}

    {#if selections.length > 0}
      <div class="rounded-lg border border-surface-200 p-3">
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-xs font-semibold uppercase tracking-wider text-surface-400">Items</h4>
          <span class="text-xs font-medium text-surface-600">{Math.round(totalCalories)} kcal</span>
        </div>
        <div class="flex flex-col gap-2">
          {#each selections as sel (sel.foodItemId)}
            <MealItemRow
              name={sel.name}
              servings={sel.servings}
              amountG={null}
              calories={sel.calories}
              proteinG={sel.proteinG}
              carbsG={sel.carbsG}
              fatG={sel.fatG}
              onRemove={() => removeItem(sel.foodItemId)}
              onIncrement={() => incrementItem(sel.foodItemId)}
              onDecrement={() => decrementItem(sel.foodItemId)}
            />
          {/each}
        </div>
      </div>
    {/if}

    <FormField label="Notes (optional)">
      <Input name="notes" placeholder="Optional notes..." bind:value={notes} />
    </FormField>

    <div class="flex justify-end gap-3 pt-2">
      <Btn variant="ghost" onclick={onClose}>Cancel</Btn>
      <Btn variant="primary" onclick={handleSubmit} disabled={!canSave || saving}>
        {saving ? 'Saving...' : 'Log Meal'}
      </Btn>
    </div>
  </div>
</Modal>
