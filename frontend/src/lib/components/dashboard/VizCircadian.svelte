<script lang="ts">
  import { goto } from '$app/navigation';
  import { db } from '$lib/db/database';
  import { fetchCircadianAdvice, type CircadianAdvice } from '$lib/analytics/views/circadian';
  import Icon from '$components/ui/Icon.svelte';

  let advice = $state<CircadianAdvice | null>(null);
  let currentTime = $state(new Date());

  // Keep current time updated for positioning the sun/moon
  $effect(() => {
    const timer = setInterval(() => {
      currentTime = new Date();
    }, 60000);

    fetchCircadianAdvice(db).then((a) => {
      advice = a;
    });

    return () => clearInterval(timer);
  });

  // Calculate sun position progress
  let progress = $derived.by(() => {
    if (!advice?.solar_times) return 0;
    const { sunrise, sunset } = advice.solar_times;

    const [riseH, riseM] = sunrise.split(':').map(Number);
    const [setH, setM] = sunset.split(':').map(Number);

    const startMins = riseH * 60 + riseM;
    const endMins = setH * 60 + setM;
    const curMins = currentTime.getHours() * 60 + currentTime.getMinutes();

    if (curMins < startMins) return 0;
    if (curMins > endMins) return 100;

    return Math.round(((curMins - startMins) / (endMins - startMins)) * 100);
  });

  let isNight = $derived.by(() => {
    if (!advice?.solar_times) return false;
    const { sunrise, sunset } = advice.solar_times;
    const [riseH, riseM] = sunrise.split(':').map(Number);
    const [setH, setM] = sunset.split(':').map(Number);
    const startMins = riseH * 60 + riseM;
    const endMins = setH * 60 + setM;
    const curMins = currentTime.getHours() * 60 + currentTime.getMinutes();
    return curMins < startMins || curMins > endMins;
  });

  let activeAdvice = $derived.by(() => {
    if (!advice) return 'Loading sleep and light schedule...';
    // Provide a neat real-time summary tip based on current time
    const curMins = currentTime.getHours() * 60 + currentTime.getMinutes();

    // Check light windows first
    if (advice.light_advice?.length > 0) {
      for (const item of advice.light_advice) {
        const [startStr, endStr] = item.time_window.split(' - ');
        if (!startStr || !endStr) continue;
        const [sh, sm] = startStr.split(':').map(Number);
        const [eh, em] = endStr.split(':').map(Number);
        const sMins = sh * 60 + sm;
        const eMins = eh * 60 + em;
        if (curMins >= sMins && curMins <= eMins) {
          return `${item.action}: ${item.description}`;
        }
      }
    }

    // Default target sleep advice
    return `Bedtime goal tonight: ${advice.sleep_window?.target_onset ?? '23:00'}.`;
  });
</script>

<button
  type="button"
  class="flex h-full w-full cursor-pointer flex-col justify-between border-0 bg-transparent p-2 text-left select-none focus:outline-none"
  onclick={() => goto('/coach/circadian')}
>
  <!-- Solar Arc Visualizer -->
  <div class="relative mt-2 flex h-20 w-full flex-col justify-end">
    <!-- Curve line -->
    <svg
      class="absolute inset-0 h-16 w-full text-surface-200"
      viewBox="0 0 100 30"
      preserveAspectRatio="none"
    >
      <path
        d="M 10 30 Q 50 2 90 30"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-dasharray="3 3"
      />
    </svg>

    <!-- Sun or Moon moving indicator -->
    {#if advice}
      {@const x = 10 + progress * 0.8}
      {@const y = 30 - Math.sin((progress / 100) * Math.PI) * 28}
      <div
        class="absolute -translate-x-1/2 -translate-y-1/2 transition-all duration-1000 ease-out"
        style="left: {x}%; top: {y}px;"
      >
        {#if isNight}
          <div
            class="flex h-6 w-6 items-center justify-center rounded-full bg-slate-900 text-amber-200 shadow-md"
          >
            <Icon name="dark-mode" size="sm" />
          </div>
        {:else}
          <div
            class="animate-spin-slow flex h-6 w-6 items-center justify-center rounded-full bg-amber-400 text-white shadow-md"
          >
            <Icon name="wb-sunny" size="sm" />
          </div>
        {/if}
      </div>
    {/if}

    <!-- Timeline Labels -->
    <div
      class="flex justify-between border-t border-surface-100 px-2 pt-1 text-[10px] text-surface-400"
    >
      <span class="flex items-center gap-0.5">
        <Icon name="light-mode" size={10} class="text-amber-500" />
        Sunrise: {advice?.solar_times?.sunrise ?? '—'}
      </span>
      <span class="flex items-center gap-0.5">
        Sunset: {advice?.solar_times?.sunset ?? '—'}
        <Icon name="dark-mode" size={10} class="text-slate-500" />
      </span>
    </div>
  </div>

  <!-- Dynamic daily tip banner -->
  <div class="rounded-lg border border-primary-500/10 bg-primary-50/50 p-2">
    <div class="flex items-start gap-1.5">
      <Icon name="psychology" size="sm" class="mt-0.5 shrink-0 text-primary-500" />
      <p class="text-[11px] leading-snug font-medium text-primary-700">
        {activeAdvice}
      </p>
    </div>
  </div>
</button>

<style>
  :global(.animate-spin-slow) {
    animation: spin 16s linear infinite;
  }
  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
</style>
