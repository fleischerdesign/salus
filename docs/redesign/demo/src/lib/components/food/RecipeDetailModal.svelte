<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import type { RecipeData, LoggedFoodItem } from '../../types/nutrition';

  let {
    open = false,
    recipe = null,
    onlogrecipe,
    onclose
  } = $props<{
    open: boolean;
    recipe: RecipeData | null;
    onlogrecipe: (mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack', item: LoggedFoodItem) => void;
    onclose: () => void;
  }>();

  let portions = $state(2);
  let targetMealType = $state<'breakfast' | 'lunch' | 'dinner' | 'snack'>('lunch');

  $effect(() => {
    if (open && recipe) {
      portions = recipe.basePortions || 2;
    }
  });

  let scaledIngredients = $derived(
    recipe ? recipe.ingredients.map(ing => ({
      ...ing,
      amount: Math.round((ing.amount / recipe.basePortions) * portions),
      kcal: Math.round((ing.kcal / recipe.basePortions) * portions),
      protein: Number(((ing.protein / recipe.basePortions) * portions).toFixed(1)),
      carbs: Number(((ing.carbs / recipe.basePortions) * portions).toFixed(1)),
      fat: Number(((ing.fat / recipe.basePortions) * portions).toFixed(1))
    })) : []
  );

  let totalKcal = $derived(scaledIngredients.reduce((sum, item) => sum + item.kcal, 0));
  let totalProtein = $derived(Number(scaledIngredients.reduce((sum, item) => sum + item.protein, 0).toFixed(1)));
  let totalCarbs = $derived(Number(scaledIngredients.reduce((sum, item) => sum + item.carbs, 0).toFixed(1)));
  let totalFat = $derived(Number(scaledIngredients.reduce((sum, item) => sum + item.fat, 0).toFixed(1)));

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

{#if open && recipe}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-70 flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl space-y-5 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-base sm:text-lg font-extrabold text-[var(--text-main)]">{recipe.title}</h2>
            <Badge variant="activity" class="text-[0.625rem]">{recipe.rating}</Badge>
          </div>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">{recipe.category} &bull; {recipe.prepTime} Zubereitung</p>
        </div>

        <button
          type="button"
          onclick={onclose}
          class="w-8 h-8 rounded-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center text-lg cursor-pointer transition-colors"
          title="Schließen"
          aria-label="Schließen"
        >
          &times;
        </button>
      </div>

      <!-- Dynamic Portion Stepper & Live Macros -->
      <div class="p-4 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-3xl space-y-3">
        
        <div class="flex items-center justify-between flex-wrap gap-2">
          <span class="text-xs font-bold text-[var(--text-muted)] uppercase">Portionen anpassen:</span>
          
          <div class="flex items-center gap-2 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-1 shadow-2xs">
            <button
              type="button"
              onclick={() => portions = Math.max(1, portions - 1)}
              class="w-7 h-7 rounded-xl bg-[var(--bg-surface-50)] text-xs font-bold text-[var(--text-main)] hover:bg-[var(--bg-surface-100)] cursor-pointer"
            >
              -
            </button>
            <span class="text-xs font-extrabold px-2 tabular-nums">{portions} {portions === 1 ? 'Portion' : 'Portionen'}</span>
            <button
              type="button"
              onclick={() => portions = Math.min(10, portions + 1)}
              class="w-7 h-7 rounded-xl bg-[var(--bg-surface-50)] text-xs font-bold text-[var(--text-main)] hover:bg-[var(--bg-surface-100)] cursor-pointer"
            >
              +
            </button>
          </div>
        </div>

        <!-- Macro Stats (Total & Per Portion) -->
        <div class="grid grid-cols-4 gap-2 text-center text-xs">
          <div class="p-2 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)]">
            <span class="text-[0.625rem] text-[var(--text-muted)] block">Kalorien / Port.</span>
            <span class="text-sm font-extrabold text-[var(--color-activity)] tabular-nums">{perPortionKcal} kcal</span>
          </div>
          <div class="p-2 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)]">
            <span class="text-[0.625rem] text-[var(--text-muted)] block">Protein / Port.</span>
            <span class="text-sm font-extrabold text-emerald-500 tabular-nums">{perPortionP}g</span>
          </div>
          <div class="p-2 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)]">
            <span class="text-[0.625rem] text-[var(--text-muted)] block">Carbs / Port.</span>
            <span class="text-sm font-extrabold text-amber-500 tabular-nums">{perPortionC}g</span>
          </div>
          <div class="p-2 rounded-2xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)]">
            <span class="text-[0.625rem] text-[var(--text-muted)] block">Fett / Port.</span>
            <span class="text-sm font-extrabold text-purple-500 tabular-nums">{perPortionF}g</span>
          </div>
        </div>

      </div>

      <!-- Scaled Ingredients Table -->
      <div class="space-y-1.5">
        <span class="text-xs font-extrabold text-[var(--text-main)] block">Zutaten ({portions} Portionen):</span>
        <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl overflow-hidden">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="text-[var(--text-muted)] border-b border-[var(--border-subtle)] uppercase tracking-wider text-[0.625rem] bg-[var(--bg-surface-50)]/50">
                <th class="py-2 px-3">Zutat</th>
                <th class="py-2 px-3">Menge</th>
                <th class="py-2 px-3">Kalorien</th>
                <th class="py-2 px-3 text-right">Protein</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-subtle)]/50">
              {#each scaledIngredients as ing}
                <tr>
                  <td class="py-2.5 px-3 font-bold text-[var(--text-main)]">{ing.name}</td>
                  <td class="py-2.5 px-3 text-[var(--text-muted)] tabular-nums">{ing.amount} {ing.unit}</td>
                  <td class="py-2.5 px-3 text-[var(--text-muted)] tabular-nums">{ing.kcal} kcal</td>
                  <td class="py-2.5 px-3 text-right font-bold text-emerald-500 tabular-nums">{ing.protein}g</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Step-by-Step Cooking Instructions -->
      <div class="space-y-1.5">
        <span class="text-xs font-extrabold text-[var(--text-main)] block">Zubereitungsschritte:</span>
        <div class="space-y-2">
          {#each recipe.instructions as step, sIdx}
            <div class="p-2.5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl flex items-start gap-2.5 text-xs text-[var(--text-main)]">
              <span class="w-5 h-5 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] font-bold text-[0.6875rem] flex items-center justify-center shrink-0">
                {sIdx + 1}
              </span>
              <span class="leading-relaxed">{step}</span>
            </div>
          {/each}
        </div>
      </div>

      <!-- Log to Diary Bar -->
      <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-[var(--text-muted)]">1 Portion eintragen in:</span>
          <select
            bind:value={targetMealType}
            class="px-2.5 py-1 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-xs font-bold text-[var(--text-main)] outline-none cursor-pointer"
          >
            <option value="breakfast">Frühstück</option>
            <option value="lunch">Mittagessen</option>
            <option value="dinner">Abendessen</option>
            <option value="snack">Snacks</option>
          </select>
        </div>

        <button
          type="button"
          onclick={handleLogPortion}
          class="px-4 py-2 rounded-xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer shadow-xs"
        >
          1 Portion ins Tagebuch loggen
        </button>
      </div>

    </div>
  </div>
{/if}
