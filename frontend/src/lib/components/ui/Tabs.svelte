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
  <nav class="flex w-60 shrink-0 flex-col border-r border-surface-200 py-2 {extraClass}">
    {#each tabs as tab}
      {@const isActive = activeTab === tab.key}
      <button
        role="tab"
        aria-selected={isActive}
        class="flex cursor-pointer items-center gap-3 border-l-[3px] px-4 py-3 text-left text-[13px] font-semibold tracking-[0.05em] transition-colors duration-150 {isActive
          ? 'border-primary-500 bg-primary-50 text-primary-600 hover:bg-primary-100'
          : 'border-transparent text-surface-600 hover:bg-surface-100'}"
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
  <div class="flex overflow-x-auto border-b border-surface-200 {extraClass}" role="tablist">
    {#each tabs as tab}
      {@const isActive = activeTab === tab.key}
      <button
        role="tab"
        aria-selected={isActive}
        class="flex min-w-[90px] cursor-pointer items-center justify-center gap-2 border-b-2 px-4 py-3 text-[13px] font-semibold tracking-[0.05em] transition-colors duration-150 {isActive
          ? 'border-primary-500 text-primary-600'
          : 'border-transparent text-surface-600 hover:bg-surface-100'}"
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
