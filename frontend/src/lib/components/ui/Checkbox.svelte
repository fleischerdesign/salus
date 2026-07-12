<script lang="ts">
  interface Props {
    name: string;
    label: string;
    checked?: boolean;
    class?: string;
  }

  let { name, label, checked = $bindable(false), class: extraClass = '' }: Props = $props();
</script>

<label class="inline-flex cursor-pointer items-center {extraClass}">
  <input
    type="checkbox"
    {name}
    bind:checked
    class="h-4 w-4 rounded border-surface-300 accent-primary-600"
  />
  <span class="ml-2 text-sm text-surface-700">{label}</span>
</label>
