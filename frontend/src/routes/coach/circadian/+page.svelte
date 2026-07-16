<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { saveCircadianProfile } from '$lib/mutations/misc';
  import { fetchCircadianAdvice, type CircadianAdvice } from '$lib/analytics/views/circadian';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Icon from '$components/ui/Icon.svelte';

  let profile = liveQuery(() =>
    db.circadian_profile.toArray().then((arr) => arr.find((p) => !p.deleted_at) ?? null)
  );

  let advice = $state<CircadianAdvice | null>(null);
  let adviceLoading = $state(false);
  let saving = $state(false);

  let latitude = $state(52.52);
  let longitude = $state(13.4);
  let timezone = $state(1);
  let chronotype = $state('intermediate');

  const chronoOpts = [
    { value: 'morning_lark', label: 'Morning Lark' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'night_owl', label: 'Night Owl' }
  ];

  $effect(() => {
    const p = $profile;
    if (p) {
      latitude = p.latitude ?? 52.52;
      longitude = p.longitude ?? 13.4;
      timezone = p.timezone_offset_hours ?? 1;
      chronotype = p.configured_chronotype ?? 'intermediate';
    }
  });

  $effect(() => {
    adviceLoading = true;
    fetchCircadianAdvice(db).then((a) => {
      advice = a;
      adviceLoading = false;
    });
  });

  function timeToHours(t: string): number {
    const [h, m] = t.split(':').map(Number);
    return h + m / 60;
  }

  function timePct(t: string): number {
    return (timeToHours(t) / 24) * 100;
  }

  function alignmentLabel(score: number) {
    if (score >= 85) return 'Optimal Synchronization';
    if (score >= 60) return 'Minor Shift (Social Jetlag)';
    return 'Misaligned Circadian Phase';
  }

  function alignmentColor(score: number) {
    if (score >= 85) return 'var(--color-primary)';
    if (score >= 60) return '#f59e0b';
    return 'var(--color-error)';
  }

  async function save(e: SubmitEvent) {
    e.preventDefault();
    saving = true;
    await saveCircadianProfile(latitude, longitude, timezone, chronotype);
    saving = false;
  }
</script>

