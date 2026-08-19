<script lang="ts">
  import { auth, type User } from '$stores/auth.svelte';
  import { rawPost } from '$lib/api/client';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Input from '$components/ui/Input.svelte';

  let username = $state('');
  let password = $state('');
  let email = $state('');
  let showPassword = $state(false);
  let error = $state('');
  let loading = $state(false);

  onMount(() => {
    if (auth.isAuthenticated) goto('/');
  });

  async function register(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    loading = true;

    const res = await rawPost('/api/v1/auth/register', {
      username,
      password,
      email: email.trim() || undefined,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    });
    const body = await res.json().catch(() => null);
    const data = res.ok ? (body as { token: string; user: Record<string, unknown> }) : null;
    const err = res.ok ? null : (body?.error ?? body?.detail ?? 'Registrierung fehlgeschlagen.');

    loading = false;

    if (err || !data) {
      error = err ?? 'Registrierung fehlgeschlagen.';
      return;
    }

    auth.setSession(data.token, data.user as User);
    await goto('/');
  }
</script>

<svelte:head>
  <title>Salus — Konto erstellen</title>
</svelte:head>

<div class="flex min-h-[85vh] items-center justify-center px-4 py-10">
  <div class="w-full max-w-md space-y-6">
    <!-- Brand Card Container -->
    <div
      class="space-y-6 rounded-3xl border border-border-subtle bg-glass-dock p-6 shadow-2xl backdrop-blur-2xl sm:p-8"
    >
      <!-- Brand Header -->
      <div class="space-y-2 text-center">
        <div
          class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary shadow-xs"
        >
          <Icon name="health-and-safety" size="lg" />
        </div>
        <div>
          <h1 class="text-xl font-black tracking-tight text-text-main sm:text-2xl">
            Konto erstellen
          </h1>
          <p class="mt-0.5 text-xs text-text-muted">
            Erstelle dein persönliches Salus-Konto für verschlüsselte Synchronisation.
          </p>
        </div>
      </div>

      <!-- Error Banner -->
      {#if error}
        <div
          class="flex items-center gap-2.5 rounded-2xl border border-rose-500/20 bg-rose-500/10 p-3.5 text-xs font-semibold text-rose-600"
        >
          <Icon name="error" size="sm" class="shrink-0" />
          <span>{error}</span>
        </div>
      {/if}

      <!-- Register Form using Input Component -->
      <form onsubmit={register} class="space-y-4">
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

        <!-- Email Input (Optional) -->
        <Input
          name="email"
          type="email"
          label="E-Mail (optional)"
          icon="mail"
          bind:value={email}
          autocomplete="email"
          placeholder="name@beispiel.de"
        />

        <!-- Password Input with Show/Hide Toggle -->
        <Input
          name="password"
          label="Passwort"
          icon="lock"
          type={showPassword ? 'text' : 'password'}
          bind:value={password}
          autocomplete="new-password"
          required
          placeholder="••••••••"
        >
          {#snippet trailing()}
            <button
              type="button"
              onclick={() => (showPassword = !showPassword)}
              class="cursor-pointer p-1 text-text-muted transition-colors hover:text-text-main"
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

        <!-- Privacy / Data Sovereignty Note -->
        <div
          class="flex items-start gap-2.5 rounded-2xl border border-border-subtle bg-surface-50 p-3 text-[0.6875rem] text-text-muted"
        >
          <Icon name="shield" size="sm" class="mt-0.5 shrink-0 text-primary" />
          <span
            >Deine Gesundheits- und Trainingsdaten bleiben privat und werden lokal im Browser
            verschlüsselt verarbeitet.</span
          >
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          disabled={loading}
          class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl bg-primary py-3 text-sm font-bold text-white shadow-md transition-all hover:opacity-90 active:scale-[0.99] disabled:opacity-50"
        >
          {#if loading}
            <Icon name="progress-activity" size="sm" class="animate-spin" />
            <span>Konto wird erstellt...</span>
          {:else}
            <span>Konto erstellen</span>
          {/if}
        </button>
      </form>

      <!-- Footer Login Link -->
      <div class="border-t border-border-subtle pt-2 text-center">
        <p class="text-xs text-text-muted">
          Bereits ein Konto vorhanden?
          <a href="/auth/login" class="ml-1 font-bold text-primary hover:underline"> Anmelden </a>
        </p>
      </div>
    </div>
  </div>
</div>
