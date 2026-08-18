<script lang="ts">
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
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

  let name = $state('');
  let activeIngredient = $state('');
  let strength = $state('');
  let form = $state('tablet');
  let instructions = $state('');
  let colorHex = $state('#4f46e5');
  let icon = $state('medication');

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

<Modal
  {open}
  onclose={onClose}
  title={medication ? 'Medikament bearbeiten' : 'Neues Medikament anlegen'}
  subtitle="Erfasse Wirkstoff, Dosierung und Einnahmehinweise"
  icon="medication"
  size="md"
>
  <form
    onsubmit={(e) => {
      e.preventDefault();
      handleSubmit();
    }}
    class="space-y-4 text-xs"
  >
    <Input
      label="Name"
      name="name"
      placeholder="z. B. Ibuprofen 400mg"
      bind:value={name}
      required
    />

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Input
        label="Wirkstoff"
        name="active_ingredient"
        placeholder="z. B. Ibuprofen"
        bind:value={activeIngredient}
      />
      <Input
        label="Stärke / Dosierung"
        name="strength"
        placeholder="z. B. 400mg"
        bind:value={strength}
      />
    </div>

    <div>
      <span class="mb-1.5 block text-xs font-bold text-[var(--text-main)]">Darreichungsform</span>
      <div class="flex flex-wrap gap-1.5">
        {#each forms as f}
          <button
            type="button"
            onclick={() => (form = f)}
            class="cursor-pointer rounded-xl border px-3 py-1.5 text-xs font-bold transition-all {form ===
            f
              ? 'border-[var(--color-primary)] bg-[var(--color-primary)] text-white shadow-xs'
              : 'border-[var(--border-subtle)] bg-[var(--bg-surface-0)] text-[var(--text-muted)] hover:border-[var(--color-primary)]'}"
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        {/each}
      </div>
    </div>

    <Input
      label="Einnahmehinweise"
      name="instructions"
      placeholder="z. B. Nach den Mahlzeiten mit reichlich Wasser einnehmen"
      bind:value={instructions}
    />

    <div class="grid grid-cols-1 items-end gap-3 sm:grid-cols-2">
      <div>
        <span class="mb-1.5 block text-xs font-bold text-[var(--text-main)]">Farbe</span>
        <div
          class="flex h-10 items-center gap-2.5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] px-3"
        >
          <input
            type="color"
            bind:value={colorHex}
            class="h-6 w-8 cursor-pointer rounded-lg border-0 bg-transparent"
          />
          <span class="font-mono text-xs font-semibold text-[var(--text-muted)]">{colorHex}</span>
        </div>
      </div>

      <Input
        label="Icon-Name"
        name="icon"
        placeholder="z. B. medication, pill, local_pharmacy"
        bind:value={icon}
      />
    </div>

    <div class="flex justify-end gap-2 border-t border-[var(--border-subtle)] pt-3">
      <Btn variant="secondary" size="md" onclick={onClose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" type="submit" disabled={!isValid || saving} loading={saving}>
        {medication ? 'Speichern' : 'Medikament anlegen'}
      </Btn>
    </div>
  </form>
</Modal>
