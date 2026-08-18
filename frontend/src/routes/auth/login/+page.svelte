<script lang="ts">
  import { auth, type User } from '$stores/auth.svelte';
  import { authConfig } from '$stores/authConfig.svelte';
  import { rawPost } from '$lib/api/client';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Input from '$components/ui/Input.svelte';
  import { Capacitor } from '@capacitor/core';
  import { getApiBaseUrl, setApiBaseUrl, testServerConnection } from '$lib/api/headers';
  import { userTimezone } from '$lib/utils/timezone';

  let username = $state('');
  let password = $state('');
  let showPassword = $state(false);
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
      serverMessage = { type: 'success', text: 'Server erfolgreich verbunden!' };
      authConfig.load();
    } else {
      serverMessage = { type: 'error', text: testRes.message };
    }
  }

  const PROVIDER_METADATA: Record<string, { label: string; icon: string; path: string }> = {
    google: {
      label: 'Mit Google anmelden',
      icon: 'login',
      path: '/api/v1/auth/oidc/google/login'
    },
    github: {
      label: 'Mit GitHub anmelden',
      icon: 'login',
      path: '/api/v1/auth/oidc/github/login'
    },
    oidc: {
      label: 'Mit OIDC anmelden',
      icon: 'login',
      path: '/api/v1/auth/oidc/oidc/login'
    }
  };

  function getProviderMetadata(name: string) {
    return (
      PROVIDER_METADATA[name] || {
        label: `Mit ${name.toUpperCase()} anmelden`,
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
      error = errData.detail || 'Anmeldung fehlgeschlagen. Bitte Zugangsdaten prüfen.';
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
  <title>Salus — Anmelden</title>
</svelte:head>

<div class="flex min-h-[85vh] items-center justify-center px-4 py-10">
  <div class="w-full max-w-md space-y-6">
    <!-- Brand Card Container -->
    <div
      class="space-y-6 rounded-3xl border border-[var(--border-subtle)] bg-[var(--glass-dock-bg)] p-6 shadow-2xl backdrop-blur-2xl sm:p-8"
    >
      <!-- Brand Header -->
      <div class="space-y-2 text-center">
        <div
          class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] shadow-xs"
        >
          <Icon name="health-and-safety" size="lg" />
        </div>
        <div>
          <h1 class="text-xl font-black tracking-tight text-[var(--text-main)] sm:text-2xl">
            Willkommen bei Salus
          </h1>
          <p class="mt-0.5 text-xs text-[var(--text-muted)]">
            Melde dich an, um deine Gesundheits- & Trainingsdaten zu synchronisieren.
          </p>
        </div>
      </div>

      <!-- Server Host Settings for Native APK / Decentralized instances -->
      {#if Capacitor.isNativePlatform()}
        <div
          class="space-y-2.5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-3.5"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 overflow-hidden">
              <Icon name="dns" size="sm" class="shrink-0 text-[var(--text-muted)]" />
              <span class="truncate text-xs font-semibold text-[var(--text-main)]">
                {getApiBaseUrl() || 'Kein Server verbunden'}
              </span>
            </div>
            <button
              type="button"
              class="shrink-0 cursor-pointer text-xs font-bold text-[var(--color-primary)] hover:underline"
              onclick={() => (showServerConfig = !showServerConfig)}
            >
              {showServerConfig ? 'Schließen' : 'Server ändern'}
            </button>
          </div>

          {#if showServerConfig}
            <div class="space-y-2 border-t border-[var(--border-subtle)] pt-2">
              {#if serverMessage}
                <div
                  class="flex items-center gap-2 rounded-xl p-2.5 text-xs font-semibold {serverMessage.type ===
                  'success'
                    ? 'border border-emerald-500/20 bg-emerald-500/10 text-emerald-600'
                    : 'border border-rose-500/20 bg-rose-500/10 text-rose-600'}"
                >
                  <Icon
                    name={serverMessage.type === 'success' ? 'check-circle' : 'error'}
                    size="sm"
                  />
                  <span>{serverMessage.text}</span>
                </div>
              {/if}
              <Input
                name="serverUrl"
                placeholder="https://salus.meine-domain.de"
                bind:value={serverUrl}
              />
              <button
                type="button"
                disabled={serverTesting}
                onclick={handleSaveServerUrl}
                class="w-full cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] py-2 text-xs font-bold text-[var(--text-main)] transition-all hover:bg-[var(--bg-surface-50)] disabled:opacity-50"
              >
                {serverTesting ? 'Verbindung wird geprüft...' : 'Verbindung prüfen & speichern'}
              </button>
            </div>
          {/if}
        </div>
      {/if}

      <!-- Error Banner -->
      {#if error}
        <div
          class="flex items-center gap-2.5 rounded-2xl border border-rose-500/20 bg-rose-500/10 p-3.5 text-xs font-semibold text-rose-600"
        >
          <Icon name="error" size="sm" class="shrink-0" />
          <span>{error}</span>
        </div>
      {/if}

      <!-- Login Form using Input Component -->
      <form onsubmit={login} class="space-y-4">
        <!-- Username Input -->
        <Input
          name="username"
          label="Benutzername"
          icon="person"
          bind:value={username}
          autocomplete="username"
          required
          placeholder="z. B. philipp"
        />

        <!-- Password Input with Show/Hide Toggle -->
        <Input
          name="password"
          label="Passwort"
          icon="lock"
          type={showPassword ? 'text' : 'password'}
          bind:value={password}
          autocomplete="current-password"
          required
          placeholder="••••••••"
        >
          {#snippet trailing()}
            <button
              type="button"
              onclick={() => (showPassword = !showPassword)}
              class="cursor-pointer p-1 text-[var(--text-muted)] transition-colors hover:text-[var(--text-main)]"
              title={showPassword ? 'Passwort verbergen' : 'Passwort anzeigen'}
              aria-label={showPassword ? 'Passwort verbergen' : 'Passwort anzeigen'}
            >
              {#if showPassword}
                <Icon name="visibility-off" size="sm" />
              {:else}
                <Icon name="visibility" size="sm" />
              {/if}
            </button>
          {/snippet}
        </Input>

        <!-- Submit Button -->
        <button
          type="submit"
          disabled={loading}
          class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl bg-[var(--color-primary)] py-3 text-sm font-bold text-white shadow-md transition-all hover:opacity-90 active:scale-[0.99] disabled:opacity-50"
        >
          {#if loading}
            <Icon name="progress-activity" size="sm" class="animate-spin" />
            <span>Anmelden...</span>
          {:else}
            <span>Anmelden</span>
          {/if}
        </button>
      </form>

      <!-- OIDC / SSO Providers -->
      {#if authConfig.oidcProviders.length > 0}
        <div class="space-y-3 pt-2">
          <div class="relative flex items-center justify-center">
            <div class="w-full border-t border-[var(--border-subtle)]"></div>
            <span
              class="absolute bg-[var(--glass-dock-bg)] px-3 text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase"
            >
              oder
            </span>
          </div>

          <div class="flex flex-col gap-2 pt-2">
            {#each authConfig.oidcProviders as provider}
              {@const meta = getProviderMetadata(provider)}
              <button
                type="button"
                onclick={() => (window.location.href = `${meta.path}?tz=${userTimezone()}`)}
                class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] py-2.5 text-xs font-bold text-[var(--text-main)] shadow-2xs transition-all hover:bg-[var(--bg-surface-50)]"
              >
                <Icon name={meta.icon} size="sm" />
                <span>{meta.label}</span>
              </button>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Local Offline Mode Section -->
      <div class="border-t border-[var(--border-subtle)] pt-4">
        <div
          class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4"
        >
          <div class="flex items-center gap-2">
            <div
              class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[var(--color-primary)]/10 text-[var(--color-primary)]"
            >
              <Icon name="devices" size="sm" />
            </div>
            <div>
              <span class="block text-xs font-bold text-[var(--text-main)]">Ohne Server nutzen</span
              >
              <span class="text-[0.6875rem] text-[var(--text-muted)]"
                >Vollständig offline in deinem Browser (Local-First)</span
              >
            </div>
          </div>

          <div class="flex items-center gap-2">
            <div class="flex-1">
              <Input
                name="localName"
                placeholder="Dein Name (z. B. Philipp)"
                bind:value={localName}
              />
            </div>
            <button
              type="button"
              onclick={startLocal}
              class="h-10 shrink-0 cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] px-4 text-xs font-bold text-[var(--text-main)] shadow-2xs transition-all hover:bg-[var(--bg-surface-100)]"
            >
              Starten
            </button>
          </div>
        </div>
      </div>

      <!-- Footer Register Link -->
      <div class="pt-2 text-center">
        <p class="text-xs text-[var(--text-muted)]">
          Noch kein Konto?
          <a
            href="/auth/register"
            class="ml-1 font-bold text-[var(--color-primary)] hover:underline"
          >
            Konto erstellen
          </a>
        </p>
      </div>
    </div>
  </div>
</div>
