<script lang="ts">
  import Select from '../ui/Select.svelte';
  import Modal from '../ui/Modal.svelte';
  import type { RecipeData, LoggedFoodItem, RecipeIngredient } from '../../types/nutrition';

  let {
    open = false,
    recipe = null,
    onlogrecipe,
    onclose
  } = $props<{
    open: boolean;
    recipe: RecipeData | null;
    onlogrecipe: (
      mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack',
      item: LoggedFoodItem
    ) => void;
    onclose: () => void;
  }>();

  let portions = $state(2);
  let targetMealType = $state<'breakfast' | 'lunch' | 'dinner' | 'snack'>('lunch');

  const mealTypeOptions = [
    { value: 'breakfast', label: 'Frühstück' },
    { value: 'lunch', label: 'Mittagessen' },
    { value: 'dinner', label: 'Abendessen' },
    { value: 'snack', label: 'Snacks' }
  ];

  $effect(() => {
    if (open && recipe) {
      portions = recipe.basePortions || 2;
    }
  });

  let scaledIngredients = $derived(
    recipe
      ? recipe.ingredients.map((ing: RecipeIngredient) => ({
          ...ing,
          amount: Math.round((ing.amount / recipe.basePortions) * portions),
          kcal: Math.round((ing.kcal / recipe.basePortions) * portions),
          protein: Number(((ing.protein / recipe.basePortions) * portions).toFixed(1)),
          carbs: Number(((ing.carbs / recipe.basePortions) * portions).toFixed(1)),
          fat: Number(((ing.fat / recipe.basePortions) * portions).toFixed(1))
        }))
      : []
  );

  let totalKcal = $derived(
    scaledIngredients.reduce((sum: number, item: { kcal: number }) => sum + item.kcal, 0)
  );
  let totalProtein = $derived(
    Number(
      scaledIngredients
        .reduce((sum: number, item: { protein: number }) => sum + item.protein, 0)
        .toFixed(1)
    )
  );
  let totalCarbs = $derived(
    Number(
      scaledIngredients
        .reduce((sum: number, item: { carbs: number }) => sum + item.carbs, 0)
        .toFixed(1)
    )
  );
  let totalFat = $derived(
    Number(
      scaledIngredients.reduce((sum: number, item: { fat: number }) => sum + item.fat, 0).toFixed(1)
    )
  );

  let perPortionKcal = $derived(portions > 0 ? Math.round(totalKcal / portions) : 0);
  let perPortionP = $derived(portions > 0 ? Number((totalProtein / portions).toFixed(1)) : 0);
  let perPortionC = $derived(portions > 0 ? Number((totalCarbs / portions).toFixed(1)) : 0);
  let perPortionF = $derived(portions > 0 ? Number((totalFat / portions).toFixed(1)) : 0);

  function handleLogPortion() {
    if (!recipe) return;

    const loggedItem: LoggedFoodItem = {
      id: `recipe_log_${Date.now()}`,
      name: `${recipe.title} (1 Portion)`,
      amountG: 350,
      kcal: perPortionKcal,
      protein: perPortionP,
      carbs: perPortionC,
      fat: perPortionF,
      fiber: 4.5
    };

    onlogrecipe(targetMealType, loggedItem);
    onclose();
  }
</script>

<Modal
  open={open && Boolean(recipe)}
  title={recipe?.title || ''}
  subtitle={`${recipe?.category || ''} • ${recipe?.prepTime || ''} Zubereitung`}
  size="lg"
  {onclose}
