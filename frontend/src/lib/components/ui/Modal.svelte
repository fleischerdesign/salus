<script lang="ts">
  import { type Snippet } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Icon from '$components/ui/Icon.svelte';

  const sizeVariants: Record<string, string> = {
    sm: 'max-w-sm',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-6xl'
  };

  interface Props {
    open?: boolean;
    title?: string;
    subtitle?: string;
    icon?: string;
    size?: keyof typeof sizeVariants;
    children?: Snippet;
    actions?: Snippet;
    onclose?: () => void;
    class?: string;
  }

  let {
    open = $bindable(false),
    title = '',
    subtitle = '',
    icon = '',
    size = 'md',
    children,
    actions,
    onclose,
    class: extraClass = ''
  }: Props = $props();

  function close() {
    open = false;
    onclose?.();
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && open) {
      close();
    }
  }

  function onBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      close();
    }
  }
</script>

<svelte:window onkeydown={onKeydown} />

{#if open}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
    transition:fade={{ duration: 150 }}
    onclick={onBackdropClick}
    role="presentation"
  >
    <div
      class="relative z-10 max-h-[92vh] w-full space-y-5 overflow-y-auto rounded-3xl border border-[var(--border-subtle)] bg-[var(--glass-dock-bg)] p-6 shadow-2xl backdrop-blur-2xl {sizeVariants[
        size
      ] || sizeVariants.md} {extraClass}"
      transition:scale={{ duration: 150, start: 0.96, easing: cubicOut }}
      role="dialog"
      aria-modal="true"
      aria-label={title || 'Dialog'}
      tabindex="-1"
    >
      <!-- Header -->
      {#if title || icon || subtitle}
        <div class="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
          <div class="flex items-center gap-3">
            {#if icon}
              <div
                class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)]"
              >
                <Icon name={icon} size="sm" />
              </div>
            {/if}
            <div>
              {#if title}
                <h3 class="text-base leading-tight font-extrabold text-[var(--text-main)]">
                  {title}
                </h3>
              {/if}
              {#if subtitle}
                <p class="mt-0.5 text-xs text-[var(--text-muted)]">{subtitle}</p>
              {/if}
            </div>
          </div>

          <button
            type="button"
            onclick={close}
            class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full bg-[var(--bg-surface-50)] text-base text-[var(--text-muted)] transition-colors hover:bg-[var(--bg-surface-100)] hover:text-[var(--text-main)]"
            title="Schließen"
            aria-label="Schließen"
          >
            <Icon name="close" size="sm" />
          </button>
        </div>
      {/if}

      <!-- Body Content -->
      <div class="text-xs text-[var(--text-main)]">
        {@render children?.()}
      </div>

      <!-- Actions Footer -->
      {#if actions}
        <div
          class="flex items-center justify-end gap-2 border-t border-[var(--border-subtle)] pt-3"
        >
          {@render actions()}
        </div>
      {/if}
    </div>
  </div>
{/if}
