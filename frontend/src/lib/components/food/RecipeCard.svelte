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
    prepTimeMin,
    cookTimeMin,
    isFavorite,
    onCook
  }: Props = $props();
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="group block cursor-pointer"
  onclick={() => goto('/recipes/' + id)}
  onkeydown={(e) => { if (e.key === 'Enter') goto('/recipes/' + id); }}
  role="link"
  tabindex="0"
>
  <Card hoverable padding={false}>
    <div class="p-4 pb-2">
      <div class="flex items-start gap-3">
        <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-600">
          <Icon name="menu-book" size="md" />
        </div>

        <div class="min-w-0 flex-1 pt-0.5">
          <div class="font-semibold text-surface-900">{name}</div>
          {#if description}
            <div class="truncate text-xs text-surface-500">{description}</div>
          {/if}
          <div class="mt-1 text-xs text-surface-400">
            {servings} serving{servings !== 1 ? 's' : ''}
            · {Math.round(totalCalories / servings)} kcal/serving
            {#if prepTimeMin || cookTimeMin}
              · {prepTimeMin ? `${prepTimeMin}m prep` : ''}{prepTimeMin && cookTimeMin ? ' + ' : ''}{cookTimeMin ? `${cookTimeMin}m cook` : ''}
            {/if}
          </div>
        </div>

        {#if isFavorite}
          <Icon name="favorite" size="sm" class="mt-0.5 text-amber-500" />
        {/if}
      </div>
    </div>

    <div class="border-t border-surface-100"></div>

    <div class="flex items-center justify-between px-4 py-2.5">
      <span class="text-xs text-surface-400">{Math.round(totalCalories)} kcal total</span>
      <button
        onclick={(e) => { e.stopPropagation(); onCook(); }}
        class="rounded-full bg-primary-500 px-4 py-1.5 text-xs font-semibold text-white hover:bg-primary-600 transition-colors"
      >
        Cook
      </button>
    </div>
  </Card>
</div>
