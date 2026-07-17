<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import FormField from '$components/forms/FormField.svelte';

  interface Props {
    open: boolean;
    habit?: {
      name: string;
      description: string;
      color: string;
      icon: string;
      frequency: string;
      target_count: number;
      days_bitmask?: number | null;
      stack_hint: string;
    } | null;
    onSave: (data: {
      name: string;
      description: string;
      color: string;
      icon: string;
      frequency: string;
      target_count: number;
      days_bitmask?: number | null;
      stack_hint: string;
    }) => Promise<void>;
    onClose: () => void;
  }

  let { open, habit = null, onSave, onClose }: Props = $props();

  let name = $state(habit?.name ?? '');
  let description = $state(habit?.description ?? '');
  let color = $state(habit?.color ?? '#4f46e5');
  let icon = $state(habit?.icon ?? 'check-circle');
  let frequency = $state(habit?.frequency ?? 'daily');
  let targetCount = $state(habit?.target_count ?? 1);
  let targetCountStr = $state(String(habit?.target_count ?? 1));
  let stackHint = $state(habit?.stack_hint ?? '');
  let daysMask = $state(habit?.days_bitmask ?? 0);
  let saving = $state(false);

  const colors = [
    '#4f46e5',
    '#ef4444',
    '#f59e0b',
    '#10b981',
    '#06b6d4',
    '#818cf8',
    '#ec4899',
    '#8b5cf6',
    '#f97316'
  ];
  const icons = [
    'check-circle',
    'self-improvement',
    'exercise',
    'restaurant',
    'menu-book',
    'bedtime',
    'water-drop',
    'psychology',
    'music-note'
  ];
  const dayLabels = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];

  function toggleDay(i: number) {
    daysMask ^= 1 << i;
  }

  async function handleSubmit() {
    if (!name.trim()) return;
    saving = true;
    try {
      await onSave({
        name: name.trim(),
        description: description.trim() || '',
        color,
        icon,
        frequency,
        target_count: targetCount,
        days_bitmask: frequency === 'custom_days' ? daysMask : null,
        stack_hint: stackHint.trim() || ''
      });
    } finally {
      saving = false;
    }
  }
</script>

<!-- scanner hints: icon="self-improvement" icon="restaurant" icon="music-note" -->
<Modal title={habit ? 'Edit Habit' : 'New Habit'} bind:open>
  <form
    onsubmit={(e) => {
      e.preventDefault();
      handleSubmit();
    }}
    class="flex flex-col gap-4"
  >
    <FormField label="Name" required>
      <Input name="name" bind:value={name} required placeholder="e.g. Morning stretch" />
    </FormField>

    <FormField label="Description">
      <Input name="description" bind:value={description} placeholder="Optional" />
    </FormField>

    <div>
      <label class="mb-1.5 block text-xs font-bold tracking-wider text-surface-500 uppercase"
        >Color</label
      >
      <div class="flex gap-2">
        {#each colors as c}
          <button
            type="button"
            class="h-8 w-8 rounded-full border-2 transition-all"
            class:border-surface-300={color !== c}
            class:border-surface-900={color === c}
            class:ring-2={color === c}
            class:ring-primary-300={color === c}
            style="background-color: {c}"
            onclick={() => (color = c)}
          ></button>
        {/each}
      </div>
    </div>

    <div>
      <label class="mb-1.5 block text-xs font-bold tracking-wider text-surface-500 uppercase"
        >Icon</label
      >
      <div class="flex flex-wrap gap-2">
        {#each icons as ico}
          <button
            type="button"
            class="duration-micro flex h-9 w-9 items-center justify-center rounded-lg border transition-all"
            class:border-surface-300={icon !== ico}
            class:border-primary-500={icon === ico}
            class:bg-primary-50={icon === ico}
            onclick={() => (icon = ico)}
          >
            <Icon
              name={ico}
              size="sm"
              class={icon === ico ? 'text-primary-600' : 'text-surface-500'}
            />
          </button>
        {/each}
      </div>
    </div>

    <FormField label="Frequency">
      <select
        bind:value={frequency as any}
        class="w-full rounded-lg border border-surface-200 bg-surface-0 px-3 py-2 text-sm text-surface-900"
      >
        <option value="daily">Every day</option>
        <option value="weekly_n">X times per week</option>
        <option value="custom_days">Custom days</option>
      </select>
    </FormField>

    {#if frequency === 'weekly_n'}
      <FormField label="Times per week">
        <input
          name="target_count"
          type="number"
          min="1"
          max="7"
          value={targetCount}
          oninput={(e) => {
            targetCount = parseInt((e.target as HTMLInputElement).value) || 1;
          }}
          class="duration-micro w-full rounded-lg border border-surface-200 bg-surface-0 px-3 py-2 text-sm text-surface-900 transition-colors hover:border-surface-300 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none"
        />
      </FormField>
    {/if}

    {#if frequency === 'custom_days'}
      <div>
        <label class="mb-1.5 block text-xs font-bold tracking-wider text-surface-500 uppercase"
          >Active Days</label
        >
        <div class="flex gap-1.5">
          {#each dayLabels as label, i}
            <button
              type="button"
              class="h-9 w-9 rounded-lg text-xs font-semibold transition-all"
              class:bg-primary-500={((daysMask >> i) & 1) === 1}
              class:text-white={((daysMask >> i) & 1) === 1}
              class:bg-surface-100={((daysMask >> i) & 1) === 0}
              class:text-surface-500={((daysMask >> i) & 1) === 0}
              onclick={() => toggleDay(i)}>{label}</button
            >
          {/each}
        </div>
      </div>
    {/if}

    <FormField label="Stack Hint (optional)">
      <Input name="stack_hint" bind:value={stackHint} placeholder="e.g. After brushing teeth" />
    </FormField>

    <div class="flex justify-end gap-2 border-t border-surface-100 pt-4">
      <Btn variant="ghost" onclick={onClose}>Cancel</Btn>
      <Btn variant="primary" loading={saving} onclick={handleSubmit}
        >{habit ? 'Save' : 'Create'}</Btn
      >
    </div>
  </form>
</Modal>
