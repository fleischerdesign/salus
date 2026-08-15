<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import Input from '$components/ui/Input.svelte';

  interface Props {
    open: boolean;
    recipeName: string;
    recipeServings: number;
    onCook: (servings: number) => void;
    onClose: () => void;
    cooking?: boolean;
  }

  let { open, recipeName, recipeServings, onCook, onClose, cooking = false }: Props = $props();

  let servings = $state(1);

  $effect(() => {
    if (open) servings = recipeServings;
  });
</script>

<Modal {open} onclose={onClose} title="Cook Recipe">
  <div class="flex flex-col gap-4">
    <p class="text-sm text-surface-600">
      Log <span class="font-semibold text-surface-900">{recipeName}</span> as a meal.
    </p>
    <FormField label="Servings">
      <Input name="cook_servings" type="number" bind:value={servings} min={1} step={0.5} />
    </FormField>
    <div class="flex justify-end gap-3 pt-2">
      <Btn variant="ghost" onclick={onClose}>Cancel</Btn>
      <Btn
        variant="primary"
        onclick={() => onCook(servings)}
        loading={cooking}
        disabled={servings < 1}
      >
        Cook {servings}
        {servings === 1 ? 'serving' : 'servings'}
      </Btn>
    </div>
  </div>
</Modal>
