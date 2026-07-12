<script lang="ts">
  import { auth, type User } from '$stores/auth.svelte';
  import { rawPost } from '$lib/api/client';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import Card from '$components/ui/Card.svelte';
  import Input from '$components/ui/Input.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import Divider from '$components/ui/Divider.svelte';
  import Icon from '$components/ui/Icon.svelte';

  let username = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  onMount(() => {
    if (auth.isAuthenticated) goto('/');
  });

  async function login(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    loading = true;

    const res = await rawPost('/api/v1/auth/login', { username, password });
    const body = await res.json().catch(() => null);
    const data = res.ok ? (body as { token: string; user: Record<string, unknown> }) : null;
    const err = res.ok ? null : (body?.error ?? body?.detail ?? 'Login failed');

    loading = false;

    if (err || !data) {
      error = err ?? 'Login failed';
      return;
    }

    auth.setSession(data.token, data.user as User);
    await goto('/');
  }
</script>

<svelte:head>
  <title>Salus — Sign In</title>
</svelte:head>

<div class="flex min-h-[80vh] items-center justify-center">
  <Card variant="elevated">
    <div style="max-width:400px;width:340px">
      <h2 class="mb-2 text-center text-[28px] font-bold leading-[36px] text-surface-900">
        Sign In
      </h2>
      <p class="mb-8 text-center text-base text-surface-500">
        Access your health data dashboard
      </p>

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
        <Btn variant="primary" type="submit" fullWidth loading={loading}>
          Sign In
        </Btn>
      </form>

      <div class="my-6">
        <Divider label="or" />
      </div>

      <div class="flex flex-col gap-2">
        <Btn variant="secondary" fullWidth onclick={() => window.location.href = '/api/v1/auth/oidc/google/login'}>
          <Icon name="login" />
          Sign in with Google
        </Btn>
        <Btn variant="secondary" fullWidth onclick={() => window.location.href = '/api/v1/auth/oidc/github/login'}>
          <Icon name="login" />
          Sign in with GitHub
        </Btn>
        <Btn variant="secondary" fullWidth onclick={() => window.location.href = '/api/v1/auth/oidc/oidc/login'}>
          <Icon name="login" />
          Sign in with OIDC
        </Btn>
      </div>

      <p class="mt-6 text-center text-sm text-surface-500">
        Don't have an account?
        <a href="/auth/register" class="font-medium text-primary-600 hover:text-primary-700">Create one</a>
      </p>
    </div>
  </Card>
</div>
