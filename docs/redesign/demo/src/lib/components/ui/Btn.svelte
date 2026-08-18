<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    variant = 'secondary',
    size = 'md',
    class: className = '',
    onclick,
    children
  } = $props<{
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg' | 'icon';
    class?: string;
    onclick?: (e: MouseEvent) => void;
    children?: Snippet;
  }>();

  const variantClasses = {
    primary: 'bg-[var(--color-primary)] text-white hover:opacity-95 shadow-sm',
    secondary: 'bg-[var(--bg-surface-50)] text-[var(--text-main)] border border-[var(--border-subtle)] hover:bg-[var(--bg-surface-100)]',
    ghost: 'bg-transparent text-[var(--text-muted)] hover:text-[var(--text-main)] hover:bg-[var(--bg-surface-50)]',
    danger: 'bg-[var(--color-vital-soft)] text-[var(--color-vital)] hover:bg-[var(--color-vital)] hover:text-white'
  };

  const sizeClasses = {
    sm: 'px-2.5 py-1 text-xs rounded-[var(--radius-sm)]',
    md: 'px-3.5 py-1.5 text-xs font-semibold rounded-[var(--radius-sm)]',
    lg: 'px-5 py-2.5 text-sm font-semibold rounded-[var(--radius-md)]',
    icon: 'w-8 h-8 p-0 rounded-full flex items-center justify-center'
  };
</script>

<button
  type="button"
  {onclick}
  class="inline-flex items-center justify-center gap-1.5 font-sans font-medium transition-all active:scale-[0.98] cursor-pointer {variantClasses[variant]} {sizeClasses[size]} {className}"
>
  {@render children?.()}
</button>
