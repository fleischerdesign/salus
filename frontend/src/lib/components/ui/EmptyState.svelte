<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    icon?: string;
    title: string;
    description?: string;
    children?: Snippet;
    class?: string;
  }

  let {
    icon = 'inbox',
    title,
    description,
    children,
    class: extraClass = ''
  }: Props = $props();
</script>

<div class="flex flex-col items-center justify-center py-16 px-4 text-center {extraClass}">
  <Icon name={icon} size="2xl" class="text-surface-300" />
  <h3 class="mt-4 text-base font-semibold text-surface-700">{title}</h3>
  {#if description}
    <p class="mt-1 text-sm text-surface-500 max-w-sm">{description}</p>
  {/if}
  {#if children}
    <div class="mt-6">
      {@render children()}
    </div>
  {/if}
</div>
