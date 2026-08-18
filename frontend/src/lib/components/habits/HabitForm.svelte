<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import { resolveColor } from '$lib/theme/colors';

  const frequencyOptions = [
    { value: 'daily', label: 'Every day' },
    { value: 'weekly_n', label: 'X times per week' },
    { value: 'custom_days', label: 'Custom days' }
  ];

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
      days_bitmask: number | null;
      stack_hint: string;
    }) => void;
    onClose: () => void;
    saving?: boolean;
  }

  let { open = $bindable(false), habit, onSave, onClose, saving = false }: Props = $props();

  const colors = [
    'rose',
    'orange',
    'amber',
    'emerald',
    'teal',
    'cyan',
    'blue',
    'indigo',
    'purple',
    'pink'
  ];

  const icons = [
    'check_circle',
    'fitness_center',
    'directions_run',
    'water_drop',
    'bedtime',
    'menu_book',
    'self_improvement',
    'nordic_walking',
    'restaurant',
    'timer'
  ];

  const dayLabels = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];

  let name = $state('');
  let description = $state('');
  let color = $state('blue');
  let icon = $state('check_circle');
  let frequency = $state('daily');
  let targetCount = $state(1);
  let daysMask = $state(127);
  let stackHint = $state('');

  $effect(() => {
    if (habit) {
      name = habit.name;
      description = habit.description ?? '';
      color = habit.color;
      icon = habit.icon;
      frequency = habit.frequency;
      targetCount = habit.target_count;
      daysMask = habit.days_bitmask ?? 127;
      stackHint = habit.stack_hint ?? '';
    } else {
      name = '';
      description = '';
      color = 'blue';
      icon = 'check_circle';
      frequency = 'daily';
      targetCount = 1;
      daysMask = 127;
      stackHint = '';
    }
  });

  function toggleDay(dayIndex: number) {
    daysMask ^= 1 << dayIndex;
  }

  function handleSubmit() {
    if (!name.trim()) return;
    onSave({
      name: name.trim(),
      description: description.trim(),
      color,
      icon,
      frequency,
      target_count: targetCount,
      days_bitmask: frequency === 'custom_days' ? daysMask : null,
      stack_hint: stackHint.trim()
    });
  }
</script>

<Modal
  title={habit ? 'Gewohnheit bearbeiten' : 'Neue Gewohnheit erstellen'}
  subtitle="Definiere Rhythmus, visuelle Kennzeichnung und Auslöser"
  icon="check_circle"
  size="md"
  bind:open
  onclose={onClose}
>
  <form
    onsubmit={(e) => {
      e.preventDefault();
      handleSubmit();
    }}
    class="space-y-4 text-xs"
  >
    <Input
      label="Name der Gewohnheit"
      name="name"
      bind:value={name}
      required
      placeholder="z. B. Morgen-Dehnung, 2L Wasser trinken..."
    />

    <Input
      label="Beschreibung (optional)"
      name="description"
      bind:value={description}
      placeholder="z. B. 10 Minuten Mobilisation nach dem Aufstehen"
    />

    <div>
      <span class="mb-1.5 block text-xs font-bold text-[var(--text-main)]">Farbe</span>
      <div class="flex flex-wrap gap-2">
        {#each colors as c}
          <button
            type="button"
            class="h-8 w-8 cursor-pointer rounded-full border-2 transition-all"
            class:border-transparent={color !== c}
            class:border-[var(--text-main)]={color === c}
            class:ring-2={color === c}
            class:ring-[var(--color-primary)]={color === c}
            style="background-color: {resolveColor(c)}"
            aria-label={c}
            onclick={() => (color = c)}
          ></button>
        {/each}
      </div>
    </div>

    <div>
      <span class="mb-1.5 block text-xs font-bold text-[var(--text-main)]">Icon</span>
      <div class="flex flex-wrap gap-1.5">
        {#each icons as ico}
          <button
            type="button"
            class="flex h-9 w-9 cursor-pointer items-center justify-center rounded-xl border transition-all {icon ===
            ico
              ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10 text-[var(--color-primary)]'
              : 'border-[var(--border-subtle)] bg-[var(--bg-surface-0)] text-[var(--text-muted)]'}"
            onclick={() => (icon = ico)}
          >
            <Icon name={ico} size="sm" />
          </button>
        {/each}
      </div>
    </div>

    <Select label="Häufigkeit" options={frequencyOptions} bind:value={frequency} />

    {#if frequency === 'weekly_n'}
      <Input
        label="Häufigkeit pro Woche"
        name="target_count"
        type="number"
        min={1}
        max={7}
        bind:value={targetCount}
      />
    {/if}

    {#if frequency === 'custom_days'}
      <div>
        <span class="mb-1.5 block text-xs font-bold text-[var(--text-main)]">Aktive Tage</span>
        <div class="flex gap-1.5">
          {#each dayLabels as label, i}
            <button
              type="button"
              class="h-9 w-9 cursor-pointer rounded-xl text-xs font-bold transition-all"
              class:bg-[var(--color-primary)]={((daysMask >> i) & 1) === 1}
              class:text-white={((daysMask >> i) & 1) === 1}
              class:bg-[var(--bg-surface-50)]={((daysMask >> i) & 1) === 0}
              class:text-[var(--text-muted)]={((daysMask >> i) & 1) === 0}
              class:border={((daysMask >> i) & 1) === 0}
              class:border-[var(--border-subtle)]={((daysMask >> i) & 1) === 0}
              onclick={() => toggleDay(i)}>{label}</button
            >
          {/each}
        </div>
      </div>
    {/if}

    <Input
      label="Habit-Stacking Hinweis (optional)"
      name="stack_hint"
      bind:value={stackHint}
      placeholder="z. B. Direkt nach dem Zähneputzen"
    />

    <div class="flex justify-end gap-2 border-t border-[var(--border-subtle)] pt-3">
      <Btn variant="secondary" size="md" onclick={onClose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" loading={saving} type="submit" disabled={!name.trim()}>
        {habit ? 'Speichern' : 'Gewohnheit anlegen'}
      </Btn>
    </div>
  </form>
</Modal>
