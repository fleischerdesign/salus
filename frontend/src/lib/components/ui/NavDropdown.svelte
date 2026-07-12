<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';
  import { page } from '$app/stores';

  interface Item {
    href: string;
    icon: string;
    label: string;
    external?: boolean;
    highlight?: boolean;
  }

  interface Props {
    label: string;
    items: Item[];
    children?: Snippet;
  }

  let { label, items, children }: Props = $props();

  let open = $state(false);
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  function show() {
    if (timeoutId) { clearTimeout(timeoutId); timeoutId = null; }
    open = true;
  }

  function hide() {
    timeoutId = setTimeout(() => { open = false; }, 150);
  }

  let isActive = $derived(items.some(item => {
    const p = $page.url.pathname;
    return p === item.href || p.startsWith(item.href + '/');
  }));

  let hasHighlight = $derived(items.some(item => item.highlight));

  let triggerClass = $derived(
    'flex h-16 items-center gap-1 border-b-2 px-4 text-[13px] font-semibold tracking-[0.05em] transition-colors duration-150 ' +
    (isActive
      ? 'border-primary-500 text-primary-600'
      : open
        ? 'border-transparent text-primary-600'
        : 'border-transparent text-surface-600 hover:text-primary-600')
  );

  let chevronClass = $derived('transition-transform duration-150 ' +
    (open ? 'rotate-180' : '')
  );

  let menuClass = $derived('absolute left-0 top-full mt-1 min-w-[180px] rounded-lg border border-surface-200 bg-surface-0 shadow-lg z-50 transition-all duration-150 ' +
    (open ? 'opacity-100 pointer-events-auto translate-y-0' : 'opacity-0 pointer-events-none -translate-y-1')
  );
</script>

<div class="relative" onmouseenter={show} onmouseleave={hide} onfocusin={show} onfocusout={hide} role="presentation">
  <button class={triggerClass} aria-expanded={open} aria-haspopup="true" type="button">
    {label}
    {#if hasHighlight}
      <span class="ml-0.5 inline-block h-2 w-2 rounded-full bg-success-500 animate-pulse"></span>
    {/if}
    <Icon name="expand-more" size="sm" class={chevronClass} />
  </button>
  <div class={menuClass}>
    {#if children}
      {@render children()}
    {:else if items.length > 0}
      {#each items as item}
        {@const active = $page.url.pathname === item.href || $page.url.pathname.startsWith(item.href + '/')}
        <a
          href={item.href}
          class="flex items-center gap-3 px-4 py-2.5 text-[13px] font-semibold tracking-[0.05em] no-underline transition-colors duration-150 hover:bg-surface-50 {item.highlight ? 'text-success-600' : active ? 'text-primary-600' : 'text-surface-700'}"
          aria-current={active ? 'page' : undefined}
        >
          {#if item.highlight}
            <span class="inline-block h-2 w-2 shrink-0 rounded-full bg-success-500 animate-pulse"></span>
          {/if}
          <Icon name={item.icon} size="md" class={item.highlight ? 'text-success-500' : ''} />
          {item.label}
        </a>
      {/each}
    {/if}
  </div>
</div>
