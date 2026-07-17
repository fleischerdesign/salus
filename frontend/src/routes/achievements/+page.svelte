<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import type { AchievementDefinition, UserAchievement } from '$lib/db/types';

  let loading = $state(true);
  let definitions = $state<AchievementDefinition[]>([]);
  let unlocked = $state<UserAchievement[]>([]);

  const unlockedCodes = $derived(new Set(unlocked.map((u) => u.achievement_code)));

  const tierColors: Record<string, string> = {
    bronze: 'from-amber-600 to-amber-700',
    silver: 'from-slate-400 to-slate-500',
    gold: 'from-yellow-500 to-amber-500',
    platinum: 'from-cyan-400 to-blue-500'
  };

  $effect(() => {
    const sub1 = liveQuery(() => db.achievement_definition.toArray()).subscribe((v) => {
      definitions = v;
    });
    const sub2 = liveQuery(() => db.user_achievement.toArray()).subscribe((v) => {
      unlocked = v;
      loading = false;
    });
    return () => {
      sub1.unsubscribe();
      sub2.unsubscribe();
    };
  });

  const visibleDefs = $derived(
    definitions.filter((d) => !d.is_hidden || unlockedCodes.has(d.code))
  );
</script>

<svelte:head><title>Salus — Achievements</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Achievements"
    subtitle="Badges and milestones earned through consistency"
    icon="emoji-events"
    iconColor="#f59e0b"
  />

  {#if loading}
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
      {#each Array(6) as _}
        <div class="aspect-square animate-pulse rounded-xl bg-surface-100"></div>
      {/each}
    </div>
  {:else}
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
      {#each visibleDefs as def (def.code)}
        {@const isUnlocked = unlockedCodes.has(def.code)}
        <Card
          padding={false}
          variant={isUnlocked ? 'elevated' : 'flat'}
          class="duration-micro flex flex-col items-center gap-2 p-4 transition-all {isUnlocked
            ? 'border-amber-300'
            : 'opacity-50 grayscale'}"
        >
          {#if isUnlocked}
            <div
              class="pointer-events-none absolute inset-0 rounded-md bg-gradient-to-br from-amber-50 to-yellow-50"
            ></div>
          {/if}
          <div
            class="relative flex h-12 w-12 items-center justify-center rounded-full text-2xl {isUnlocked
              ? (tierColors[def.tier] ?? 'from-surface-400 to-surface-500' + ' text-white')
              : 'bg-surface-100 text-surface-300'} {isUnlocked ? 'bg-gradient-to-br' : ''}"
          >
            <Icon name={isUnlocked ? def.icon : 'lock'} size="xl" />
          </div>
          <div class="relative text-center">
            <div class="line-clamp-1 text-xs font-semibold text-surface-800">{def.title}</div>
            <div class="text-[10px] text-surface-400 capitalize">{def.tier}</div>
          </div>
        </Card>
      {/each}
    </div>
    {#if visibleDefs.length === 0}
      <div class="flex flex-col items-center gap-3 py-16 text-center">
        <Icon name="emoji-events" size="2xl" class="text-surface-300" />
        <h3 class="text-lg font-semibold text-surface-700">No achievements synced yet</h3>
        <p class="max-w-xs text-sm text-surface-400">
          Your achievements will appear here once data has been synced.
        </p>
      </div>
    {/if}
  {/if}
</div>
