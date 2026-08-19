<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { startFastingSession } from '$lib/mutations/fasting';

  let { onopenfood } = $props<{
    onopenfood?: () => void;
  }>();

  const sessionsQuery = useQuery(() => db.fasting_session.toArray());
  const allSessions = $derived(sessionsQuery.value ?? []);
  const activeSession = $derived(allSessions.find((s) => !s.ended_at && !s.deleted_at));

  let currentTime = $state(Date.now());

  $effect(() => {
    const timer = setInterval(() => {
      currentTime = Date.now();
    }, 1000);
    return () => clearInterval(timer);
  });

  let elapsedSeconds = $derived.by(() => {
    if (!activeSession) return 0;
    const start = new Date(activeSession.started_at).getTime();
    return Math.max(0, Math.floor((currentTime - start) / 1000));
  });

  let elapsedHours = $derived(elapsedSeconds / 3600);

  let formattedTimer = $derived.by(() => {
    if (!activeSession) return '00:00:00';
    const h = String(Math.floor(elapsedSeconds / 3600)).padStart(2, '0');
    const m = String(Math.floor((elapsedSeconds % 3600) / 60)).padStart(2, '0');
    const s = String(elapsedSeconds % 60).padStart(2, '0');
    return `${h}:${m}:${s}`;
  });

  let metabolicZone = $derived.by(() => {
    if (!activeSession) return 'Bereit';
    if (elapsedHours < 4) return 'Zone 1: Blutzucker sinkt';
    if (elapsedHours < 12) return 'Zone 2: Fettverbrennung';
    if (elapsedHours < 18) return 'Zone 3: Ketose';
    if (elapsedHours < 24) return 'Zone 4: Autophagie';
    return 'Zone 5: Tiefe Autophagie';
  });

  async function handleStart() {
    await startFastingSession({ target_hours: 16, fasting_type: '16:8', water_only: true });
  }
</script>

<div
  class="flex h-full flex-col justify-between space-y-4 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
>
  <div class="flex items-start justify-between gap-3">
    <div class="flex min-w-0 items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
        style="background-color: color-mix(in srgb, var(--color-fasting) 12%, transparent); color: var(--color-fasting);"
      >
        <Icon name="schedule" size="md" />
      </div>
      <div class="min-w-0">
        <h3 class="truncate text-sm font-extrabold tracking-tight text-[var(--text-main)]">
          Intervallfasten &amp; Autophagie
        </h3>
        <p class="truncate text-xs text-[var(--text-muted)]">Metabolische Fastenuhr</p>
      </div>
    </div>
    <Badge variant={activeSession ? 'fasting' : 'default'} class="text-[0.625rem] font-bold">
      {activeSession ? (elapsedHours >= 18 ? 'Autophagie' : 'Fasten aktiv') : 'Inaktiv'}
    </Badge>
  </div>

  <div class="py-3 text-center">
    <div class="font-mono text-[1.8rem] font-extrabold text-[var(--text-main)] tabular-nums">
      {formattedTimer}
    </div>
    <div
      class="mt-0.5 text-[0.75rem] font-semibold tracking-wider text-[var(--color-fasting)] uppercase"
    >
      {metabolicZone}
    </div>
  </div>

  <div class="mb-3 text-center text-[0.75rem] text-[var(--text-muted)]">
    {#if activeSession}
      Ziel: <strong>{activeSession.target_hours || 16} Stunden</strong>
    {:else}
      Noch kein aktives Fastenfenster gestartet
    {/if}
  </div>

  {#if activeSession}
    <button
      type="button"
      class="w-full cursor-pointer rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] py-2 text-xs font-bold text-[var(--text-main)] transition-colors hover:bg-[var(--bg-surface-100)]"
      onclick={onopenfood}
    >
      Mahlzeit erfassen
    </button>
  {:else}
    <Btn variant="primary" size="sm" fullWidth onclick={handleStart}>Fasten starten (16:8)</Btn>
  {/if}
</div>
