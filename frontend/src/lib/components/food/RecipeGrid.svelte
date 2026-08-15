<script lang="ts">
  import EmptyState from '$components/ui/EmptyState.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import RecipeCard from './RecipeCard.svelte';

  interface Props {
    recipes: {
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
    }[];
    onCook: (recipeId: string) => void;
    onCreate: () => void;
  }

  let { recipes, onCook, onCreate }: Props = $props();
</script>

{#if recipes.length === 0}
  <EmptyState
    icon="menu-book"
    title="No recipes"
    description="Create your first recipe to quickly log frequent meals."
  >
    <Btn variant="primary" onclick={onCreate}>Create Recipe</Btn>
  </EmptyState>
{:else}
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
    {#each recipes as recipe (recipe.id)}
      <RecipeCard
        id={recipe.id}
        name={recipe.name}
        description={recipe.description}
        servings={recipe.servings}
        totalCalories={recipe.totalCalories}
        totalProtein={recipe.totalProtein}
        totalCarbs={recipe.totalCarbs}
        totalFat={recipe.totalFat}
        prepTimeMin={recipe.prepTimeMin}
        cookTimeMin={recipe.cookTimeMin}
        isFavorite={recipe.isFavorite}
        onCook={() => onCook(recipe.id)}
      />
    {/each}
  </div>
{/if}
