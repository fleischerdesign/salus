<script lang="ts">
  import { auth } from '$stores/auth.svelte';
  import { rawPost } from '$lib/api/client';
  import Icon from '$components/ui/Icon.svelte';
  import { goto } from '$app/navigation';

  let open = $state(false);
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  function show() {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    open = true;
  }

  function hide() {
    timeoutId = setTimeout(() => {
      open = false;
    }, 150);
  }

  async function handleLogout() {
    await rawPost('/api/v1/auth/logout', {});
    auth.clear();
    await goto('/auth/login');
  }

  let menuClass = $derived(
    'absolute right-0 top-full mt-2 min-w-[200px] rounded-xl border border-surface-200 bg-surface-0 py-1 shadow-lg z-dropdown transition-all duration-micro ' +
      (open
        ? 'opacity-100 pointer-events-auto translate-y-0'
        : 'opacity-0 pointer-events-none -translate-y-1')
  );
</script>

<div class="relative" onmouseenter={show} onmouseleave={hide} role="presentation">
  <button
    class="duration-micro flex items-center gap-2 rounded-full p-1 transition-colors hover:bg-surface-200"
    aria-expanded={open}
    aria-haspopup="true"
    type="button"
  >
    <span
      class="inline-flex h-9 w-9 items-center justify-center rounded-full bg-primary-500 text-[13px] font-semibold text-white uppercase"
    >
      {(auth.user?.display_name || auth.user?.username || 'U')[0]}
    </span>
  </button>
  <div class={menuClass}>
    <div class="border-b border-surface-200 px-4 py-3">
      <span
        class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-primary-500 text-sm font-semibold text-white uppercase"
      >
        {(auth.user?.display_name || auth.user?.username || 'U')[0]}
      </span>
      <div class="mt-2 font-semibold text-surface-900">
        {auth.user?.display_name || auth.user?.username}
      </div>
      {#if auth.user?.email}
        <div class="text-[11px] text-surface-500">{auth.user?.email}</div>
      {/if}
    </div>
    <a
      href="/settings"
      class="duration-micro flex items-center gap-3 px-4 py-2.5 text-[13px] font-semibold tracking-[0.05em] text-surface-700 no-underline transition-colors hover:bg-surface-50"
    >
      <Icon name="settings" size="md" />
      Settings
    </a>
    {#if auth.isAdmin}
      <a
        href="/admin"
        class="duration-micro flex items-center gap-3 px-4 py-2.5 text-[13px] font-semibold tracking-[0.05em] text-surface-700 no-underline transition-colors hover:bg-surface-50"
      >
        <Icon name="admin-panel-settings" size="md" />
        Admin
      </a>
    {/if}
    <hr class="my-1 border-surface-200" />
    <button
      class="duration-micro flex w-full items-center gap-3 px-4 py-2.5 text-[13px] font-semibold tracking-[0.05em] text-error-600 transition-colors hover:bg-surface-50"
      onclick={handleLogout}
    >
      <Icon name="logout" size="md" />
      Logout
    </button>
  </div>
</div>
