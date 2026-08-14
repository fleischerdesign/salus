<script lang="ts">
  import { auth, type User } from '$stores/auth.svelte';
  import { authConfig } from '$stores/authConfig.svelte';
  import { rawPost } from '$lib/api/client';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import Card from '$components/ui/Card.svelte';
  import Input from '$components/ui/Input.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import Divider from '$components/ui/Divider.svelte';
  import Icon from '$components/ui/Icon.svelte';

  import { Capacitor } from '@capacitor/core';
  import { getApiBaseUrl, setApiBaseUrl, testServerConnection } from '$lib/api/headers';

  let username = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  let localName = $state('');

  let showServerConfig = $state(Capacitor.isNativePlatform() && !getApiBaseUrl());
  let serverUrl = $state(getApiBaseUrl() || '');
  let serverTesting = $state(false);
  let serverMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  async function handleSaveServerUrl() {
    serverTesting = true;
    serverMessage = null;
    const testRes = await testServerConnection(serverUrl);
    serverTesting = false;
    if (testRes.success) {
      const saved = setApiBaseUrl(serverUrl);
      serverUrl = saved;
      serverMessage = { type: 'success', text: 'Server host connected!' };
      authConfig.load();
    } else {
      serverMessage = { type: 'error', text: testRes.message };
    }
  }

  const PROVIDER_METADATA: Record<string, { label: string; icon: string; path: string }> = {
    google: {
      label: 'Sign in with Google',
      icon: 'login',
      path: '/api/v1/auth/oidc/google/login'
    },
    github: {
      label: 'Sign in with GitHub',
      icon: 'login',
      path: '/api/v1/auth/oidc/github/login'
    },
    oidc: {
      label: 'Sign in with OIDC',
      icon: 'login',
      path: '/api/v1/auth/oidc/oidc/login'
    }
  };

  function getProviderMetadata(name: string) {
    return (
      PROVIDER_METADATA[name] || {
        label: `Sign in with ${name.toUpperCase()}`,
        icon: 'login',
        path: `/api/v1/auth/oidc/${name}/login`
      }
    );
  }

  onMount(() => {
    if (auth.isAuthenticated) {
      goto('/');
    } else {
      authConfig.load();
    }
  });

  async function login(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    loading = true;

    const res = await rawPost('/api/v1/auth/login', { username, password });
    loading = false;

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      error = errData.detail || 'Login failed';
      return;
    }

    const data = await res.json();
    auth.setSession(data.token, data.user as User);
    await goto('/');
  }

  function startLocal() {
    const name = localName.trim() || 'Lokaler Nutzer';
    auth.setLocalSession(name);
    goto('/');
  }
</script>

<svelte:head>
  <title>Salus — Sign In</title>
</svelte:head>

<div class="flex min-h-[80vh] items-center justify-center">
  <Card variant="elevated">
    <div style="max-width:400px;width:340px">
      <h1 class="mb-2 text-center text-3xl leading-[36px] font-bold text-surface-900">Sign In</h1>
      <p class="mb-8 text-center text-base text-surface-500">Access your health data dashboard</p>

      <!-- Server Host pill/expander for Native APK / Decentralized instances -->
      {#if Capacitor.isNativePlatform()}
        <div class="mb-5 rounded-xl border border-surface-200 bg-surface-50/60 p-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 overflow-hidden">
              <Icon name="dns" size="sm" class="shrink-0 text-surface-400" />
              <span class="truncate text-xs font-medium text-surface-600">
                {getApiBaseUrl() || 'No server connected'}
              </span>
            </div>
            <button
              type="button"
              class="shrink-0 cursor-pointer text-xs font-semibold text-primary-600 hover:text-primary-700"
              onclick={() => (showServerConfig = !showServerConfig)}
            >
              {showServerConfig ? 'Close' : 'Change Host'}
            </button>
          </div>

          {#if showServerConfig}
            <div class="mt-3 space-y-2 border-t border-surface-200/60 pt-3">
              {#if serverMessage}
                <AlertBanner variant={serverMessage.type === 'success' ? 'success' : 'error'}>
                  {serverMessage.text}
                </AlertBanner>
              {/if}
              <Input
                name="serverUrl"
                placeholder="https://salus.my-domain.com"
                bind:value={serverUrl}
              />
              <Btn
                variant="secondary"
                size="sm"
                fullWidth
                loading={serverTesting}
                onclick={handleSaveServerUrl}
              >
                Connect & Verify Server
              </Btn>
            </div>
          {/if}
        </div>
      {/if}

      {#if error}
        <div class="mb-4">
          <AlertBanner variant="error" message={error} />
        </div>
      {/if}

      <form onsubmit={login} class="flex flex-col gap-4">
        <Input
          name="username"
          label="Username"
          bind:value={username}
          autocomplete="username"
          required
        />
        <Input
          name="password"
          type="password"
          label="Password"
          bind:value={password}
          autocomplete="current-password"
          required
        />
        <Btn variant="primary" type="submit" fullWidth {loading}>Sign In</Btn>
      </form>

      {#if authConfig.oidcProviders.length > 0}
        <div class="my-6">
          <Divider label="or" />
        </div>

        <div class="flex flex-col gap-2">
          {#each authConfig.oidcProviders as provider}
            {@const meta = getProviderMetadata(provider)}
            <Btn variant="secondary" fullWidth onclick={() => (window.location.href = meta.path)}>
              <Icon name={meta.icon} />
              {meta.label}
            </Btn>
          {/each}
        </div>
      {/if}

      <div class="my-6">
        <Divider label="ohne Server" />
      </div>

      <div class="flex flex-col gap-2">
        <Input name="localName" label="Dein Name" bind:value={localName} placeholder="Max" />
        <Btn variant="secondary" fullWidth onclick={startLocal}>
          <Icon name="devices" />
          Lokal starten
        </Btn>
        <p class="text-center text-xs text-surface-400">
          Deine Daten bleiben auf diesem Gerät und können verloren gehen. Sichere sie regelmäßig per
          Export (Einstellungen → Lokaler Speicher).
        </p>
      </div>

      <p class="mt-6 text-center text-sm text-surface-500">
        Don't have an account?
        <a href="/auth/register" class="font-medium text-primary-600 hover:text-primary-700"
          >Create one</a
        >
      </p>
    </div>
  </Card>
</div>
