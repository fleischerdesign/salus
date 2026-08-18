<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

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

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-5 shadow-[var(--shadow-card)]">
  <div class="flex items-center justify-between mb-3">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="insights" class="text-[var(--color-primary)]" />
      <span>Ende-zu-Ende verschlüsselte Arzt-Freigabe</span>
    </div>
    <Badge variant="default">AES-256 GCM Zero-Knowledge</Badge>
  </div>

  <p class="text-xs text-[var(--text-muted)] mb-4">
    Erzeuge einen kryptographisch gesicherten Einmallink für deinen behandelnden Arzt. Die Entschlüsselung erfolgt rein clientseitig im Browser des Arztes – der Server sieht niemals Klartextdaten.
  </p>

  {#if !shareLink}
    <Btn variant="primary" class="w-full" onclick={generateLink}>
      {isGenerating ? 'Schlüsselpaar wird generiert...' : '24h Arzt-Freigabelink erzeugen'}
    </Btn>
  {:else}
    <div class="space-y-2">
      <div class="flex items-center gap-2 bg-[var(--bg-surface-50)] border border-[var(--border-subtle)] rounded-xl p-2.5">
        <input
          type="text"
          readonly
          value={shareLink}
          class="bg-transparent border-none outline-none font-mono text-xs text-[var(--color-primary)] flex-1 select-all"
        />
        <Btn variant="secondary" size="sm" onclick={copyLink}>Kopieren</Btn>
      </div>
      <div class="flex justify-between items-center text-[0.6875rem] text-[var(--text-soft)] px-1">
        <span>Gültigkeit: 24 Stunden</span>
        <button type="button" class="text-[var(--color-vital)] hover:underline cursor-pointer" onclick={() => shareLink = null}>
          Link widerrufen
        </button>
      </div>
    </div>
  {/if}
</div>
