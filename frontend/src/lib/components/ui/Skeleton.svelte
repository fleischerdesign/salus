<script lang="ts">
  interface Props {
    variant?: 'text' | 'title' | 'avatar' | 'card';
    width?: string;
    height?: string;
  }

  let { variant = 'text', width, height }: Props = $props();

  const defaultWidth: Record<string, string> = {
    text: '100%',
    title: '60%',
    avatar: '2.5rem',
    card: '100%'
  };

  const defaultHeight: Record<string, string> = {
    text: '1rem',
    title: '1.5rem',
    avatar: '2.5rem',
    card: '7.5rem'
  };

  let w = $derived(width ?? defaultWidth[variant]);
  let h = $derived(height ?? defaultHeight[variant]);
</script>

<div
  class="animate-pulse rounded-sm bg-surface-200 opacity-60 {variant === 'avatar'
    ? 'rounded-full'
    : ''}"
  style="width: {w}; height: {h};"
></div>
