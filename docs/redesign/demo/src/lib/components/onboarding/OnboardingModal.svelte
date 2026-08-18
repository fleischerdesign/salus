<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let {
    open = false,
    initialMode = 'user', // 'user' | 'admin'
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

  // ═══════════════════════════════════════════════════════════
  // 1. USER ONBOARDING STATE
  // ═══════════════════════════════════════════════════════════
  let uName = $state('Philipp Fleischer');
  let uBioSex = $state<'male' | 'female' | 'other'>('male');
  let uBirthYear = $state(1994);
  let uHeight = $state(184);
  let uWeight = $state(81.8);
  let uTimezone = $state('Europe/Berlin');
  let uGoals = $state<string[]>(['cardio', 'longevity', 'strength']);
  let uFirstMetric = $state('weight');
  let uFirstValue = $state('81.8');
  let uTokenGenerated = $state(false);
  let uApiToken = $state('');

  let bmrCalculated = $derived(
    Math.round(10 * uWeight + 6.25 * uHeight - 5 * (2026 - uBirthYear) + (uBioSex === 'male' ? 5 : -161))
  );

  function toggleGoal(g: string) {
    if (uGoals.includes(g)) uGoals = uGoals.filter(item => item !== g);
    else uGoals.push(g);
  }

  function generateUserToken() {
    uApiToken = `salus_pat_${Math.random().toString(36).substring(2, 10)}_live`;
    uTokenGenerated = true;
  }

  // ═══════════════════════════════════════════════════════════
  // 2. ADMIN INSTANCE SETUP STATE
  // ═══════════════════════════════════════════════════════════
  let aInstanceName = $state('Salus Health Node');
  let aDomain = $state('salus.local');
  let aOpenRegistration = $state(false);
  let aAdminUser = $state('admin');
  let aAdminEmail = $state('admin@salus.local');
  let aAdminPassword = $state('');
  let aSeedCatalog = $state(true);
  let aSeedFoodDb = $state(true);
  let aAuthProvider = $state<'local' | 'oidc' | 'ldap'>('local');
  let aOidcIssuer = $state('https://auth.company.com/realms/health');

  function completeSetup() {
    if (mode === 'user') {
      alert(`Willkommen bei Salus, ${uName}! Dein biometrisches Profil (Grundumsatz: ${bmrCalculated} kcal) wurde initialisiert.`);
    } else {
      alert(`Instanz "${aInstanceName}" (@${aDomain}) erfolgreich konfiguriert. 42 globale Metriken geseedet.`);
    }
    onclose();
  }
</script>

{#if open}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-60 flex items-center justify-center p-3 sm:p-5 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-xl w-full shadow-2xl space-y-6 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Top Navigation & Flow-Mode Switcher -->
      <div class="flex items-center justify-between flex-wrap gap-3 pb-2 border-b border-[var(--border-subtle)]">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full bg-[var(--color-primary)] text-white flex items-center justify-center font-extrabold text-sm shadow-xs">
            S
          </div>
          <div>
            <h1 class="font-extrabold text-sm text-[var(--text-main)]">
              {mode === 'user' ? 'Persönliches Onboarding' : 'Instanz-Initialisierung'}
            </h1>
            <span class="text-[0.625rem] text-[var(--text-soft)]">
              {mode === 'user' ? 'Schritt ' + currentStep + ' von 5 • Biometrisches Profil' : 'Schritt ' + currentStep + ' von 5 • Server-Setup'}
            </span>
          </div>
        </div>

        <!-- Mode Switcher Pills -->
        <div class="flex items-center gap-1 bg-[var(--bg-surface-50)] p-1 rounded-full border border-[var(--border-subtle)]">
          <button
            type="button"
            onclick={() => { mode = 'user'; currentStep = 1; }}
            class="px-2.5 py-1 rounded-full text-[0.6875rem] font-bold transition-all cursor-pointer {mode === 'user' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-xs' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
          >
            User-Setup
          </button>
          <button
            type="button"
            onclick={() => { mode = 'admin'; currentStep = 1; }}
            class="px-2.5 py-1 rounded-full text-[0.6875rem] font-bold transition-all cursor-pointer {mode === 'admin' ? 'bg-[var(--bg-surface-0)] text-[var(--color-vital)] shadow-xs' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
          >
            Server-Admin
          </button>
        </div>
      </div>

      <!-- Step Indicator Dots -->
      <div class="flex items-center justify-between px-2">
        {#each [1, 2, 3, 4, 5] as stepNum}
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-full flex items-center justify-center text-[0.625rem] font-bold font-mono transition-all {currentStep === stepNum ? 'bg-[var(--color-primary)] text-white scale-110 shadow-sm' : currentStep > stepNum ? 'bg-emerald-500 text-white' : 'bg-[var(--bg-surface-50)] text-[var(--text-soft)] border border-[var(--border-subtle)]'}">
              {currentStep > stepNum ? '' : stepNum}
            </div>
            {#if stepNum < 5}
              <div class="w-6 sm:w-12 h-0.5 transition-all {currentStep > stepNum ? 'bg-emerald-500' : 'bg-[var(--border-subtle)]'}"></div>
            {/if}
          </div>
        {/each}
      </div>

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- FLOW A: USER ONBOARDING (5 STEPS)                           -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {#if mode === 'user'}

        <!-- STEP 1: STAMMDATEN & BIOMETRIE -->
        {#if currentStep === 1}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">1. Biometrisches Basisprofil</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Grundlage für kalorische Berechnungen nach Katch-McArdle und klinische Referenzwerte</p>
            </div>

            <div class="space-y-3 text-xs">
              <div>
                <label for="u-name" class="block font-semibold text-[var(--text-muted)] mb-1">Dein Name</label>
                <input id="u-name" type="text" bind:value={uName} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]" />
              </div>

              <div>
                <span class="block font-semibold text-[var(--text-muted)] mb-1">Biologisches Geschlecht</span>
                <div class="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onclick={() => uBioSex = 'male'}
                    class="py-2.5 rounded-xl border text-xs font-semibold cursor-pointer transition-all {uBioSex === 'male' ? 'bg-[var(--color-primary)] text-white border-transparent' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                  >
                    Männlich
                  </button>
                  <button
                    type="button"
                    onclick={() => uBioSex = 'female'}
                    class="py-2.5 rounded-xl border text-xs font-semibold cursor-pointer transition-all {uBioSex === 'female' ? 'bg-[var(--color-primary)] text-white border-transparent' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                  >
                    Weiblich
                  </button>
                  <button
                    type="button"
                    onclick={() => uBioSex = 'other'}
                    class="py-2.5 rounded-xl border text-xs font-semibold cursor-pointer transition-all {uBioSex === 'other' ? 'bg-[var(--color-primary)] text-white border-transparent' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                  >
                    Divers
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-3 gap-2.5">
                <div>
                  <label for="u-year" class="block font-semibold text-[var(--text-muted)] mb-1">Geburtsjahr</label>
                  <input id="u-year" type="number" bind:value={uBirthYear} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-[var(--text-main)] outline-none" />
                </div>
                <div>
                  <label for="u-height" class="block font-semibold text-[var(--text-muted)] mb-1">Größe (cm)</label>
                  <input id="u-height" type="number" bind:value={uHeight} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-[var(--text-main)] outline-none" />
                </div>
                <div>
                  <label for="u-weight" class="block font-semibold text-[var(--text-muted)] mb-1">Gewicht (kg)</label>
                  <input id="u-weight" type="number" step="0.1" bind:value={uWeight} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-[var(--text-main)] outline-none" />
                </div>
              </div>

              <!-- Live BMR Preview -->
              <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl flex items-center justify-between">
                <span class="text-[0.6875rem] text-[var(--text-muted)]">Berechneter Grundumsatz (BMR):</span>
                <span class="font-mono font-bold text-[var(--color-primary)]">{bmrCalculated} kcal / Tag</span>
              </div>
            </div>
          </div>

        <!-- STEP 2: TIMEZONE & CIRCADIAN -->
        {:else if currentStep === 2}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">2. Zeitzone und Zirkadiane Steuerung</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Zeitzone für deine tagesaktuellen Auswertungen und Zirkadian-Rhythmen</p>
            </div>

            <div class="space-y-3 text-xs">
              <div>
                <div class="flex justify-between items-center mb-1">
                  <label for="u-tz" class="font-semibold text-[var(--text-muted)]">IANA Zeitzone</label>
                  <button type="button" onclick={() => uTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone} class="text-[var(--color-primary)] hover:underline text-[0.6875rem] font-semibold cursor-pointer">
                    Geräte-Zeitzone übernehmen
                  </button>
                </div>
                <select id="u-tz" bind:value={uTimezone} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-[var(--text-main)] outline-none">
                  <option value="Europe/Berlin">Europe/Berlin (Mitteleuropäische Zeit)</option>
                  <option value="Europe/Zurich">Europe/Zurich (Schweiz)</option>
                  <option value="Europe/Vienna">Europe/Vienna (Österreich)</option>
                  <option value="America/New_York">America/New_York (US Ostküste)</option>
                  <option value="UTC">UTC (Koordiniert)</option>
                </select>
              </div>

              <div class="p-3.5 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl space-y-2">
                <span class="font-bold text-[var(--text-main)] flex items-center gap-1.5">
                  <Icon name="sun" class="text-[var(--color-circadian)]" /> Automatische Zirkadian-Berechnung
                </span>
                <p class="text-[0.6875rem] text-[var(--text-muted)] leading-relaxed">
                  Salus berechnet anhand deiner Zeitzone die astronomische Sonnenkurve, das Melatonin-Onset-Fenster und die Koffein-Abklingkurve (5.5h Halbwertszeit).
                </p>
              </div>
            </div>
          </div>

        <!-- STEP 3: HEALTH FOCUS GOALS -->
        {:else if currentStep === 3}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">3. Deine primären Schwerpunkte</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Wähle die Fachbereiche, die auf deinem Dashboard priorisiert werden sollen</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              {#each [
                { id: 'cardio', label: 'Kardiovaskuläre Gesundheit', desc: 'Blutdruck, Ruhepuls, HRV-Tracking' },
                { id: 'longevity', label: 'Langlebigkeit und Biomarker', desc: 'ApoB, HbA1c, hs-CRP Verläufe' },
                { id: 'strength', label: 'Kraftaufbau und Training', desc: 'Progressive Overload, 1RM Kurven' },
                { id: 'autophagy', label: 'Intervallfasten und Autophagie', desc: '16:8 Timer, Ketose-Phasen' },
                { id: 'sleep', label: 'Schlafarchitektur', desc: 'Tiefschlaf-Analyse, Chronotyp' },
                { id: 'habits', label: 'Gewohnheiten und Streaks', desc: '52-Wochen Konsistenzmatrizen' }
              ] as f}
                <button
                  type="button"
                  onclick={() => toggleGoal(f.id)}
                  class="text-left p-3 rounded-xl border transition-all cursor-pointer {uGoals.includes(f.id) ? 'bg-[var(--color-primary)]/10 border-[var(--color-primary)] shadow-xs' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] hover:border-[var(--text-soft)]'}"
                >
                  <div class="font-bold text-[var(--text-main)] flex items-center justify-between">
                    <span>{f.label}</span>
                    {#if uGoals.includes(f.id)}<span class="text-[var(--color-primary)]"></span>{/if}
                  </div>
                  <div class="text-[0.625rem] text-[var(--text-soft)] mt-0.5">{f.desc}</div>
                </button>
              {/each}
            </div>
          </div>

        <!-- STEP 4: SENSORS & WEARABLES -->
        {:else if currentStep === 4}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">4. Sensoren und Datenquellen</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Kopplung für automatischen Datentransfer oder API-Token Generierung</p>
            </div>

            <div class="space-y-2.5 text-xs">
              <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl flex items-center justify-between">
                <div class="flex items-center gap-2.5">
                  <Icon name="sun" class="text-rose-500" />
                  <div>
                    <div class="font-bold text-[var(--text-main)]">Apple HealthKit</div>
                    <div class="text-[0.625rem] text-[var(--text-soft)]">Schritte, Ruhepuls, Schlafphasen</div>
                  </div>
                </div>
                <Badge variant="success">Verbunden</Badge>
              </div>

              <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl flex items-center justify-between">
                <div class="flex items-center gap-2.5">
                  <Icon name="sun" class="text-slate-400" />
                  <div>
                    <div class="font-bold text-[var(--text-main)]">Oura Ring Gen 3</div>
                    <div class="text-[0.625rem] text-[var(--text-soft)]">HRV, Bereitschaft, Temperatur</div>
                  </div>
                </div>
                <Badge variant="success">Verbunden</Badge>
              </div>

              <!-- API Token Generator -->
              <div class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl space-y-2">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-bold text-[var(--text-main)]">Persönlicher Webhook API-Token</div>
                    <div class="text-[0.625rem] text-[var(--text-soft)]">Für Shortcuts, Home Assistant & Skripte</div>
                  </div>
                  {#if !uTokenGenerated}
                    <Btn variant="secondary" size="sm" onclick={generateUserToken}>
                      Token erstellen
                    </Btn>
                  {:else}
                    <Badge variant="primary">Erstellt</Badge>
                  {/if}
                </div>

                {#if uTokenGenerated}
                  <input type="text" value={uApiToken} readonly class="w-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-lg p-2 font-mono text-[0.6875rem] text-[var(--color-primary)] outline-none" />
                {/if}
              </div>
            </div>
          </div>

        <!-- STEP 5: FIRST ENTRY & FINISH -->
        {:else if currentStep === 5}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">5. Erste Messung erfassen</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Erfasse deinen ersten Messpunkt, um die statistischen Trend-Splines zu starten</p>
            </div>

            <div class="p-4 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-3 text-xs">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label for="u-metric" class="block font-semibold text-[var(--text-muted)] mb-1">Vitalparameter</label>
                  <select id="u-metric" bind:value={uFirstMetric} class="w-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-[var(--text-main)] outline-none">
                    <option value="weight">Körpergewicht (kg)</option>
                    <option value="systolic_bp">Systolischer Blutdruck (mmHg)</option>
                    <option value="resting_hr">Ruheherzfrequenz (bpm)</option>
                    <option value="water">Wasserzufuhr (ml)</option>
                  </select>
                </div>

                <div>
                  <label for="u-val" class="block font-semibold text-[var(--text-muted)] mb-1">Messwert</label>
                  <input id="u-val" type="text" bind:value={uFirstValue} class="w-full bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-xl p-2.5 font-mono text-[var(--text-main)] outline-none" />
                </div>
              </div>

              <div class="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-500 text-[0.6875rem] font-semibold flex items-center gap-2">
                <Icon name="check" size={14} />
                <span>Wird sicher lokal auf deinem Gerät gespeichert und Ende-zu-Ende verschlüsselt synchronisiert.</span>
              </div>
            </div>
          </div>
        {/if}

      <!-- ═══════════════════════════════════════════════════════════ -->
      <!-- FLOW B: ADMIN INSTANCE SETUP (5 STEPS)                      -->
      <!-- ═══════════════════════════════════════════════════════════ -->
      {:else if mode === 'admin'}

        <!-- STEP 1: INSTANCE NAME & FEDERATION -->
        {#if currentStep === 1}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">1. Instanz-Identität und Föderation</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Konfiguriere den Servernamen und die WebFinger / ActivityPub Domain</p>
            </div>

            <div class="space-y-3 text-xs">
              <div>
                <label for="a-inst" class="block font-semibold text-[var(--text-muted)] mb-1">Instanz-Name</label>
                <input id="a-inst" type="text" bind:value={aInstanceName} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-[var(--text-main)] outline-none focus:border-[var(--color-primary)]" />
              </div>

              <div>
                <label for="a-dom" class="block font-semibold text-[var(--text-muted)] mb-1">Föderations-Domain (@handle@domain)</label>
                <input id="a-dom" type="text" bind:value={aDomain} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 font-mono text-[var(--text-main)] outline-none" />
              </div>

              <div class="flex items-center justify-between p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl">
                <div>
                  <span class="font-semibold text-[var(--text-main)] block">Offene Benutzer-Registrierung</span>
                  <span class="text-[0.625rem] text-[var(--text-soft)]">Neue Nutzer können sich selbst registrieren</span>
                </div>
                <button
                  type="button"
                  aria-label="Offene Registrierung umschalten"
                  onclick={() => aOpenRegistration = !aOpenRegistration}
                  class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out {aOpenRegistration ? 'bg-[var(--color-primary)]' : 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)]'}"
                >
                  <span class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out {aOpenRegistration ? 'translate-x-5' : 'translate-x-0'}"></span>
                </button>
              </div>
            </div>
          </div>

        <!-- STEP 2: MASTER ADMIN ACCOUNT -->
        {:else if currentStep === 2}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">2. Master-Administrator-Konto</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Erstelle den primären Administrator mit vollen Systemrechten</p>
            </div>

            <div class="space-y-3 text-xs">
              <div>
                <label for="a-user" class="block font-semibold text-[var(--text-muted)] mb-1">Admin-Benutzername</label>
                <input id="a-user" type="text" bind:value={aAdminUser} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 font-mono text-[var(--text-main)] outline-none" />
              </div>

              <div>
                <label for="a-mail" class="block font-semibold text-[var(--text-muted)] mb-1">Admin E-Mail</label>
                <input id="a-mail" type="email" bind:value={aAdminEmail} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-[var(--text-main)] outline-none" />
              </div>

              <div>
                <label for="a-pwd" class="block font-semibold text-[var(--text-muted)] mb-1">Master-Passwort (Bcrypt)</label>
                <input id="a-pwd" type="password" bind:value={aAdminPassword} placeholder="Mindestens 12 Zeichen..." class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 text-[var(--text-main)] outline-none" />
              </div>
            </div>
          </div>

        <!-- STEP 3: SEED CATALOGS & DATA ENGINE -->
        {:else if currentStep === 3}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">3. Globale Kataloge und Seed-Daten</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Initialisiere die evidenzbasierten Definitionen in der SQL-Datenbank</p>
            </div>

            <div class="space-y-2.5 text-xs">
              <label class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl flex items-center justify-between cursor-pointer">
                <div>
                  <span class="font-bold text-[var(--text-main)] block">Klinischer Metriken-Katalog (42 Metriken)</span>
                  <span class="text-[0.625rem] text-[var(--text-soft)]">Kardiovaskulär, Lipide, KFA, Schlaf, Glukose</span>
                </div>
                <input type="checkbox" bind:checked={aSeedCatalog} class="w-4 h-4 rounded text-[var(--color-primary)]" />
              </label>

              <label class="p-3 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl flex items-center justify-between cursor-pointer">
                <div>
                  <span class="font-bold text-[var(--text-main)] block">USDA & OpenFoodFacts Basiskatalog</span>
                  <span class="text-[0.625rem] text-[var(--text-soft)]">Über 8.000 verifizierte Standard-Lebensmittel</span>
                </div>
                <input type="checkbox" bind:checked={aSeedFoodDb} class="w-4 h-4 rounded text-[var(--color-primary)]" />
              </label>
            </div>
          </div>

        <!-- STEP 4: AUTHENTICATION PROVIDERS -->
        {:else if currentStep === 4}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">4. Authentifizierungs-Strategie</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Wähle die Auth-Provider-Architektur (Strategy Pattern)</p>
            </div>

            <div class="space-y-2.5 text-xs">
              <div class="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onclick={() => aAuthProvider = 'local'}
                  class="py-3 rounded-xl border text-xs font-semibold cursor-pointer transition-all text-center {aAuthProvider === 'local' ? 'bg-[var(--color-primary)] text-white border-transparent' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                >
                  Lokale DB (Bcrypt)
                </button>
                <button
                  type="button"
                  onclick={() => aAuthProvider = 'oidc'}
                  class="py-3 rounded-xl border text-xs font-semibold cursor-pointer transition-all text-center {aAuthProvider === 'oidc' ? 'bg-[var(--color-primary)] text-white border-transparent' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                >
                  OAuth2 / OIDC
                </button>
                <button
                  type="button"
                  onclick={() => aAuthProvider = 'ldap'}
                  class="py-3 rounded-xl border text-xs font-semibold cursor-pointer transition-all text-center {aAuthProvider === 'ldap' ? 'bg-[var(--color-primary)] text-white border-transparent' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
                >
                  LDAP / AD
                </button>
              </div>

              {#if aAuthProvider === 'oidc'}
                <div>
                  <label for="a-oidc" class="block font-semibold text-[var(--text-muted)] mb-1">OIDC Issuer URL</label>
                  <input id="a-oidc" type="text" bind:value={aOidcIssuer} class="w-full bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5 font-mono text-[var(--text-main)] outline-none" />
                </div>
              {/if}
            </div>
          </div>

        <!-- STEP 5: INSTANCE LAUNCH -->
        {:else if currentStep === 5}
          <div class="space-y-4 animate-[fadeIn_0.15s_ease-out]">
            <div>
              <h2 class="text-base font-extrabold text-[var(--text-main)]">5. Instanz-Start & Telemetrie</h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5">Alle Prüfungen erfolgreich. Die Salus-Instanz ist bereit für den Produktivbetrieb.</p>
            </div>

            <div class="p-4 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-2xl space-y-2 text-xs">
              <div class="flex items-center justify-between">
                <span class="text-[var(--text-muted)]">Instanz-Name:</span>
                <span class="font-bold text-[var(--text-main)]">{aInstanceName}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-[var(--text-muted)]">Föderations-Handle:</span>
                <span class="font-mono text-[var(--color-primary)]">@{aAdminUser}@{aDomain}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-[var(--text-muted)]">Datenqualitäts-Sweep:</span>
                <Badge variant="success">Aktiviert (Alle 6h)</Badge>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-[var(--text-muted)]">Echtzeit-Synchronisation:</span>
                <Badge variant="primary">Aktiv</Badge>
              </div>
            </div>
          </div>
        {/if}

      {/if}

      <!-- Bottom Step Navigation Buttons -->
      <div class="flex items-center justify-between pt-3 border-t border-[var(--border-subtle)]">
        {#if currentStep > 1}
          <Btn variant="secondary" size="sm" onclick={() => currentStep -= 1}>
            &larr; Zurück
          </Btn>
        {:else}
          <Btn variant="ghost" size="sm" onclick={onclose}>
            Schließen
          </Btn>
        {/if}

        {#if currentStep < 5}
          <Btn variant="primary" size="sm" onclick={() => currentStep += 1}>
            Weiter &rarr;
          </Btn>
        {:else}
          <Btn variant="primary" size="sm" onclick={completeSetup}>
            {mode === 'user' ? 'Profil aktivieren & Starten' : 'Instanz starten & Initialisieren'}
          </Btn>
        {/if}
      </div>

    </div>
  </div>
{/if}
