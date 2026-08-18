<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Btn from '../ui/Btn.svelte';
  import Modal from '../ui/Modal.svelte';

  let { open = false, onclose } = $props<{
    open: boolean;
    onclose: () => void;
  }>();

  let validityHours = $state(24);
  let selectedPanels = $state<string[]>(['lipids', 'metabolic', 'inflammation']);
  let shareLink = $state('https://salus.local/shares/sh_9f82ab#k_7x2m91pq4');
  let pinCode = $state('4829');

  function togglePanel(id: string) {
    if (selectedPanels.includes(id)) {
      selectedPanels = selectedPanels.filter((p) => p !== id);
    } else {
      selectedPanels.push(id);
    }
  }

  function copyLink() {
    navigator.clipboard?.writeText(shareLink);
    alert('Verschlüsselter Arzt-Freigabelink in die Zwischenablage kopiert!');
  }
</script>

<Modal
  {open}
  title="Ende-zu-Ende Arzt-Freigabe"
  subtitle="Kryptografisch gesicherter, zeitlich begrenzter Zugang für medizinisches Fachpersonal"
  icon="labs"
  size="md"
  {onclose}
>
  <div class="space-y-5 text-xs">
    <!-- Zero-Knowledge Security Badge -->
    <div
      class="flex items-center gap-2.5 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-3 text-xs font-semibold text-emerald-500"
    >
      <Icon name="check" size={16} class="shrink-0" />
      <span
        >Zero-Knowledge: Der Schlüssel liegt im URL-Hash und wird niemals an den Salus-Server
        übertragen.</span
      >
    </div>

    <!-- Ephemeral QR Code Display -->
    <div
      class="flex flex-col items-center justify-center space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 text-center"
    >
      <!-- SVG Generated QR Code -->
      <div
        class="relative flex h-40 w-40 items-center justify-center rounded-2xl border border-slate-200 bg-white p-2 shadow-sm"
      >
        <svg viewBox="0 0 100 100" class="h-full w-full text-slate-900" fill="currentColor">
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
          <div
            class="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-primary)] text-xs font-extrabold text-white shadow-md"
          >
            S
          </div>
        </div>
      </div>

      <div>
        <span class="block text-xs font-bold text-[var(--text-main)]">Arzt-Scan QR-Code</span>
        <span class="text-[0.6875rem] text-[var(--text-muted)]"
          >Der Arzt kann den Code mit jedem Tablet oder Smartphone scannen</span
        >
      </div>

      <!-- PIN Code -->
      <div class="flex items-center gap-2 pt-1">
        <span class="text-xs text-[var(--text-soft)]">Sicherheits-PIN:</span>
        <span
          class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-3 py-1 font-bold tracking-widest text-[var(--color-primary)]"
        >
          {pinCode}
        </span>
      </div>
    </div>

    <!-- Validity & Scope Selection -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <span class="font-semibold text-[var(--text-muted)]">Gültigkeitsdauer</span>
        <div class="flex gap-1.5">
          {#each [24, 72, 168] as h}
            <button
              type="button"
              onclick={() => (validityHours = h)}
              class="cursor-pointer rounded-xl px-2.5 py-1 font-bold transition-all {validityHours ===
              h
                ? 'bg-[var(--color-primary)] text-white'
                : 'border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)]'}"
            >
              {h === 24 ? '24h' : h === 72 ? '3 Tage' : '7 Tage'}
            </button>
          {/each}
        </div>
      </div>

      <!-- Included Panels -->
      <div>
        <span class="mb-1.5 block font-semibold text-[var(--text-muted)]"
          >Freigegebene Laborprofile</span
        >
        <div class="grid grid-cols-2 gap-2">
          {#each [{ id: 'lipids', label: 'Lipidprofil und ApoB', count: '5 Marker' }, { id: 'metabolic', label: 'Glukosestoffwechsel', count: '4 Marker' }, { id: 'inflammation', label: 'hs-CRP und Entzündung', count: '3 Marker' }, { id: 'hormones', label: 'Hormone und Schilddrüse', count: '6 Marker' }] as p}
            <button
              type="button"
              onclick={() => togglePanel(p.id)}
              class="cursor-pointer rounded-xl border p-2.5 text-left transition-all {selectedPanels.includes(
                p.id
              )
                ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10'
                : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)]'}"
            >
              <div class="font-bold text-[var(--text-main)]">{p.label}</div>
              <div class="text-[0.625rem] text-[var(--text-soft)]">{p.count}</div>
            </button>
          {/each}
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-3">
      <Btn variant="secondary" size="md" onclick={copyLink}>Link kopieren</Btn>
      <Btn variant="primary" size="md" onclick={onclose}>Fertig</Btn>
    </div>
  </div>
</Modal>
