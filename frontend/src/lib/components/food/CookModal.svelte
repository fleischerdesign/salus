<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Stepper from '$components/ui/Stepper.svelte';

  interface Props {
    open: boolean;
    recipeName: string;
    recipeServings: number;
    macros: { calories: number; protein: number; carbs: number; fat: number } | null;
    onCook: (servings: number) => void;
    onClose: () => void;
    cooking?: boolean;
  }

  let {
    open,
    recipeName,
    recipeServings,
    macros,
    onCook,
    onClose,
    cooking = false
  }: Props = $props();

  let servings = $state(1);

  $effect(() => {
    if (open) servings = recipeServings;
  });

  const scaled = $derived.by(() => {
    if (!macros) return null;
    const factor = servings / (recipeServings > 0 ? recipeServings : 1);
    return {
      calories: Math.round(macros.calories * factor),
      protein: Math.round(macros.protein * factor),
      carbs: Math.round(macros.carbs * factor),
      fat: Math.round(macros.fat * factor)
    };
  });
</script>

<Modal {open} onclose={onClose} title="Cook Recipe">
  <div class="flex flex-col gap-5">
    <p class="text-sm text-surface-600">
      Log <span class="font-semibold text-surface-900">{recipeName}</span> as a meal.
    </p>

    <div class="flex items-center justify-between rounded-xl bg-surface-50 px-4 py-3">
      <div>
        <div class="text-2xl font-bold text-surface-900 tabular-nums">
          {scaled ? scaled.calories.toLocaleString() : '—'}
          <span class="text-sm font-medium text-surface-400"> kcal</span>
        </div>
        <div class="mt-1 text-xs text-surface-500">
          {#if scaled}
            {scaled.protein}P · {scaled.carbs}C · {scaled.fat}F
          {:else}
            —
          {/if}
        </div>
      </div>
      <Stepper name="cook_servings" label="Servings" min={0.5} step={0.5} bind:value={servings} />
    </div>

    <div class="flex justify-end gap-3 pt-2">
      <Btn variant="ghost" onclick={onClose}>Cancel</Btn>
      <Btn
        variant="primary"
        onclick={() => onCook(servings)}
        loading={cooking}
        disabled={servings < 0.5}
      >
        Cook {servings}
        {servings === 1 ? 'serving' : 'servings'}
      </Btn>
    </div>
  </div>
</Modal>
