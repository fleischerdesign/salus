<script lang="ts">
  import { type Snippet } from 'svelte';
  import { fly } from 'svelte/transition';
  import { DURATIONS, motionParams } from '$lib/utils/motion';
  import Icon from './Icon.svelte';

  export interface MenuItem {
    label: string;
    icon?: string;
    variant?: 'default' | 'danger';
    onclick?: () => void;
  }

  interface Props {
    items?: MenuItem[];
    triggerIcon?: string;
    triggerLabel?: string;
    children?: Snippet;
    align?: 'left' | 'right';
    class?: string;
  }

  let {
    items = [],
    triggerIcon = 'more-vert',
    triggerLabel = 'More actions',
    children,
    align = 'right',
    class: extraClass = ''
  }: Props = $props();

  let open = $state(false);
  let containerEl: HTMLDivElement | null = $state(null);

  function toggle() {
    open = !open;
  }

  function close() {
    open = false;
  }

  function handleItemClick(item: MenuItem) {
    close();
    item.onclick?.();
  }

  function handleOutsideClick(e: MouseEvent) {
    if (containerEl && !containerEl.contains(e.target as Node)) {
      close();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') close();
  }

  $effect(() => {
    if (open) {
      document.addEventListener('click', handleOutsideClick);
      document.addEventListener('keydown', handleKeydown);
      return () => {
        document.removeEventListener('click', handleOutsideClick);
        document.removeEventListener('keydown', handleKeydown);
      };
    }
  });
</script>

<div class="relative {extraClass}" bind:this={containerEl}>
  <button
    type="button"
    class="duration-micro flex h-8 w-8 items-center justify-center rounded-md text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700 focus:ring-2 focus:ring-primary-200 focus:outline-none"
    aria-label={triggerLabel}
    aria-haspopup="menu"
    aria-expanded={open}
    onclick={toggle}
  >
    <Icon name={triggerIcon} size="sm" />
  </button>

  {#if open}
    <div
      class="absolute top-full z-50 mt-1 min-w-[180px] overflow-hidden rounded-lg border border-surface-200 bg-surface-0 py-1 shadow-lg {align ===
      'right'
        ? 'right-0'
        : 'left-0'}"
      transition:fly={{ y: -4, ...motionParams(DURATIONS.micro) }}
      role="menu"
    >
      {#if children}
        {@render children()}
      {:else}
        {#each items as item, i}
          <button
            type="button"
            class="duration-micro flex w-full items-center gap-2.5 px-3 py-2 text-left text-sm transition-colors hover:bg-surface-50 {item.variant ===
            'danger'
              ? 'text-error-600 hover:bg-error-50'
              : 'text-surface-700'}"
            role="menuitem"
            onclick={() => handleItemClick(item)}
          >
            {#if item.icon}
              <Icon
                name={item.icon}
                size="sm"
                class={item.variant === 'danger' ? 'text-error-500' : 'text-surface-400'}
              />
            {/if}
            <span>{item.label}</span>
          </button>
        {/each}
      {/if}
    </div>
  {/if}
</div>