<svelte:head><title>Salus — Circadian Advisor</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Circadian & Light Advisor"
    subtitle="Sync your biometrics, sleep patterns, and daily habits with the natural solar cycle."
    icon="light_mode"
    iconColor="#4f46e5"
  />

  {#if adviceLoading && !advice}
    <Spinner size="lg" />
  {:else if advice}
    <Card>
      {#snippet header()}
        <h2 class="text-lg font-semibold text-surface-900">24-Hour Circadian Alignment Timeline</h2>
        <p class="mt-1 text-xs text-surface-500">
          Visualizing solar phases alongside your actual habits.
        </p>
      {/snippet}

      {@const dawnPct = timePct(advice.solar_times.dawn)}
      {@const sunrisePct = timePct(advice.solar_times.sunrise)}
      {@const sunsetPct = timePct(advice.solar_times.sunset)}
      {@const duskPct = timePct(advice.solar_times.dusk)}

      <div class="space-y-3">
        <div
          class="relative h-8 overflow-hidden rounded-2xl bg-surface-100 shadow-[inset_0_2px_4px_rgba(0,0,0,0.05)]"
        >
          <div
            class="absolute inset-y-0 bg-indigo-900"
            style="left: 0%; right: {100 - dawnPct}%"
          ></div>
          <div
            class="absolute inset-y-0 bg-gradient-to-r from-orange-300 to-yellow-200"
            style="left: {dawnPct}%; right: {100 - sunrisePct}%"
          ></div>
          <div
            class="absolute inset-y-0 bg-gradient-to-r from-yellow-200 via-yellow-300 to-amber-200"
            style="left: {sunrisePct}%; right: {100 - sunsetPct}%"
          ></div>
          <div
            class="absolute inset-y-0 bg-gradient-to-r from-amber-200 to-orange-300"
            style="left: {sunsetPct}%; right: {100 - duskPct}%"
          ></div>
          <div class="absolute inset-y-0 bg-indigo-900" style="left: {duskPct}%; right: 0%"></div>
        </div>

        <div class="flex justify-between px-2 text-xs font-semibold text-surface-500">
          <span>00:00</span>
          <span>Dawn: {advice.solar_times.dawn}</span>
          <span>Sunrise: {advice.solar_times.sunrise}</span>
          <span>Noon: {advice.solar_times.solar_noon}</span>
          <span>Sunset: {advice.solar_times.sunset}</span>
          <span>Dusk: {advice.solar_times.dusk}</span>
          <span>24:00</span>
        </div>
      </div>
    </Card>

    <div class="grid gap-6 lg:grid-cols-2">
      <div class="space-y-6">
        <Card>
          <div class="flex flex-col items-center text-center">
            <h3 class="text-lg font-semibold text-surface-900">Circadian Alignment</h3>
            <div class="relative my-4 flex h-[120px] w-[120px] items-center justify-center">
              <svg viewBox="0 0 120 120" class="h-full w-full -rotate-90">
                <circle
                  cx="60"
                  cy="60"
                  r="44"
                  stroke="var(--color-surface-100)"
                  stroke-width="8"
                  fill="transparent"
                />
                <circle
                  cx="60"
                  cy="60"
                  r="44"
                  stroke={alignmentColor(advice.alignment_score)}
                  stroke-width="8"
                  fill="transparent"
                  stroke-linecap="round"
                  stroke-dasharray={2 * Math.PI * 44}
                  stroke-dashoffset={(2 * Math.PI * 44 * (100 - advice.alignment_score)) / 100}
                />
              </svg>
              <span class="absolute text-2xl font-extrabold text-surface-900">
                {advice.alignment_score}%
              </span>
            </div>
            <p class="text-sm font-medium text-surface-700">
              {alignmentLabel(advice.alignment_score)}
            </p>
          </div>
        </Card>

        <Card>
          {#snippet header()}
            <h2 class="text-lg font-semibold text-surface-900">Location & Chronotype</h2>
          {/snippet}
          <form onsubmit={save} class="flex flex-col gap-4">
            <div class="grid grid-cols-2 gap-4">
              <FormField label="Latitude">
                <Input name="lat" type="number" step="0.0001" bind:value={latitude} />
              </FormField>
              <FormField label="Longitude">
                <Input name="lon" type="number" step="0.0001" bind:value={longitude} />
              </FormField>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <FormField label="Timezone UTC Offset">
                <Input name="tz" type="number" step="0.5" bind:value={timezone} />
              </FormField>
              <FormField label="Chronotype">
                <Select name="chronotype" options={chronoOpts} bind:value={chronotype} />
              </FormField>
            </div>
            <Btn variant="primary" type="submit" size="sm" loading={saving}>Update Parameters</Btn>
          </form>
        </Card>
      </div>

      <div class="space-y-6">
        <Card>
          {#snippet header()}
            <h2 class="text-lg font-semibold text-surface-900">Optimal Sleep Window</h2>
          {/snippet}
          <div class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-lg border border-primary-200 bg-primary-50 p-3 text-center">
                <p class="text-xs font-medium text-primary-600">Target Window</p>
                <p class="mt-1 text-base font-semibold text-primary-700">
                  {advice.sleep_window.target_onset} -
                  {advice.sleep_window.target_offset}
                </p>
              </div>
              <div class="rounded-lg border border-surface-200 bg-surface-50 p-3 text-center">
                <p class="text-xs font-medium text-surface-500">Actual Window (Recent)</p>
                <p class="mt-1 text-base font-semibold text-surface-700">
                  {advice.sleep_window.actual_onset} -
                  {advice.sleep_window.actual_offset}
                </p>
              </div>
            </div>
            <p class="text-sm leading-relaxed text-surface-600">
              {advice.sleep_window.advice}
            </p>
          </div>
        </Card>

        <Card>
          {#snippet header()}
            <h2 class="text-lg font-semibold text-surface-900">Light Exposure Scheduling</h2>
          {/snippet}
          <div class="-mx-4 divide-y divide-surface-100">
            {#each advice.light_advice as la, i}
              <div class="flex gap-3 px-4 py-3">
                <Icon
                  name={i === 0 ? 'light-mode' : 'dark-mode'}
                  size="lg"
                  class="mt-0.5 shrink-0 text-primary-500"
                />
                <div class="min-w-0">
                  <p class="text-sm font-medium text-surface-900">
                    {la.action}
                    <span class="text-primary-600">{la.time_window}</span>
                  </p>
                  <p class="mt-1 text-xs leading-relaxed text-surface-500">
                    {la.description}
                  </p>
                </div>
              </div>
            {/each}
          </div>
        </Card>

        <Card>
          {#snippet header()}
            <h2 class="text-lg font-semibold text-surface-900">Metabolic Window (Eating)</h2>
          {/snippet}
          <div class="space-y-3">
            <div class="w-fit rounded-lg border border-teal-200 bg-teal-50 p-3">
              <p class="text-xs font-medium text-teal-600">Optimal Intake Period</p>
              <p class="mt-1 text-base font-semibold text-teal-700">
                {advice.eating_window.start} -
                {advice.eating_window.end}
              </p>
            </div>
            <p class="text-sm leading-relaxed text-surface-600">
              {advice.eating_window.advice}
            </p>
          </div>
        </Card>
      </div>
    </div>
  {:else}
    <p class="text-surface-500">
      No circadian profile found. Please set up your location and chronotype.
    </p>
  {/if}
</div>
