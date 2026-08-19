<script lang="ts">
  import Icon from './Icon.svelte';

  interface Props {
    name?: string;
    accept?: string;
    label?: string;
    hint?: string;
    onfile?: (file: File) => void;
    class?: string;
  }

  let {
    name = 'file',
    accept,
    label = 'Click or drag file to upload',
    hint,
    onfile,
    class: extraClass = ''
  }: Props = $props();

  let isDragging = $state(false);
  let fileName = $state('');

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    isDragging = false;
    const file = e.dataTransfer?.files?.[0];
    if (file) {
      fileName = file.name;
      onfile?.(file);
    }
  }

  function handleChange(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      fileName = file.name;
      onfile?.(file);
    }
  }
</script>

<label
  for={name}
  class="duration-micro flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 text-center transition-colors
    {isDragging
    ? 'border-primary-500 bg-primary-50'
    : 'border-surface-200 hover:border-surface-300 hover:bg-surface-50'} {extraClass}"
  ondragover={(e) => {
    e.preventDefault();
    isDragging = true;
  }}
  ondragleave={() => {
    isDragging = false;
  }}
  ondrop={handleDrop}
>
  <Icon name="upload-file" size="xl" class="text-surface-400" />
  <span class="mt-2 text-sm font-medium text-surface-700">
    {#if fileName}
      {fileName}
    {:else}
      {label}
    {/if}
  </span>
  {#if hint}
    <span class="mt-1 text-xs text-surface-400">{hint}</span>
  {/if}
  <input type="file" id={name} {name} {accept} class="sr-only" onchange={handleChange} />
</label>
