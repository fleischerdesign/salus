<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  interface Tab {
    key: string;
    label: string;
    icon?: string;
  }

  interface Props {
    tabs: Tab[];
    activeTab: string;
    variant?: 'bar' | 'sidebar';
    onchange?: (key: string) => void;
    class?: string;
  }

  let {
    tabs,
    activeTab = $bindable(''),
    variant = 'bar',
    onchange,
    class: extraClass = ''
  }: Props = $props();

  function selectTab(key: string) {
    activeTab = key;
    onchange?.(key);
  }
</script>

{#if variant === 'sidebar'}
  <nav class="border-surface-200 flex w-60 shrink-0 flex-col border-r py-2 {extraClass}">
    {#each tabs as tab}
      {@const isActive = activeTab === tab.key}
      <button
        role="tab"
        aria-selected={isActive}
        class="duration-micro tracking-label flex cursor-pointer items-center gap-3 border-l-[3px] px-4 py-3 text-left text-xs font-semibold transition-colors {isActive
          ? 'border-primary-500 bg-primary-50 text-primary-600 hover:bg-primary-100'
          : 'text-surface-600 hover:bg-surface-100 border-transparent'}"
        onclick={() => selectTab(tab.key)}
      >
        {#if tab.icon}
          <Icon name={tab.icon} size="md" />
        {/if}
        {tab.label}
      </button>
    {/each}
  </nav>
{:else}
  <div class="border-surface-200 flex overflow-x-auto border-b {extraClass}" role="tablist">
    {#each tabs as tab}
      {@const isActive = activeTab === tab.key}
      <button
        role="tab"
        aria-selected={isActive}
        class="duration-micro tracking-label flex min-w-[90px] cursor-pointer items-center justify-center gap-2 border-b-2 px-4 py-3 text-xs font-semibold transition-colors {isActive
          ? 'border-primary-500 text-primary-600'
          : 'text-surface-600 hover:bg-surface-100 border-transparent'}"
        onclick={() => selectTab(tab.key)}
      >
        {#if tab.icon}
          <Icon name={tab.icon} size="sm" />
        {/if}
        {tab.label}
      </button>
    {/each}
  </div>
{/if}
