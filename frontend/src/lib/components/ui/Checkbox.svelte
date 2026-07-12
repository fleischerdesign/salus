<script lang="ts">
  interface Props {
    name: string;
    label: string;
    checked?: boolean;
    class?: string;
  }

  let {
    name,
    label,
    checked = $bindable(false),
    class: extraClass = ''
  }: Props = $props();
</script>

<label class="inline-flex items-center cursor-pointer {extraClass}">
  <input
    type="checkbox"
    {name}
    bind:checked
    class="h-4 w-4 rounded accent-primary-600 border-surface-300"
  />
  <span class="ml-2 text-sm text-surface-700">{label}</span>
</label>
