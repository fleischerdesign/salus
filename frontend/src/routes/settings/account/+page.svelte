<script lang="ts">
  import { auth } from '$stores/auth.svelte';
  import { setLocaleState } from '$lib/api/headers';
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { mutate } from '$lib/db/mutate';
  import { mutateDomain } from '$lib/db/mutate-domain';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import RadioGroup from '$components/ui/RadioGroup.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Avatar from '$components/ui/Avatar.svelte';

  let userProfiles = liveQuery(() => db.user_profile.toArray());
  let apiTokens = liveQuery(() =>
    db.api_token.toArray().then((arr) => arr.filter((t) => t.is_active !== false))
  );

  let currentPassword = $state('');
  let newPassword = $state('');
  let pwError = $state('');
  let pwSuccess = $state('');
  let changing = $state(false);

  let theme = $state('system');
  let locale = $state('en');
  let tokenLabel = $state('');
  let tokenCreating = $state(false);
  let newToken = $state('');
  let error = $state('');
  let success = $state('');

  const themeOptions = [
    { value: 'system', label: 'System' },
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' }
  ];

  const localeOptions = [
    { value: 'en', label: 'English' },
    { value: 'de', label: 'German' }
  ];

  let userProfile = $derived($userProfiles && $userProfiles.length > 0 ? $userProfiles[0] : null);

  $effect(() => {
    if (userProfile) {
      theme = userProfile.theme || 'system';
      locale = userProfile.locale || 'en';
    }
  });

  async function changePassword(e: SubmitEvent) {
    e.preventDefault();
    pwError = '';
    pwSuccess = '';
    changing = true;
    const resp = await mutateDomain({
      url: '/api/v1/settings/password',
      method: 'POST',
      body: { current_password: currentPassword, new_password: newPassword }
    });
    changing = false;
    if (!resp.ok) {
      pwError = resp.error ?? 'Request failed';
      return;
    }
    pwSuccess = 'Password changed.';
    currentPassword = '';
    newPassword = '';
  }

  async function createToken(e: SubmitEvent) {
    e.preventDefault();
    tokenCreating = true;
    const resp = await mutateDomain({
      url: '/api/v1/settings/tokens',
      method: 'POST',
      body: { label: tokenLabel },
      responseTable: 'api_token'
    });
    tokenCreating = false;
    if (!resp.ok) return;
    newToken = (resp.data as { token: string }).token;
    tokenLabel = '';
  }

  async function revokeToken(id: number) {
    if (!confirm('Revoke this API token?')) return;
    const token = await db.api_token.get(id);
    if (!token) return;
    await mutate({
      table: 'api_token',
      type: 'update',
      realId: id,
      data: { is_active: false },
      optimistic: { ...token, is_active: false }
    });
  }

  async function setTheme(t: string) {
    theme = t;
    document.documentElement.setAttribute('data-theme', t);
    if (userProfile) {
      await mutate({
        table: 'user',
        type: 'update',
        realId: userProfile.id,
        data: { theme: t },
        optimistic: { ...userProfile, theme: t }
      });
    }
  }

  async function setLocale(loc: string) {
    locale = loc;
    setLocaleState(loc);
    if (userProfile) {
      await mutate({
        table: 'user',
        type: 'update',
        realId: userProfile.id,
        data: { locale: loc },
        optimistic: { ...userProfile, locale: loc }
      });
    }
  }
</script>

