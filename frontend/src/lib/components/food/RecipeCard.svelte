<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Card from '$components/ui/Card.svelte';
  import { goto } from '$app/navigation';

  interface Props {
    id: string;
    name: string;
    description: string | null;
    servings: number;
    totalCalories: number;
    totalProtein: number;
    totalCarbs: number;
    totalFat: number;
    prepTimeMin: number | null;
    cookTimeMin: number | null;
    isFavorite: boolean;
    onCook: () => void;
  }

  let {
    id,
    name,
    description,
    servings,
    totalCalories,
    totalProtein,
    totalCarbs,
    totalFat,
    prepTimeMin,
    cookTimeMin,
    isFavorite,
    onCook
  }: Props = $props();

  const perServing = $derived({
    calories: servings > 0 ? totalCalories / servings : 0,
    protein: servings > 0 ? totalProtein / servings : 0,
    carbs: servings > 0 ? totalCarbs / servings : 0,
    fat: servings > 0 ? totalFat / servings : 0
  });
</script>

<div
  class="group block cursor-pointer"
  onclick={() => goto('/recipes/' + id)}
  onkeydown={(e) => {
    if (e.key === 'Enter') goto('/recipes/' + id);
  }}
  role="link"
  tabindex="0"
>
  <Card hoverable padding={false}>
    <div class="p-4 pb-2">
      <div class="flex items-start gap-3">
        <div
          class="bg-warning-100 text-warning-600 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl"
        >
          <Icon name="menu-book" size="md" />
        </div>

        <div class="min-w-0 flex-1 pt-0.5">
          <div class="font-semibold text-surface-900">{name}</div>
          {#if description}
            <div class="truncate text-xs text-surface-500">{description}</div>
          {/if}
          <div class="mt-1 text-xs text-surface-400">
            {servings} serving{servings !== 1 ? 's' : ''}
            · {Math.round(perServing.calories)} kcal/serving
            {#if prepTimeMin || cookTimeMin}
              · {prepTimeMin ? `${prepTimeMin}m prep` : ''}{prepTimeMin && cookTimeMin
                ? ' + '
                : ''}{cookTimeMin ? `${cookTimeMin}m cook` : ''}
            {/if}
          </div>
        </div>

        {#if isFavorite}
          <Icon name="favorite" size="sm" class="text-warning-500 mt-0.5" />
        {/if}
      </div>

      <div class="mt-3 flex flex-wrap gap-x-4 gap-y-1 border-t border-surface-100 pt-2.5 text-xs">
        <span class="text-primary-600">P {Math.round(perServing.protein)}g</span>
        <span class="text-warning-600">C {Math.round(perServing.carbs)}g</span>
        <span class="text-error-500">F {Math.round(perServing.fat)}g</span>
        <span class="ml-auto text-surface-400">{Math.round(totalCalories)} kcal total</span>
      </div>
    </div>

    <div class="flex items-center justify-between border-t border-surface-100 px-4 py-2.5">
      <span class="text-xs text-surface-400">per serving</span>
      <button
        onclick={(e) => {
          e.stopPropagation();
          onCook();
        }}
        class="bg-primary-500 text-on-primary hover:bg-primary-600 rounded-full px-4 py-1.5 text-xs font-semibold transition-colors"
      >
        Cook
      </button>
    </div>
  </Card>
</div>
