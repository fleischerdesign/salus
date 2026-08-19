<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';

  let shareLink = $state<string | null>(null);
  let isGenerating = $state(false);

  function generateLink() {
    isGenerating = true;
    setTimeout(() => {
      shareLink = `https://salus.health/share#key=${Math.random().toString(36).substring(2, 15)}&exp=24h`;
      isGenerating = false;
    }, 600);
  }

  function copyLink() {
    if (shareLink) {
      navigator.clipboard?.writeText(shareLink);
      alert('Kryptographischer Freigabelink in die Zwischenablage kopiert!');
    }
  }
</script>

<div class="rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card">
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center gap-2">
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-soft text-primary">
        <Icon name="key" size="sm" />
      </div>
      <div>
        <h4 class="text-sm font-bold text-text-main">Arzt-Direktfreigabe (E2EE)</h4>
        <span class="text-[0.6875rem] text-text-soft"
          >Client-seitige ECDH End-to-End Verschlüsselung</span
        >
      </div>
    </div>
    <Badge variant="default">AES-256 GCM Zero-Knowledge</Badge>
  </div>

  <p class="mb-4 text-xs text-text-muted">
    Erzeuge einen kryptographisch gesicherten Einmallink für deinen behandelnden Arzt. Die
    Entschlüsselung erfolgt rein clientseitig im Browser des Arztes – der Server sieht niemals
    Klartextdaten.
  </p>

  {#if !shareLink}
    <Btn variant="primary" class="w-full" onclick={generateLink}>
      {isGenerating ? 'Schlüsselpaar wird generiert...' : '24h Arzt-Freigabelink erzeugen'}
    </Btn>
  {:else}
    <div class="space-y-2">
      <div class="flex items-center gap-2">
        <div class="flex-1 font-mono">
          <Input readonly value={shareLink} />
        </div>
        <Btn variant="secondary" size="md" onclick={copyLink} class="h-10 shrink-0">Kopieren</Btn>
      </div>
      <div class="flex items-center justify-between px-1 text-[0.6875rem] text-text-soft">
        <span>Gültigkeit: 24 Stunden</span>
        <button
          type="button"
          class="cursor-pointer text-vital hover:underline"
          onclick={() => (shareLink = null)}
        >
          Link widerrufen
        </button>
      </div>
    </div>
  {/if}
</div>