{#if $userProfiles === undefined}
  <div class="flex justify-center py-12"><Spinner /></div>
{:else}
  {#if error}<AlertBanner variant="error" class="mb-4">{error}</AlertBanner>{/if}
  {#if success}<AlertBanner variant="success" class="mb-4">{success}</AlertBanner>{/if}

  <div class="space-y-6">
    <!-- Profile -->
    <Card>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Profile</span>
      {/snippet}
      <div class="flex items-center gap-4">
        <Avatar name={auth.user?.display_name || auth.user?.username || '?'} size="lg" />
        <div>
          <p class="text-base font-semibold text-surface-900">
            {auth.user?.display_name || auth.user?.username}
          </p>
          {#if auth.user?.email}
            <p class="text-sm text-surface-500">{auth.user.email}</p>
          {:else}
            <p class="text-sm text-surface-400">No email set</p>
          {/if}
        </div>
      </div>
    </Card>

    <!-- Appearance -->
    <Card>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Appearance</span>
      {/snippet}
      <div class="space-y-5">
        <div>
          <p class="mb-2 text-xs font-semibold tracking-wider text-surface-400 uppercase">Theme</p>
          <RadioGroup name="theme" options={themeOptions} value={theme} onchange={setTheme} />
        </div>
        <div class="border-t border-surface-100 pt-5">
          <p class="mb-2 text-xs font-semibold tracking-wider text-surface-400 uppercase">
            Language
          </p>
          <RadioGroup name="locale" options={localeOptions} value={locale} onchange={setLocale} />
        </div>
      </div>
    </Card>

    <!-- Connected Accounts -->
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Connected Accounts</span>
      {/snippet}
      <div class="divide-y divide-surface-100">
        <div class="flex items-center justify-between px-5 py-3">
          <span class="text-sm text-surface-500">Google</span>
          <Btn variant="secondary" size="sm" href="/api/v1/auth/oidc/google/login">Connect</Btn>
        </div>
        <div class="flex items-center justify-between px-5 py-3">
          <span class="text-sm text-surface-500">GitHub</span>
          <Btn variant="secondary" size="sm" href="/api/v1/auth/oidc/github/login">Connect</Btn>
        </div>
        <div class="flex items-center justify-between px-5 py-3">
          <span class="text-sm text-surface-500">OIDC</span>
          <Btn variant="secondary" size="sm" href="/api/v1/auth/oidc/oidc/login">Connect</Btn>
        </div>
      </div>
    </Card>

    <!-- API Tokens -->
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">API Tokens</span>
      {/snippet}
      <div class="space-y-3 p-5">
        <form onsubmit={createToken} class="flex items-end gap-3">
          <div class="flex-1">
            <FormField label="Token Label">
              <Input name="label" bind:value={tokenLabel} placeholder="e.g. My App" />
            </FormField>
          </div>
          <Btn variant="primary" type="submit" size="sm" loading={tokenCreating}>Generate</Btn>
        </form>

        {#if newToken}
          <AlertBanner variant="warning">Copy this token now — it won't be shown again.</AlertBanner
          >
          <div
            class="flex items-center gap-2 rounded-lg border border-surface-200 bg-surface-50 p-3"
          >
            <code class="flex-1 text-xs font-medium break-all text-surface-700">{newToken}</code>
            <Btn
              variant="secondary"
              size="sm"
              onclick={() => navigator.clipboard.writeText(newToken)}>Copy</Btn
            >
          </div>
        {/if}

        {#if $apiTokens && $apiTokens.filter((t) => t.is_active).length > 0}
          <div class="border-t border-surface-100 pt-3">
            <p class="mb-2 text-xs font-semibold tracking-wider text-surface-400 uppercase">
              Active Tokens
            </p>
            <div class="space-y-2">
              {#each $apiTokens.filter((t) => t.is_active) as t}
                <div
                  class="flex items-center justify-between rounded-lg border border-surface-200 px-3 py-2"
                >
                  <div>
                    <p class="text-sm font-medium text-surface-700">{t.label}</p>
                    <p class="text-xs text-surface-400">
                      {t.token_prefix}…
                      {#if t.last_used_at}
                        · Last used {new Date(t.last_used_at).toLocaleDateString()}{/if}
                    </p>
                  </div>
                  <button
                    type="button"
                    class="rounded px-2 py-1 text-xs font-medium text-error-600 transition-colors duration-150 hover:bg-error-50"
                    onclick={() => revokeToken(t.id)}>Revoke</button
                  >
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </Card>

    <!-- Connected Sources -->
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Connected Sources</span>
      {/snippet}
      <div class="divide-y divide-surface-100">
        <div class="flex items-center justify-between px-5 py-3">
          <span class="text-sm text-surface-700">Samsung Health</span>
          <Badge variant="success">Active</Badge>
        </div>
        <div class="flex items-center justify-between px-5 py-3">
          <span class="text-sm text-surface-700">Apple Health</span>
          <Badge variant="default">Available</Badge>
        </div>
        <div class="flex items-center justify-between px-5 py-3">
          <span class="text-sm text-surface-700">Oura Ring</span>
          <Badge variant="default">Available</Badge>
        </div>
      </div>
    </Card>

    <!-- Change Password -->
    {#if auth.user}
      <Card>
        {#snippet header()}
          <span class="text-sm font-semibold text-surface-900">Change Password</span>
        {/snippet}
        <form onsubmit={changePassword} class="flex max-w-sm flex-col gap-4">
          <input
            type="text"
            name="username"
            value={auth.user.username ?? ''}
            autocomplete="username"
            hidden
          />
          <FormField label="Current Password">
            <Input
              name="current"
              type="password"
              bind:value={currentPassword}
              required
              autocomplete="current-password"
            />
          </FormField>
          <FormField label="New Password">
            <Input
              name="new"
              type="password"
              bind:value={newPassword}
              required
              minlength={6}
              autocomplete="new-password"
            />
          </FormField>
          {#if pwError}<AlertBanner variant="error">{pwError}</AlertBanner>{/if}
          {#if pwSuccess}<AlertBanner variant="success">{pwSuccess}</AlertBanner>{/if}
          <Btn variant="primary" type="submit" loading={changing}>Change Password</Btn>
        </form>
      </Card>
    {/if}
  </div>
{/if}
