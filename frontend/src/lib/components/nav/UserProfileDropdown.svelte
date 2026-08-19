<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  let { onnavigate, onopenonboarding, onclose } = $props<{
    onnavigate: (path: string) => void;
    onopenonboarding: () => void;
    onclose: () => void;
  }>();

  const userProfilesQuery = useQuery(() => db.user_profile.toArray());
  const userProfiles = $derived(userProfilesQuery.value);
  let userProfile = $derived(
    userProfiles && (userProfiles ?? []).length > 0 ? userProfiles[0] : null
  );

  let displayName = $derived(
    userProfile?.display_name || userProfile?.username || 'Philipp Fleischer'
  );
  let email = $derived(userProfile?.email || 'philipp@salus.local');
  let initial = $derived(displayName.charAt(0).toUpperCase());

  function select(path: string) {
    onnavigate(path);
    onclose();
  }
</script>

<div
  class="glass-panel animate-slide-down w-64 space-y-1 rounded-3xl p-2 text-xs text-text-main shadow-2xl"
>
  <!-- User Profile Header -->
  <div
    class="flex items-center gap-3 rounded-2xl border border-border-subtle/70 bg-surface-50/50 p-3"
  >
    <div
      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-tr from-primary to-activity text-sm font-extrabold text-white shadow-xs"
    >
      {initial}
    </div>
    <div class="flex-1 overflow-hidden">
      <span class="block truncate text-sm font-extrabold text-text-main">{displayName}</span>
      <span class="block truncate text-[0.6875rem] text-text-muted">{email}</span>
    </div>
  </div>

  <!-- Navigation Action Items -->
  <div class="space-y-0.5 pt-1">
    <button
      type="button"
      onclick={() => select('/settings')}
      class="flex w-full cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-left text-xs font-semibold text-text-main transition-colors hover:bg-surface-50/80"
    >
      <Icon name="settings" size="sm" class="text-primary opacity-80" />
      <span class="flex-1">Einstellungen</span>
    </button>

    {#if userProfile?.is_admin}
      <button
        type="button"
        onclick={() => select('/admin')}
        class="flex w-full cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-left text-xs font-semibold text-text-main transition-colors hover:bg-surface-50/80"
      >
        <Icon name="admin_panel_settings" size="sm" class="text-vital opacity-80" />
        <span class="flex-1">Administration</span>
      </button>
    {/if}

    <button
      type="button"
      onclick={() => {
        onopenonboarding();
        onclose();
      }}
      class="flex w-full cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-left text-xs font-semibold text-text-main transition-colors hover:bg-surface-50/80"
    >
      <Icon name="auto_awesome" size="sm" class="text-circadian opacity-80" />
      <span class="flex-1">Einführung und Tour</span>
    </button>
  </div>
</div>
