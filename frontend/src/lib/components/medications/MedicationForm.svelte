<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import Input from '$components/ui/Input.svelte';

  interface Props {
    open: boolean;
    medication?: {
      name: string;
      active_ingredient: string;
      strength: string;
      form: string;
      instructions: string;
      color_hex: string;
      icon: string;
    } | null;
    onSave: (data: {
      name: string;
      active_ingredient: string;
      strength: string;
      form: string;
      instructions: string;
      color_hex: string;
      icon: string;
    }) => void;
    onClose: () => void;
    saving?: boolean;
  }

  let { open, medication, onSave, onClose, saving = false }: Props = $props();

  const forms = ['tablet', 'capsule', 'liquid', 'injection', 'patch', 'cream', 'drops'];

  let name = $state(medication?.name ?? '');
  let activeIngredient = $state(medication?.active_ingredient ?? '');
  let strength = $state(medication?.strength ?? '');
  let form = $state(medication?.form ?? 'tablet');
  let instructions = $state(medication?.instructions ?? '');
  let colorHex = $state(medication?.color_hex ?? '#4f46e5');
  let icon = $state(medication?.icon ?? 'medication');

  $effect(() => {
    if (medication) {
      name = medication.name;
      activeIngredient = medication.active_ingredient ?? '';
      strength = medication.strength ?? '';
      form = medication.form;
      instructions = medication.instructions ?? '';
      colorHex = medication.color_hex;
      icon = medication.icon;
    } else {
      name = '';
      activeIngredient = '';
      strength = '';
      form = 'tablet';
      instructions = '';
      colorHex = '#4f46e5';
      icon = 'medication';
    }
  });

  const isValid = $derived(name.trim().length > 0);

  function handleSubmit() {
    if (!isValid) return;
    onSave({
      name: name.trim(),
      active_ingredient: activeIngredient.trim() || '',
      strength: strength.trim() || '',
      form,
      instructions: instructions.trim() || '',
      color_hex: colorHex,
      icon
    });
  }
</script>

<Modal {open} onclose={onClose} title={medication ? 'Edit Medication' : 'New Medication'}>
  <div class="flex flex-col gap-4">
    <FormField label="Name" required>
      <Input name="name" placeholder="e.g. Ibuprofen 400mg" bind:value={name} />
    </FormField>

    <div class="grid grid-cols-2 gap-4">
      <FormField label="Active Ingredient">
        <Input
          name="active_ingredient"
          placeholder="e.g. Ibuprofen"
          bind:value={activeIngredient}
        />
      </FormField>
      <FormField label="Strength">
        <Input name="strength" placeholder="e.g. 400mg" bind:value={strength} />
      </FormField>
    </div>

    <FormField label="Form">
      <div class="flex flex-wrap gap-2">
        {#each forms as f}
          <button
            type="button"
            onclick={() => (form = f)}
            class="rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors"
            class:border-primary-500={form === f}
            class:bg-primary-50={form === f}
            class:text-primary-700={form === f}
            class:border-surface-200={form !== f}
            class:text-surface-600={form !== f}
            class:hover:border-surface-300={form !== f}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        {/each}
      </div>
    </FormField>

    <FormField label="Instructions">
      <Input name="instructions" placeholder="e.g. Take with food" bind:value={instructions} />
    </FormField>

    <FormField label="Color">
      <div class="flex items-center gap-3">
        <input
          type="color"
          bind:value={colorHex}
          class="h-9 w-12 cursor-pointer rounded border border-surface-200"
        />
        <span class="text-xs text-surface-500">{colorHex}</span>
      </div>
    </FormField>

    <FormField label="Icon">
      <Input name="icon" placeholder="Material Symbols icon name" bind:value={icon} />
    </FormField>

    <div class="flex justify-end gap-3 pt-2">
      <Btn variant="ghost" onclick={onClose}>Cancel</Btn>
      <Btn variant="primary" onclick={handleSubmit} disabled={!isValid || saving}>
        {saving ? 'Saving...' : medication ? 'Save' : 'Create'}
      </Btn>
    </div>
  </div>
</Modal>
