<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import PageHeader from '$components/ui/PageHeader.svelte';
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
        <div
          class="duration-micro flex flex-col items-center gap-2 rounded-xl border p-4 transition-all"
          class:border-surface-200={!isUnlocked}
          class:border-amber-300={isUnlocked}
          class:bg-surface-0={!isUnlocked}
          class:bg-gradient-to-br={isUnlocked}
          class:from-amber-50={isUnlocked}
          class:to-yellow-50={isUnlocked}
          class:shadow-sm={isUnlocked}
          class:opacity-50={!isUnlocked}
          class:grayscale={!isUnlocked}
        >
          <div
            class="flex h-12 w-12 items-center justify-center rounded-full text-2xl {isUnlocked
              ? (tierColors[def.tier] ?? 'from-surface-400 to-surface-500' + ' text-white')
              : 'bg-surface-100 text-surface-300'} {isUnlocked ? 'bg-gradient-to-br' : ''}"
          >
            <span class="material-symbols-outlined text-2xl">{isUnlocked ? def.icon : 'lock'}</span>
          </div>
          <div class="text-center">
            <div class="line-clamp-1 text-xs font-semibold text-surface-800">{def.title}</div>
            <div class="text-[10px] text-surface-400 capitalize">{def.tier}</div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
