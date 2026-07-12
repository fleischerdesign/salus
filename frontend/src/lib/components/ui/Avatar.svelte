<script lang="ts">
  interface Props {
    name?: string;
    src?: string;
    size?: 'sm' | 'md' | 'lg';
    interactive?: boolean;
    class?: string;
  }

  let {
    name = '?',
    src,
    size = 'md',
    interactive = false,
    class: extraClass = ''
  }: Props = $props();

  const sizeClasses: Record<string, string> = {
    sm: 'h-9 w-9 text-[13px]',
    md: 'h-10 w-10 text-base',
    lg: 'h-12 w-12 text-xl'
  };

  let initial = $derived(name[0]?.toUpperCase() ?? '?');

  let interactiveClass = $derived(interactive ? 'cursor-pointer hover:opacity-85' : '');
</script>

{#if src}
  <img
    {src}
    alt={name}
    class="inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full object-cover {sizeClasses[
      size
    ]} {interactiveClass} {extraClass}"
  />
{:else}
  <span
    class="inline-flex shrink-0 items-center justify-center rounded-full bg-primary-500 font-semibold text-white uppercase {sizeClasses[
      size
    ]} {interactiveClass} {extraClass}"
  >
    {initial}
  </span>
{/if}
