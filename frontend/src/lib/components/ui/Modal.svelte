<script lang="ts">
  import { type Snippet } from 'svelte';
  import { fade } from 'svelte/transition';
  import { DURATIONS, EASINGS, motionParams } from '$lib/utils/motion';
  import Icon from '$components/ui/Icon.svelte';
  const sizeVariants = {
    sm: 'max-w-sm',
    md: 'max-w-lg',
    lg: 'max-w-2xl'
  };

  interface Props {
    open?: boolean;
    title?: string;
    size?: keyof typeof sizeVariants;
    children?: Snippet;
    onclose?: () => void;
    class?: string;
  }

  let {
    open = $bindable(false),
    title,
    size = 'md',
    children,
    onclose,
    class: extraClass = ''
  }: Props = $props();

  function close() {
    open = false;
    onclose?.();
  }
  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') close();
  }
  function onBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) close();
  }
</script>

<svelte:window onkeydown={onKeydown} />

{#if open}
  <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
  <div
    class="fixed inset-0 z-500 flex items-center justify-center bg-black/50"
    in:fade={motionParams(DURATIONS.normal, EASINGS.standard)}
    out:fade={motionParams(DURATIONS.fast)}
    onclick={onBackdropClick}
    role="presentation"
  >
    <div
      class="relative z-[501] mx-4 w-full rounded-lg bg-surface-0 shadow-lg {sizeVariants[size]}"
      in:fade={motionParams(DURATIONS.normal, EASINGS.standard)}
      out:fade={motionParams(DURATIONS.fast)}
      role="dialog"
      aria-modal="true"
      aria-label={title ?? 'Dialog'}
    >
      <div class="flex items-center justify-between border-b border-surface-200 px-6 py-3">
        <h2 class="text-sm font-semibold text-surface-900">{title ?? ''}</h2>
        <button
          class="duration-micro flex h-7 w-7 items-center justify-center rounded-full text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-600"
          onclick={close}
          aria-label="Close"
        >
          <Icon name="close" size="md" />
        </button>
      </div>
      <div class="p-6">{@render children?.()}</div>
    </div>
  </div>
{/if}
