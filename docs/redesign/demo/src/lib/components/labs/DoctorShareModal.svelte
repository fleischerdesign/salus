<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let {
    open = false,
    onclose
  } = $props<{
    open: boolean;
    onclose: () => void;
  }>();

  let validityHours = $state(24);
  let selectedPanels = $state<string[]>(['lipids', 'metabolic', 'inflammation']);
  let shareGenerated = $state(true);
  let shareLink = $state('https://salus.local/shares/sh_9f82ab#k_7x2m91pq4');
  let pinCode = $state('4829');

  function togglePanel(id: string) {
    if (selectedPanels.includes(id)) {
      selectedPanels = selectedPanels.filter(p => p !== id);
    } else {
      selectedPanels.push(id);
    }
  }

  function copyLink() {
    navigator.clipboard?.writeText(shareLink);
    alert('Verschlüsselter Arzt-Freigabelink in die Zwischenablage kopiert!');
  }
</script>

{#if open}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-60 flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-6 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold">
            <Icon name="labs" size={22} />
          </div>
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Ende-zu-Ende Arzt-Freigabe</h2>
            <p class="text-xs text-[var(--text-muted)]">Kryptografisch gesicherter, zeitlich begrenzter Zugang für medizinisches Fachpersonal</p>
          </div>
        </div>
        <button
          type="button"
          onclick={onclose}
          class="text-[var(--text-muted)] hover:text-[var(--text-main)] text-xl cursor-pointer"
        >
          &times;
        </button>
      </div>

      <!-- Zero-Knowledge Security Badge -->
      <div class="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center gap-2.5 text-xs text-emerald-500 font-semibold">
        <Icon name="check" size={16} class="shrink-0" />
        <span>Zero-Knowledge: Der Schlüssel liegt im URL-Hash und wird niemals an den Salus-Server übertragen.</span>
      </div>

      <!-- Ephemeral QR Code Display -->
      <div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 flex flex-col items-center justify-center text-center space-y-3">
        <!-- SVG Generated QR Code Placeholder -->
        <div class="w-40 h-40 bg-white p-2 rounded-2xl shadow-sm border border-slate-200 flex items-center justify-center relative">
          <!-- Simple Clean QR pattern representation -->
          <svg viewBox="0 0 100 100" class="w-full h-full text-slate-900" fill="currentColor">
            <path d="M10 10h30v30h-30z M15 15v20h20v-20z M20 20h10v10h-10z" />
            <path d="M60 10h30v30h-30z M65 15v20h20v-20z M70 20h10v10h-10z" />
            <path d="M10 60h30v30h-30z M15 65v20h20v-20z M20 70h10v10h-10z" />
            <rect x="45" y="10" width="8" height="8" />
            <rect x="45" y="25" width="8" height="8" />
            <rect x="45" y="45" width="10" height="10" />
            <rect x="60" y="45" width="8" height="8" />
            <rect x="75" y="45" width="15" height="8" />
            <rect x="60" y="60" width="10" height="10" />
            <rect x="80" y="60" width="10" height="10" />
            <rect x="60" y="80" width="30" height="10" />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="w-8 h-8 rounded-full bg-[var(--color-primary)] text-white font-extrabold text-xs flex items-center justify-center shadow-md">
              S
            </div>
          </div>
        </div>

        <div>
          <span class="text-xs font-bold text-[var(--text-main)] block">Arzt-Scan QR-Code</span>
          <span class="text-[0.6875rem] text-[var(--text-muted)]">Der Arzt kann den Code mit jedem Tablet oder Smartphone scannen</span>
        </div>

        <!-- PIN Code -->
        <div class="flex items-center gap-2 pt-1">
          <span class="text-xs text-[var(--text-soft)]">Sicherheits-PIN:</span>
          <span class="px-3 py-1 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-lg font-bold tracking-widest text-[var(--color-primary)]">
            {pinCode}
          </span>
        </div>
      </div>

      <!-- Validity & Scope Selection -->
      <div class="space-y-3 text-xs">
        <div class="flex items-center justify-between">
          <span class="font-semibold text-[var(--text-muted)]">Gültigkeitsdauer</span>
          <div class="flex gap-1.5">
            {#each [24, 72, 168] as h}
              <button
                type="button"
                onclick={() => validityHours = h}
                class="px-2.5 py-1 rounded-xl font-bold cursor-pointer transition-all {validityHours === h ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] text-[var(--text-muted)]'}"
              >
                {h === 24 ? '24h' : h === 72 ? '3 Tage' : '7 Tage'}
              </button>
            {/each}
          </div>
        </div>

        <!-- Included Panels -->
        <div>
          <span class="block font-semibold text-[var(--text-muted)] mb-1.5">Freigegebene Laborprofile</span>
          <div class="grid grid-cols-2 gap-2">
            {#each [
              { id: 'lipids', label: 'Lipidprofil und ApoB', count: '5 Marker' },
              { id: 'metabolic', label: 'Glukosestoffwechsel', count: '4 Marker' },
              { id: 'inflammation', label: 'hs-CRP und Entzündung', count: '3 Marker' },
              { id: 'hormones', label: 'Hormone und Schilddrüse', count: '6 Marker' }
            ] as p}
              <button
                type="button"
                onclick={() => togglePanel(p.id)}
                class="p-2.5 rounded-xl border text-left cursor-pointer transition-all {selectedPanels.includes(p.id) ? 'bg-[var(--color-primary)]/10 border-[var(--color-primary)]' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
              >
                <div class="font-bold text-[var(--text-main)]">{p.label}</div>
                <div class="text-[0.625rem] text-[var(--text-soft)]">{p.count}</div>
              </button>
            {/each}
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center justify-between pt-2 border-t border-[var(--border-subtle)]">
        <Btn variant="secondary" size="sm" onclick={copyLink}>
           Link kopieren
        </Btn>
        <Btn variant="primary" size="sm" onclick={onclose}>
          Fertig
        </Btn>
      </div>

    </div>
  </div>
{/if}
