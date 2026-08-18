<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import type { FoodItem } from '$lib/db/types';
  import type { RecipeIngredientInput } from '$lib/mutations/recipe';

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
      description?: string | null;
      instructions?: string | null;
      servings: number;
      prep_time_min?: number | null;
      cook_time_min?: number | null;
    } | null;
    recipeIngredients?: {
      food_item_id: string;
      amount_g: number;
      notes?: string | null;
    }[];
    existingIngredients?: IngredientSelection[];
    foodItems?: FoodItem[];
    onSave: (data: {
      name: string;
      description?: string;
      instructions?: string;
      servings: number;
      prep_time_min?: number | null;
      cook_time_min?: number | null;
      ingredients: RecipeIngredientInput[];
    }) => void;
    onClose: () => void;
    saving?: boolean;
  }

  let {
    open,
    recipe,
    recipeIngredients = [],
    existingIngredients = [],
    foodItems = [],
    onSave,
    onClose,
    saving = false
  }: Props = $props();

  let name = $state('');
  let description = $state('');
  let instructions = $state('');
  let servings = $state(1);
  let prepTimeMin = $state<number | undefined>(undefined);
  let cookTimeMin = $state<number | undefined>(undefined);
  let ingredients = $state<IngredientSelection[]>([]);
  let search = $state('');

  $effect(() => {
    if (!open) return;
    if (recipe) {
      name = recipe.name;
      description = recipe.description ?? '';
      instructions = recipe.instructions ?? '';
      servings = recipe.servings;
      prepTimeMin = recipe.prep_time_min ?? undefined;
      cookTimeMin = recipe.cook_time_min ?? undefined;

      if (recipeIngredients.length > 0) {
        const foodMap = new Map(foodItems.map((f) => [f.id, f]));
        ingredients = recipeIngredients.map((ri) => {
          const food = foodMap.get(ri.food_item_id);
          return {
            foodItemId: ri.food_item_id,
            amountG: ri.amount_g,
            name: food?.name ?? 'Zutat',
            calories: food?.calories_per_serving ?? 0,
            proteinG: food?.protein_g ?? 0,
            carbsG: food?.carbs_g ?? 0,
            fatG: food?.fat_g ?? 0,
            notes: ri.notes ?? ''
          };
        });
      } else {
        ingredients = [...existingIngredients];
      }
    } else {
      name = '';
      description = '';
      instructions = '';
      servings = 1;
      prepTimeMin = undefined;
      cookTimeMin = undefined;
      ingredients = [];
    }
  });

  const filteredItems = $derived(
    search.trim()
      ? foodItems.filter(
          (f) =>
            f.name.toLowerCase().includes(search.toLowerCase()) ||
            (f.brand && f.brand.toLowerCase().includes(search.toLowerCase()))
        )
      : []
  );

  function addIngredient(food: FoodItem) {
    if (ingredients.some((i) => i.foodItemId === food.id)) return;
    ingredients.push({
      foodItemId: food.id,
      amountG: food.serving_size || 100,
      name: food.name,
      calories: food.calories_per_serving,
      proteinG: food.protein_g,
      carbsG: food.carbs_g,
      fatG: food.fat_g,
      notes: ''
    });
    search = '';
  }

  function removeIngredient(foodItemId: string) {
    ingredients = ingredients.filter((i) => i.foodItemId !== foodItemId);
  }

  function updateAmount(foodItemId: string, amountG: number) {
    const item = ingredients.find((i) => i.foodItemId === foodItemId);
    if (item) item.amountG = amountG;
  }

  const isValid = $derived(name.trim().length > 0 && servings > 0);

  function handleSubmit() {
    if (!isValid) return;
    onSave({
      name: name.trim(),
      description: description.trim() || undefined,
      instructions: instructions.trim() || undefined,
      servings,
      prep_time_min: prepTimeMin !== undefined ? Number(prepTimeMin) : null,
      cook_time_min: cookTimeMin !== undefined ? Number(cookTimeMin) : null,
      ingredients: ingredients.map((i) => ({
        food_item_id: i.foodItemId,
        amount_g: i.amountG,
        notes: i.notes || undefined
      }))
    });
  }
</script>

