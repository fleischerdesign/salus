<script lang="ts">
  import { auth, type User } from '$stores/auth.svelte';
  import { rawPost } from '$lib/api/client';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import Card from '$components/ui/Card.svelte';
  import Input from '$components/ui/Input.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';

  let username = $state('');
  let password = $state('');
  let email = $state('');
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
      username, password, email: email.trim() || undefined
    });
    const body = await res.json().catch(() => null);
    const data = res.ok ? (body as { token: string; user: Record<string, unknown> }) : null;
    const err = res.ok ? null : (body?.error ?? body?.detail ?? 'Registration failed');

    loading = false;

    if (err || !data) {
      error = err ?? 'Registration failed';
      return;
    }

    auth.setSession(data.token, data.user as User);
    await goto('/');
  }
</script>

<svelte:head>
  <title>Salus — Create Account</title>
</svelte:head>

<div class="flex min-h-[80vh] items-center justify-center">
  <Card variant="elevated">
    <div style="max-width:400px;width:340px">
      <h2 class="mb-2 text-center text-[28px] font-bold leading-[36px] text-surface-900">
        Create Account
      </h2>
      <p class="mb-8 text-center text-base text-surface-500">
        Start tracking your health data
      </p>

      {#if error}
        <div class="mb-4">
          <AlertBanner variant="error" message={error} />
        </div>
      {/if}

      <form onsubmit={register} class="flex flex-col gap-4">
	<Input
		name="username"
		label="Username"
		bind:value={username}
		autocomplete="username"
		required
	/>
        <Input
          name="email"
          type="email"
          label="Email (optional)"
          bind:value={email}
        />
        <Input
          name="password"
          type="password"
          label="Password"
          bind:value={password}
          autocomplete="new-password"
          required
        />
        <Btn variant="primary" type="submit" fullWidth loading={loading}>
          Create Account
        </Btn>
      </form>

      <p class="mt-6 text-center text-sm text-surface-500">
        Already have an account?
        <a href="/auth/login" class="font-medium text-primary-600 hover:text-primary-700">Sign in</a>
      </p>
    </div>
  </Card>
</div>