>
  <div class="space-y-5">
    <!-- Macro Summary Hero Banner (Scales dynamically) -->
    <div
      class="space-y-3 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4"
    >
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span class="text-xs font-bold text-[var(--text-muted)] uppercase">Portionen anpassen:</span
        >

        <div
          class="flex items-center gap-2 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-1 shadow-2xs"
        >
          <button
            type="button"
            onclick={() => (portions = Math.max(1, portions - 1))}
            class="h-7 w-7 cursor-pointer rounded-xl bg-[var(--bg-surface-50)] text-xs font-bold text-[var(--text-main)] hover:bg-[var(--bg-surface-100)]"
          >
            -
          </button>
          <span class="px-2 text-xs font-extrabold tabular-nums"
            >{portions} {portions === 1 ? 'Portion' : 'Portionen'}</span
          >
          <button
            type="button"
            onclick={() => (portions = Math.min(10, portions + 1))}
            class="h-7 w-7 cursor-pointer rounded-xl bg-[var(--bg-surface-50)] text-xs font-bold text-[var(--text-main)] hover:bg-[var(--bg-surface-100)]"
          >
            +
          </button>
        </div>
      </div>

      <!-- Macro Stats (Total & Per Portion) -->
      <div class="grid grid-cols-4 gap-2 text-center text-xs">
        <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2">
          <span class="block text-[0.625rem] text-[var(--text-muted)]">Kalorien / Port.</span>
          <span class="text-sm font-extrabold text-[var(--color-activity)] tabular-nums"
            >{perPortionKcal} kcal</span
          >
        </div>
        <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2">
          <span class="block text-[0.625rem] text-[var(--text-muted)]">Protein / Port.</span>
          <span class="text-sm font-extrabold text-emerald-500 tabular-nums">{perPortionP}g</span>
        </div>
        <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2">
          <span class="block text-[0.625rem] text-[var(--text-muted)]">Carbs / Port.</span>
          <span class="text-sm font-extrabold text-amber-500 tabular-nums">{perPortionC}g</span>
        </div>
        <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2">
          <span class="block text-[0.625rem] text-[var(--text-muted)]">Fett / Port.</span>
          <span class="text-sm font-extrabold text-purple-500 tabular-nums">{perPortionF}g</span>
        </div>
      </div>
    </div>

    <!-- Scaled Ingredients Table -->
    <div class="space-y-1.5">
      <span class="block text-xs font-extrabold text-[var(--text-main)]"
        >Zutaten ({portions} Portionen):</span
      >
      <div
        class="overflow-hidden rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)]"
      >
        <table class="w-full border-collapse text-left text-xs">
          <thead>
            <tr
              class="border-b border-[var(--border-subtle)] bg-[var(--bg-surface-50)]/50 text-[0.625rem] tracking-wider text-[var(--text-muted)] uppercase"
            >
              <th class="px-3 py-2">Zutat</th>
              <th class="px-3 py-2">Menge</th>
              <th class="px-3 py-2">Kalorien</th>
              <th class="px-3 py-2 text-right">Protein</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-subtle)]/50">
            {#each scaledIngredients as ing}
              <tr>
                <td class="px-3 py-2.5 font-bold text-[var(--text-main)]">{ing.name}</td>
                <td class="px-3 py-2.5 text-[var(--text-muted)] tabular-nums"
                  >{ing.amount} {ing.unit}</td
                >
                <td class="px-3 py-2.5 text-[var(--text-muted)] tabular-nums">{ing.kcal} kcal</td>
                <td class="px-3 py-2.5 text-right font-bold text-emerald-500 tabular-nums"
                  >{ing.protein}g</td
                >
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Step-by-Step Cooking Instructions -->
    <div class="space-y-1.5">
      <span class="block text-xs font-extrabold text-[var(--text-main)]">Zubereitungsschritte:</span
      >
      <div class="space-y-2">
        {#each recipe.instructions as step, sIdx}
          <div
            class="flex items-start gap-2.5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-2.5 text-xs text-[var(--text-main)]"
          >
            <span
              class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)]/10 text-[0.6875rem] font-bold text-[var(--color-primary)]"
            >
              {sIdx + 1}
            </span>
            <span class="leading-relaxed">{step}</span>
          </div>
        {/each}
      </div>
    </div>

    <!-- Log to Diary Bar -->
    <div
      class="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3"
    >
      <div class="flex min-w-[200px] items-center gap-2">
        <span class="shrink-0 text-xs font-bold text-[var(--text-muted)]">Eintragen in:</span>
        <div class="flex-1">
          <Select bind:value={targetMealType} options={mealTypeOptions} />
        </div>
      </div>

      <button
        type="button"
        onclick={handleLogPortion}
        class="cursor-pointer rounded-xl bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90"
      >
        1 Portion ins Tagebuch loggen
      </button>
    </div>
  </div>
</Modal>