<Modal
  {open}
  onclose={onClose}
  title={recipe ? 'Rezept bearbeiten' : 'Neues Rezept'}
  subtitle="Zutaten, Nährwerte und Zubereitungsschritte"
  icon="menu_book"
  size="lg"
>
  <form
    onsubmit={(e) => {
      e.preventDefault();
      handleSubmit();
    }}
    class="space-y-4 text-xs"
  >
    <Input
      label="Rezeptname"
      name="recipe_name"
      placeholder="z. B. Protein Haferflocken Bowl"
      bind:value={name}
      required
    />

    <Input
      label="Kurzbeschreibung (optional)"
      name="description"
      placeholder="z. B. Schnelles Post-Workout Frühstück mit hohem Proteingehalt"
      bind:value={description}
    />

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <Input
        label="Portionen"
        name="servings"
        type="number"
        bind:value={servings}
        min={1}
        required
      />
      <Input
        label="Vorbereitungszeit (Minuten)"
        name="prep_time"
        type="number"
        bind:value={prepTimeMin}
        min={0}
        placeholder="10"
      />
      <Input
        label="Koch-/Backzeit (Minuten)"
        name="cook_time"
        type="number"
        bind:value={cookTimeMin}
        min={0}
        placeholder="20"
      />
    </div>

    <div>
      <Input
        label="Zutaten aus Datenbank hinzufügen"
        icon="search"
        name="recipe_food_search"
        placeholder="Lebensmittel suchen..."
        bind:value={search}
      />
    </div>

    {#if search.trim() && filteredItems.length > 0}
      <div
        class="max-h-40 divide-y divide-[var(--border-subtle)] overflow-y-auto rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)]"
      >
        {#each filteredItems.slice(0, 10) as food (food.id)}
          <button
            type="button"
            onclick={() => addIngredient(food)}
            class="flex w-full cursor-pointer items-center justify-between px-3.5 py-2.5 text-left transition-colors hover:bg-[var(--bg-surface-50)]"
          >
            <div>
              <div class="text-xs font-bold text-[var(--text-main)]">{food.name}</div>
              <div class="text-[0.6875rem] text-[var(--text-muted)]">
                {food.calories_per_serving} kcal pro {food.serving_size}
                {food.serving_unit}
              </div>
            </div>
            <Icon name="add-circle" size="sm" class="text-[var(--color-primary)]" />
          </button>
        {/each}
      </div>
    {/if}

    {#if ingredients.length > 0}
      <div class="space-y-2 rounded-2xl border border-[var(--border-subtle)] p-3">
        <h3 class="text-xs font-bold tracking-wider text-[var(--text-muted)] uppercase">
          Enthaltene Zutaten ({ingredients.length})
        </h3>
        <div class="flex flex-col gap-2">
          {#each ingredients as ing (ing.foodItemId)}
            <div
              class="flex items-center gap-3 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3 py-2"
            >
              <div class="min-w-0 flex-1">
                <div class="truncate text-xs font-bold text-[var(--text-main)]">{ing.name}</div>
                <div class="text-[0.6875rem] text-[var(--text-muted)]">
                  {Math.round(ing.calories * (ing.amountG / 100))} kcal
                </div>
              </div>
              <div class="flex flex-shrink-0 items-center gap-2">
                <div class="w-28">
                  <Input
                    name={'amount_' + ing.foodItemId}
                    type="number"
                    value={ing.amountG}
                    min={1}
                    unit="g"
                    oninput={(e) =>
                      updateAmount(ing.foodItemId, Number((e.target as HTMLInputElement).value))}
                  />
                </div>
                <button
                  type="button"
                  onclick={() => removeIngredient(ing.foodItemId)}
                  class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-xl text-[var(--text-muted)] transition-colors hover:bg-rose-500/10 hover:text-rose-500"
                >
                  <Icon name="close" size="sm" />
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <Textarea
      label="Zubereitungsschritte"
      name="instructions"
      placeholder="Schritt-für-Schritt Zubereitungsanleitung..."
      bind:value={instructions}
      rows={4}
    />

    <div class="flex justify-end gap-2 border-t border-[var(--border-subtle)] pt-3">
      <Btn variant="secondary" size="md" onclick={onClose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" type="submit" disabled={!isValid || saving} loading={saving}>
        {recipe ? 'Speichern' : 'Rezept anlegen'}
      </Btn>
    </div>
  </form>
</Modal>
