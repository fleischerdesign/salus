<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';

  let {
    open = false,
    initialMode = 'user',
    onclose
  } = $props<{
    open: boolean;
    initialMode?: 'user' | 'admin';
    onclose: () => void;
  }>();

  let mode = $state<'user' | 'admin'>('user');
  let currentStep = $state(1);

  $effect(() => {
    mode = initialMode;
    currentStep = 1;
  });

  // 1. USER ONBOARDING STATE
  let uName = $state('Philipp Fleischer');
  let uBioSex = $state<'male' | 'female' | 'other'>('male');
  let uBirthYear = $state(1994);
  let uHeight = $state(184);
  let uWeight = $state(81.8);
  let uTimezone = $state('Europe/Berlin');
  let uGoals = $state<string[]>(['cardio', 'longevity', 'strength']);

  let bmrCalculated = $derived(
    Math.round(
      10 * uWeight + 6.25 * uHeight - 5 * (2026 - uBirthYear) + (uBioSex === 'male' ? 5 : -161)
    )
  );

  function toggleGoal(g: string) {
    if (uGoals.includes(g)) uGoals = uGoals.filter((item) => item !== g);
    else uGoals.push(g);
  }

  function completeSetup() {
    onclose();
  }
</script>

{#if open}
  <div
    class="fixed inset-0 z-70 flex items-center justify-center overflow-y-auto bg-black/75 p-3 backdrop-blur-md sm:p-5"
  >
    <div
      class="glass-panel animate-modal-pop w-full max-w-xl space-y-6 rounded-3xl p-6 text-text-main shadow-2xl sm:p-8"
    >
      <!-- Top Navigation & Flow-Mode Switcher -->
      <div
        class="flex flex-wrap items-center justify-between gap-3 border-b border-border-subtle pb-2"
      >
        <div class="flex items-center gap-2.5">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-extrabold text-white shadow-xs"
          >
            S
          </div>
          <div>
            <h1 class="text-sm font-extrabold text-text-main">
              {mode === 'user' ? 'Persönliches Onboarding' : 'Instanz-Initialisierung'}
            </h1>
            <span class="text-[0.625rem] text-text-soft">
              {mode === 'user'
                ? 'Schritt ' + currentStep + ' von 4 • Biometrisches Profil'
                : 'Schritt ' + currentStep + ' von 4 • Server-Setup'}
            </span>
          </div>
        </div>

        <button
          type="button"
          onclick={onclose}
          class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-full text-text-muted transition-colors hover:bg-surface-50 hover:text-text-main"
        >
          <Icon name="close" size="sm" />
        </button>
      </div>

      <!-- Step Progress Indicator -->
      <div class="flex items-center justify-between gap-2">
        {#each [1, 2, 3, 4] as step}
          <div
            class="h-1.5 flex-1 rounded-full transition-all duration-300 {step <= currentStep
              ? 'bg-primary'
              : 'bg-surface-100'}"
          ></div>
        {/each}
      </div>

      <!-- Step Content -->
      {#if currentStep === 1}
        <div class="space-y-4">
          <h2 class="text-base font-bold text-text-main">1. Basis-Identität &amp; Biometrie</h2>
          <Input
            bind:value={uName}
            label="Vollständiger Name / Anzeigename"
            placeholder="z.B. Philipp Fleischer"
          />

          <div class="grid grid-cols-2 gap-3">
            <Input bind:value={uHeight} label="Körpergröße" type="number" unit="cm" />
            <Input bind:value={uWeight} label="Körpergewicht" type="number" unit="kg" />
          </div>

          <div
            class="flex items-center justify-between rounded-xl border border-border-subtle bg-surface-50 p-3 text-xs"
          >
            <span class="text-text-muted">Berechneter Grundumsatz (BMR)</span>
            <span class="font-extrabold text-primary tabular-nums">{bmrCalculated} kcal/Tag</span>
          </div>
        </div>
      {:else if currentStep === 2}
        <div class="space-y-4">
          <h2 class="text-base font-bold text-text-main">
            2. Primäre Gesundheits- &amp; Therapieziele
          </h2>
          <div class="grid grid-cols-2 gap-2.5">
            <button
              type="button"
              onclick={() => toggleGoal('strength')}
              class="cursor-pointer rounded-2xl border p-3 text-left transition-all {uGoals.includes(
                'strength'
              )
                ? 'border-primary bg-primary-soft shadow-xs'
                : 'border-border-subtle bg-surface-50'}"
            >
              <span class="block text-xs font-bold text-text-main"
                >Kraftaufbau &amp; Hypertrophie</span
              >
              <span class="text-[0.625rem] text-text-muted">Progressive Overload &amp; 1RM</span>
            </button>

            <button
              type="button"
              onclick={() => toggleGoal('longevity')}
              class="cursor-pointer rounded-2xl border p-3 text-left transition-all {uGoals.includes(
                'longevity'
              )
                ? 'border-vital bg-vital-soft shadow-xs'
                : 'border-border-subtle bg-surface-50'}"
            >
              <span class="block text-xs font-bold text-text-main"
                >Langlebigkeit &amp; Prävention</span
              >
              <span class="text-[0.625rem] text-text-muted">ESC 2024 &amp; ApoB-Optimierung</span>
            </button>

            <button
              type="button"
              onclick={() => toggleGoal('cardio')}
              class="cursor-pointer rounded-2xl border p-3 text-left transition-all {uGoals.includes(
                'cardio'
              )
                ? 'border-hydrate bg-hydrate-soft shadow-xs'
                : 'border-border-subtle bg-surface-50'}"
            >
              <span class="block text-xs font-bold text-text-main">Kardiovaskuläre Ausdauer</span>
              <span class="text-[0.625rem] text-text-muted">VO2max &amp; Ruhepuls-Senkung</span>
            </button>

            <button
              type="button"
              onclick={() => toggleGoal('fasting')}
              class="cursor-pointer rounded-2xl border p-3 text-left transition-all {uGoals.includes(
                'fasting'
              )
                ? 'border-circadian bg-circadian-soft shadow-xs'
                : 'border-border-subtle bg-surface-50'}"
            >
              <span class="block text-xs font-bold text-text-main">Stoffwechsel &amp; Fasten</span>
              <span class="text-[0.625rem] text-text-muted">16:8 &amp; Glukosestabilität</span>
            </button>
          </div>
        </div>
      {:else if currentStep === 3}
        <div class="space-y-4">
          <h2 class="text-base font-bold text-text-main">3. Zeitzone &amp; Tagesrhythmus</h2>
          <Input
            bind:value={uTimezone}
            label="Standort-Zeitzone (IANA)"
            placeholder="Europe/Berlin"
          />
          <p class="text-xs leading-relaxed text-text-muted">
            Deine Tagesgrenzen und zirkadianen Sonnenbögen werden millimetergenau auf Basis dieser
            Zeitzone berechnet.
          </p>
        </div>
      {:else if currentStep === 4}
        <div class="space-y-4 py-2 text-center">
          <div
            class="mx-auto flex h-16 w-16 items-center justify-center rounded-full border-2 border-emerald-500/30 bg-emerald-500/15 text-2xl font-black text-emerald-500"
          >
            <Icon name="check_circle" size="lg" />
          </div>
          <h2 class="text-lg font-extrabold text-text-main">Profil erfolgreich eingerichtet!</h2>
          <p class="mx-auto max-w-sm text-xs text-text-muted">
            Salus ist nun personalisiert und synchronisiert alle biometrischen Daten lokal und
            verschlüsselt.
          </p>
        </div>
      {/if}

      <!-- Bottom Navigation Controls -->
      <div class="flex items-center justify-between border-t border-border-subtle pt-4">
        {#if currentStep > 1}
          <Btn variant="secondary" onclick={() => (currentStep -= 1)}>
            <Icon name="arrow_back" size="sm" />
            <span>Zurück</span>
          </Btn>
        {:else}
          <div></div>
        {/if}

        {#if currentStep < 4}
          <Btn variant="primary" onclick={() => (currentStep += 1)}>
            <span>Weiter</span>
            <Icon name="arrow_forward" size="sm" />
          </Btn>
        {:else}
          <Btn variant="primary" onclick={completeSetup}>
            <Icon name="check" size="sm" />
            <span>Loslegen</span>
          </Btn>
        {/if}
      </div>
    </div>
  </div>
{/if}
