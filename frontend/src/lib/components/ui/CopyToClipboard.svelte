<script lang="ts">
  import Icon from './Icon.svelte';

  interface Props {
    value: string;
    label?: string;
    class?: string;
  }

  let { value, label, class: extraClass = '' }: Props = $props();

  let copied = $state(false);
  let timeoutId: ReturnType<typeof setTimeout>;

  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      copied = true;
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => (copied = false), 2000);
    } catch {
      /* clipboard unavailable */
    }
  }
</script>

<div class="flex items-center gap-2 rounded-md bg-surface-100 px-3 py-2 {extraClass}">
  <code class="flex-1 truncate text-sm text-surface-700">{value}</code>
  <button
    type="button"
    class="flex h-7 w-7 items-center justify-center rounded-md text-surface-400 transition-colors duration-150 hover:bg-surface-200 hover:text-surface-600"
    aria-label={copied ? 'Copied' : label ?? 'Copy'}
    onclick={copy}
  >
    <Icon name={copied ? 'check' : 'content-copy'} size="sm" />
  </button>
</div>
