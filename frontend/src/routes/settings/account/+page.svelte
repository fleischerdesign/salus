<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$stores/auth.svelte';
  import { authConfig } from '$stores/authConfig.svelte';
  import { setLocaleState } from '$lib/api/headers';
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import {
    changePassword as doChangePassword,
    createToken as doCreateToken,
    revokeToken as doRevokeToken
  } from '$lib/mutations/account';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import RadioGroup from '$components/ui/RadioGroup.svelte';
  import Avatar from '$components/ui/Avatar.svelte';

  const PROVIDER_METADATA: Record<string, { displayName: string; path: string }> = {
    google: {
      displayName: 'Google',
      path: '/api/v1/auth/oidc/google/login'
    },
    github: {
      displayName: 'GitHub',
      path: '/api/v1/auth/oidc/github/login'
    },
    oidc: {
      displayName: 'OIDC',
      path: '/api/v1/auth/oidc/oidc/login'
    }
  };

  function getProviderMetadata(name: string) {
    return (
      PROVIDER_METADATA[name] || {
        displayName: name.toUpperCase(),
        path: `/api/v1/auth/oidc/${name}/login`
      }
    );
  }

  onMount(() => {
    authConfig.load();
  });

  let userProfiles = liveQuery(() => db.user_profile.toArray());
  let apiTokens = liveQuery(() =>
    db.api_token.toArray().then((arr) => arr.filter((t) => t.is_active !== false))
  );

  let currentPassword = $state('');
  let newPassword = $state('');
  let pwError = $state('');
  let pwSuccess = $state('');
  let pwLoading = $state(false);

  let tokenLabel = $state('');
  let newToken = $state('');
  let tokenCreating = $state(false);

  let theme = $state(localStorage.getItem('salus_theme') || 'system');
  let locale = $state(localStorage.getItem('salus_locale') || 'en');

  const themeOptions = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'system', label: 'System' }
  ];

  const localeOptions = [
    { value: 'en', label: 'English' },
    { value: 'de', label: 'Deutsch' },
    { value: 'es', label: 'Español' },
    { value: 'fr', label: 'Français' }
  ];

  function setTheme(val: string) {
    theme = val;
    localStorage.setItem('salus_theme', val);
    if (val === 'dark') document.documentElement.classList.add('dark');
    else if (val === 'light') document.documentElement.classList.remove('dark');
    else {
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  }

  function setLocale(val: string) {
    locale = val;
    localStorage.setItem('salus_locale', val);
    setLocaleState(val);
  }

  async function changePassword(e: SubmitEvent) {
    e.preventDefault();
    pwError = '';
    pwSuccess = '';
    pwLoading = true;

    try {
      await doChangePassword(currentPassword, newPassword);
      pwSuccess = 'Password changed successfully.';
      currentPassword = '';
      newPassword = '';
    } catch (err: unknown) {
      pwError = err instanceof Error ? err.message : 'Failed to change password.';
    } finally {
      pwLoading = false;
    }
  }

  async function createToken(e: SubmitEvent) {
    e.preventDefault();
    if (!tokenLabel.trim()) return;
    tokenCreating = true;
    try {
      const res = (await doCreateToken(tokenLabel)) as {
        token?: string;
        data?: { token?: string };
      };
      const tokenValue = res?.token || res?.data?.token;
      if (tokenValue) {
        newToken = tokenValue;
        tokenLabel = '';
      }
    } catch {
      /* ignore */
    } finally {
      tokenCreating = false;
    }
  }

  async function revokeToken(id: string | number) {
    await doRevokeToken(String(id));
  }
</script>

<div class="space-y-6">
  {#if $userProfiles && $userProfiles.length > 0}
    {@const profile = $userProfiles[0]}
    <!-- User Profile Header -->
    <div class="flex items-center gap-4 rounded-xl border border-surface-200 bg-surface-0 p-5">
      <Avatar name={profile.display_name || auth.user?.username} size="lg" />
      <div>
        <h3 class="text-base font-semibold text-surface-900">
          {profile.display_name || auth.user?.username || 'User'}
        </h3>
        <p class="font-mono text-xs text-surface-500">@{auth.user?.username || 'user'}</p>
        {#if auth.user?.email}
          <p class="text-xs text-surface-400">{auth.user.email}</p>
        {/if}
      </div>
    </div>
  {/if}

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
    <!-- User Preferences (Language) -->
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Language</span>
      {/snippet}
      <div class="p-5">
        <p class="mb-2 text-xs font-semibold tracking-wider text-surface-400 uppercase">
          Preferred Language
        </p>
        <RadioGroup name="locale" options={localeOptions} value={locale} onchange={setLocale} />
      </div>
    </Card>

    <!-- Connected Accounts -->
    {#if authConfig.oidcProviders.length > 0}
      <Card padding={false}>
        {#snippet header()}
          <span class="text-sm font-semibold text-surface-900">Connected Accounts</span>
        {/snippet}
        <div class="divide-y divide-surface-100">
          {#each authConfig.oidcProviders as provider}
            {@const meta = getProviderMetadata(provider)}
            <div class="flex items-center justify-between px-5 py-3">
              <span class="text-sm text-surface-500">{meta.displayName}</span>
              <Btn variant="secondary" size="sm" href={meta.path}>Connect</Btn>
            </div>
          {/each}
        </div>
      </Card>
    {/if}

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
                    class="duration-micro cursor-pointer rounded px-2 py-1 text-xs font-medium text-error-600 transition-colors hover:bg-error-50"
                    onclick={() => revokeToken(String(t.id))}>Revoke</button
                  >
                </div>
              {/each}
            </div>
          </div>
        {/if}
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
            class="hidden"
            tabindex="-1"
            aria-hidden="true"
          />
          <FormField label="Current Password">
            <Input
              name="current-password"
              type="password"
              bind:value={currentPassword}
              autocomplete="current-password"
              required
            />
          </FormField>
          <FormField label="New Password">
            <Input
              name="new-password"
              type="password"
              bind:value={newPassword}
              autocomplete="new-password"
              required
            />
          </FormField>
          {#if pwError}
            <AlertBanner variant="error">{pwError}</AlertBanner>
          {/if}
          {#if pwSuccess}
            <AlertBanner variant="success">{pwSuccess}</AlertBanner>
          {/if}
          <div class="flex justify-end">
            <Btn variant="primary" type="submit" loading={pwLoading}>Update Password</Btn>
          </div>
        </form>
      </Card>
    {/if}
  </div>
</div>
