<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  const insightsQuery = useQuery(async () => {
    const all = await db.insight.toArray();
    return all.filter((i) => !i.deleted_at);
  });

  const insights = $derived(insightsQuery.value ?? []);
  const loading = $derived(insightsQuery.loading);
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Gesundheitsempfehlungen und Coaching</h1>
      <p class="mt-0.5 text-sm text-[var(--text-muted)]">
        Personalisierte Langlebigkeits-Erkenntnisse abgeleitet aus deinen biometrischen
        Korrelationen
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">Modell: Biometric Engine</Badge>
    </div>
  </div>

  <!-- Insights List -->
  {#if loading}
    <div class="py-12 text-center text-sm text-[var(--text-muted)]">
      Erkenntnisse werden berechnet...
    </div>
  {:else if insights.length === 0}
    <div
      class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-8 text-center shadow-[var(--shadow-card)]"
    >
      <div
        class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
      >
        <Icon name="psychology" size="lg" />
      </div>
      <h3 class="text-base font-bold text-[var(--text-main)]">
        Noch keine Coaching-Impulse generiert
      </h3>
      <p class="mx-auto max-w-md text-xs text-[var(--text-muted)]">
        Sobald du regelmäßig biometrische Messwerte (Schlaf, Aktivität, Ernährung oder HRV) erfasst,
        leitet die Biometric Engine evidenzbasierte Korrelationen und Handlungsempfehlungen ab.
      </p>
    </div>
  {:else}
    <div class="space-y-4">
      {#each insights as ins (ins.id)}
        <div
          class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-6 shadow-[var(--shadow-card)]"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span
              class="font-mono text-xs font-bold tracking-wider text-[var(--color-primary)] uppercase"
              >{ins.query_date}</span
            >
            <Badge variant="default" class="font-mono text-[0.625rem]">Evidenzbasiert</Badge>
          </div>

          <p class="text-xs leading-relaxed text-[var(--text-muted)]">{ins.content}</p>
        </div>
      {/each}
    </div>
  {/if}
</div>
