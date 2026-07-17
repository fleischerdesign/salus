<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import Input from '$components/ui/Input.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import type { FoodItem } from '$lib/db/types';

  interface IngredientSelection {
    foodItemId: string;
    amountG: number;
    name: string;
    calories: number;
    proteinG: number;
    carbsG: number;
    fatG: number;
    notes: string;
  }

  interface Props {
    open: boolean;
    recipe?: {
      name: string;
      description: string;
      instructions: string;
      servings: number;
      prep_time_min: number | null;
      cook_time_min: number | null;
    } | null;
    foodItems: FoodItem[];
    onSave: (data: {
      name: string;
      description: string;
      instructions: string;
      servings: number;
      prep_time_min: number | null;
      cook_time_min: number | null;
      ingredients: { food_item_id: string; amount_g: number; notes: string }[];
    }) => void;
    onClose: () => void;
    saving?: boolean;
  }

  let { open, recipe, foodItems, onSave, onClose, saving = false }: Props = $props();

  let name = $state('');
  let description = $state('');
  let instructions = $state('');
  let servings = $state(4);
  let prepTimeMin = $state<string | undefined>(undefined);
  let cookTimeMin = $state<string | undefined>(undefined);
  let search = $state('');
  let ingredients = $state<IngredientSelection[]>([]);

  function reset() {
    if (recipe) {
      name = recipe.name;
      description = recipe.description ?? '';
      instructions = recipe.instructions ?? '';
      servings = recipe.servings;
      prepTimeMin = recipe.prep_time_min?.toString() ?? undefined;
      cookTimeMin = recipe.cook_time_min?.toString() ?? undefined;
    } else {
      name = '';
      description = '';
      instructions = '';
      servings = 4;
      prepTimeMin = undefined;
      cookTimeMin = undefined;
    }
    search = '';
    ingredients = [];
  }

  $effect(() => {
    if (open) reset();
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

  function addIngredient(food: FoodItem) {
    ingredients = [
      ...ingredients,
      {
        foodItemId: food.id ?? '',
        amountG: 100,
        name: food.name,
        calories: food.calories_per_serving,
        proteinG: food.protein_g,
        carbsG: food.carbs_g,
        fatG: food.fat_g,
        notes: ''
      }
    ];
    search = '';
  }

  function updateAmount(foodItemId: string, amount: number) {
    const ing = ingredients.find((i) => i.foodItemId === foodItemId);
    if (ing) {
      ing.amountG = Math.max(1, amount);
      ingredients = [...ingredients];
    }
  }

  function removeIngredient(foodItemId: string) {
    ingredients = ingredients.filter((i) => i.foodItemId !== foodItemId);
  }

  const canSave = $derived(name.trim().length > 0 && ingredients.length > 0);

  function handleSubmit() {
    if (!canSave) return;
    onSave({
      name: name.trim(),
      description: description.trim() || '',
      instructions: instructions.trim() || '',
      servings,
      prep_time_min: prepTimeMin ? parseInt(prepTimeMin) : null,
      cook_time_min: cookTimeMin ? parseInt(cookTimeMin) : null,
      ingredients: ingredients.map((i) => ({
        food_item_id: i.foodItemId,
        amount_g: i.amountG,
        notes: i.notes || ''
      }))
    });
  }
</script>

<Modal open={open} onclose={onClose} title={recipe ? 'Edit Recipe' : 'New Recipe'} size="lg">
  <div class="flex flex-col gap-4">
    <FormField label="Name" required>
      <Input name="recipe_name" placeholder="e.g. Protein Pancakes" bind:value={name} />
    </FormField>

    <FormField label="Description">
      <Input name="description" placeholder="Short description..." bind:value={description} />
    </FormField>

    <div class="grid grid-cols-3 gap-4">
      <FormField label="Servings">
        <Input name="servings" type="number" bind:value={servings} min={1} />
      </FormField>
      <FormField label="Prep Time (min)">
        <Input name="prep_time" type="number" bind:value={prepTimeMin} min={0} placeholder="10" />
      </FormField>
      <FormField label="Cook Time (min)">
        <Input name="cook_time" type="number" bind:value={cookTimeMin} min={0} placeholder="20" />
      </FormField>
    </div>

    <FormField label="Add Ingredients">
      <Input
        name="recipe_food_search"
        placeholder="Search food items..."
        bind:value={search}
      />
    </FormField>

    {#if search.trim() && filteredItems.length > 0}
      <div class="max-h-40 overflow-y-auto rounded-lg border border-surface-200">
        {#each filteredItems.slice(0, 10) as food (food.id)}
          <button
            onclick={() => addIngredient(food)}
            class="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-surface-50 border-b border-surface-100 last:border-b-0"
          >
            <div>
              <div class="text-sm font-medium text-surface-700">{food.name}</div>
              <div class="text-xs text-surface-400">{food.calories_per_serving} kcal per {food.serving_size}{food.serving_unit}</div>
            </div>
            <Icon name="add-circle" size="sm" class="text-primary-500" />
          </button>
        {/each}
      </div>
    {/if}

    {#if ingredients.length > 0}
      <div class="rounded-lg border border-surface-200 p-3">
        <h4 class="mb-2 text-xs font-semibold uppercase tracking-wider text-surface-400">Ingredients</h4>
        <div class="flex flex-col gap-2">
          {#each ingredients as ing (ing.foodItemId)}
            <div class="flex items-center gap-3 rounded-lg bg-surface-50 px-3 py-2">
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-surface-700 truncate">{ing.name}</div>
                <div class="text-xs text-surface-400">{Math.round(ing.calories * (ing.amountG / 100))} kcal</div>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <Input name={'amount_' + ing.foodItemId} type="number" value={ing.amountG} min={1} class="!h-8 w-20 text-xs" />
                <button onclick={() => removeIngredient(ing.foodItemId)} class="flex h-7 w-7 items-center justify-center rounded text-surface-400 hover:text-error-500">
                  <Icon name="close" size="sm" />
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <FormField label="Instructions">
      <Textarea name="instructions" placeholder="Step-by-step preparation..." bind:value={instructions} rows={4} />
    </FormField>

    <div class="flex justify-end gap-3 pt-2">
      <Btn variant="ghost" onclick={onClose}>Cancel</Btn>
      <Btn variant="primary" onclick={handleSubmit} disabled={!canSave || saving}>
        {saving ? 'Saving...' : recipe ? 'Save' : 'Create'}
      </Btn>
    </div>
  </div>
</Modal>
