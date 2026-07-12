<script lang="ts">
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Icon from '$components/ui/Icon.svelte';

  let exportLoading = $state(false);

  function handleExport() {
    exportLoading = true;
    window.location.href = '/api/v1/export/download?format=zip';
    setTimeout(() => (exportLoading = false), 1000);
  }
</script>

<div class="space-y-6">
  <!-- Privacy Policy -->
  <Card>
    <div class="flex items-start gap-4">
      <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
        <Icon name="shield" size="sm" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-surface-900">Local First Policy</h3>
        <p class="mt-2 text-sm leading-relaxed text-surface-500">
          Your health data stays on your device and server. No third-party analytics, no cloud intermediaries, and no telemetry unless you explicitly opt in.
        </p>
        <div class="mt-4 rounded-lg border border-surface-200 bg-surface-50 p-4">
          <h4 class="text-sm font-semibold text-surface-700">Zero-Knowledge Protocol Assurance</h4>
          <p class="mt-1 text-sm text-surface-500">
            Medical shares use end-to-end encryption (AES-GCM + RSA-OAEP). Your private key never leaves your browser.
          </p>
        </div>
      </div>
    </div>
  </Card>

  <!-- Security & Audit -->
  <Card padding={false}>
    {#snippet header()}
      <span class="text-sm font-semibold text-surface-900">Security &amp; Audit</span>
    {/snippet}
    <div class="divide-y divide-surface-100">
      <div class="flex items-center justify-between px-5 py-4">
        <div>
          <p class="text-sm font-medium text-surface-700">Two-Factor Authentication (2FA)</p>
          <p class="text-xs text-surface-400">Enhance security using standard TOTP authenticator apps.</p>
        </div>
        <Badge variant="default">Coming Soon</Badge>
      </div>
      <div class="flex items-center justify-between px-5 py-4">
        <div>
          <p class="text-sm font-medium text-surface-700">Security Log Audit</p>
          <p class="text-xs text-surface-400">Review recent login timestamps, IP locations, and API requests.</p>
        </div>
        <Badge variant="default">Coming Soon</Badge>
      </div>
    </div>
  </Card>

  <!-- Data Portability -->
  <Card>
    {#snippet header()}
      <span class="text-sm font-semibold text-surface-900">Data Portability &amp; Backup</span>
    {/snippet}
    <p class="mb-4 text-sm text-surface-500">
      Under GDPR Article 20, you have the right to receive your data in a structured, machine-readable format. Export a complete ZIP archive of your health records and restore from a backup.
    </p>
    <div class="flex flex-wrap items-center gap-4">
      <Btn variant="primary" loading={exportLoading} onclick={handleExport}>
        <Icon name="download" size="sm" />Export Data (ZIP)
      </Btn>
      <div class="flex items-center gap-2">
        <input type="file" accept=".zip" class="text-sm text-surface-500 file:mr-3 file:rounded-md file:border file:border-surface-300 file:bg-surface-50 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-surface-700 hover:file:bg-surface-100" />
        <Btn variant="secondary" size="sm">Import / Restore</Btn>
      </div>
    </div>
  </Card>
</div>
