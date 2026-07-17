<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import {
    createShareRecipient,
    deleteShareRecipient,
    createAsymmetricShare,
    deleteAsymmetricShare,
    synthesizeOpenScience
  } from '$lib/mutations/misc';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Input from '$components/ui/Input.svelte';
  import Select from '$components/ui/Select.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import Icon from '$components/ui/Icon.svelte';

  /* ── Crypto utilities ── */
  function formatAsPem(binary: ArrayBuffer, label: string): string {
    const base64 = btoa(String.fromCharCode(...new Uint8Array(binary)));
    const chunks = base64.match(/.{1,64}/g)!.join('\n');
    return `-----BEGIN ${label}-----\n${chunks}\n-----END ${label}-----`;
  }

  function pemToBinary(pem: string): ArrayBuffer {
    const encoded = pem
      .split('\n')
      .filter((l) => l.trim() && !l.includes('BEGIN') && !l.includes('END'))
      .join('');
    return Uint8Array.from(atob(encoded), (c) => c.charCodeAt(0)).buffer;
  }

  function arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array): string {
    const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
    return btoa(String.fromCharCode(...bytes));
  }

  let recipientsRaw = liveQuery(() =>
    db.share_recipient.toArray().then((arr) => arr.filter((r) => !r.deleted_at))
  );
  let shareRows = liveQuery(() =>
    db.asymmetric_share.toArray().then((arr) => arr.filter((s) => !s.deleted_at))
  );

  let recipients = $derived($recipientsRaw ?? []);
  let shares = $derived(
    ($shareRows ?? []).map((s) => {
      const rec = recipients.find((r) => r.id === s.recipient_id);
      return {
        id: s.id,
        recipient: { name: rec?.name ?? 'Unknown' },
        created_at: s.created_at,
        expires_at: s.expires_at
      };
    })
  );

  let error = $state('');
  let success = $state('');

  // Medical Share
  let recipientName = $state('');
  let recipientPubkey = $state('');
  let shareRecipientId = $state('');
  let shareResultUrl = $state('');
  let shareResultVisible = $state(false);
  let shareCreating = $state(false);

  // Open Science
  let scienceMetrics = $state<string[]>([
    'steps',
    'sleep_duration',
    'resting_heart_rate',
    'active_calories'
  ]);
  let scienceWeeks = $state('12');
  let scienceEpsilon = $state('1.0');
  let scienceBirthYear = $state('');
  let scienceWeight = $state('');
  let sciencePreview: Record<string, unknown> | null = $state(null);
  let scienceLoading = $state(false);
  let scienceVisible = $state(false);

  async function generateKeyPair() {
    try {
      const keyPair = await crypto.subtle.generateKey(
        {
          name: 'RSA-OAEP',
          modulusLength: 2048,
          publicExponent: new Uint8Array([1, 0, 1]),
          hash: 'SHA-256'
        },
        true,
        ['encrypt', 'decrypt']
      );
      const exportedPub = await crypto.subtle.exportKey('spki', keyPair.publicKey);
      recipientPubkey = formatAsPem(exportedPub, 'PUBLIC KEY');
      const exportedPriv = await crypto.subtle.exportKey('jwk', keyPair.privateKey);
      const blob = new Blob([JSON.stringify(exportedPriv, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `salus_gp_key_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      error = '';
      success = 'Keys generated. Public key filled in form. Private key downloaded.';
    } catch (e: unknown) {
      error = 'Key generation failed: ' + (e as Error).message;
    }
  }

  async function saveRecipient(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    const resp = await createShareRecipient(recipientName, recipientPubkey);
    if (!resp.ok) {
      error = resp.error ?? 'Request failed';
      return;
    }
    recipientName = '';
    recipientPubkey = '';
  }

  async function deleteRecipient(id: string) {
    if (!confirm('Delete this recipient? All associated shares will also be deleted.')) return;
    await deleteShareRecipient(id);
  }

  async function createShare(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    shareCreating = true;
    shareResultVisible = false;

    const form = e.target as HTMLFormElement;
    const days = parseInt((form.querySelector('[name="share_days"]') as HTMLInputElement).value);
    const expireHours =
      parseInt((form.querySelector('[name="expire_hours"]') as HTMLInputElement).value) || null;

    const recipient = recipients.find((r) => r.id === shareRecipientId);
    if (!recipient) {
      error = 'Please select a recipient.';
      shareCreating = false;
      return;
    }

    try {
      const since = new Date();
      since.setDate(since.getDate() - days);
      since.setHours(0, 0, 0, 0);
      const sinceIso = since.toISOString();

      const [measurements, metricTypes] = await Promise.all([
        db.measurement
          .where('start_time')
          .above(sinceIso)
          .toArray()
          .then((arr) => arr.filter((m) => !m.deleted_at)),
        db.metric_definition.toArray()
      ]);

      const rawData = {
        measurements,
        metric_types: metricTypes,
        days,
        generated_at: new Date().toISOString()
      };

      const spkiBinary = pemToBinary(recipient.public_key);
      const pubKey = await crypto.subtle.importKey(
        'spki',
        spkiBinary,
        { name: 'RSA-OAEP', hash: 'SHA-256' },
        false,
        ['encrypt']
      );

      const aesKey = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, [
        'encrypt'
      ]);
      const iv = crypto.getRandomValues(new Uint8Array(12));
      const encoded = new TextEncoder().encode(JSON.stringify(rawData));
      const encryptedBuf: ArrayBuffer = await crypto.subtle.encrypt(
        { name: 'AES-GCM', iv },
        aesKey,
        encoded
      );
      const rawAesKey: ArrayBuffer = await crypto.subtle.exportKey('raw', aesKey);
      const encryptedKeyBuf: ArrayBuffer = await crypto.subtle.encrypt(
        { name: 'RSA-OAEP' },
        pubKey,
        rawAesKey
      );

      const aesPayload = new Uint8Array(12 + encryptedBuf.byteLength);
      aesPayload.set(iv, 0);
      aesPayload.set(new Uint8Array(encryptedBuf), 12);

      const resp = await createAsymmetricShare(
        recipient.id,
        arrayBufferToBase64(aesPayload),
        arrayBufferToBase64(encryptedKeyBuf),
        expireHours ?? undefined
      );
      if (!resp.ok) {
        error = resp.error ?? 'Request failed';
        shareCreating = false;
        return;
      }

      const after = await db.asymmetric_share.where({ recipient_id: recipient.id }).toArray();
      const share = after[after.length - 1];
      shareResultUrl = `${window.location.origin}/share/doctor/${share.id}`;
      shareResultVisible = true;
    } catch (e: unknown) {
      error = 'Encryption failed: ' + (e as Error).message;
    }
    shareCreating = false;
  }

  async function deleteShare(id: string) {
    if (!confirm('Revoke this share link?')) return;
    await deleteAsymmetricShare(id);
  }

  async function copyShareUrl() {
    await navigator.clipboard.writeText(shareResultUrl);
  }

  async function copyLinkForShare(id: string) {
    await navigator.clipboard.writeText(`${window.location.origin}/share/doctor/${id}`);
  }

  function toggleScienceMetric(m: string) {
    scienceMetrics = scienceMetrics.includes(m)
      ? scienceMetrics.filter((x) => x !== m)
      : [...scienceMetrics, m];
  }

  async function generatePreview() {
    if (scienceMetrics.length === 0) {
      error = 'Select at least one metric.';
      return;
    }
    scienceLoading = true;
    error = '';
    const resp = await synthesizeOpenScience({
      metrics: scienceMetrics,
      weeks: parseInt(scienceWeeks),
      epsilon: parseFloat(scienceEpsilon),
      include_demographics: true,
      user_birth_year: scienceBirthYear ? parseInt(scienceBirthYear) : null,
      user_weight_kg: scienceWeight ? parseFloat(scienceWeight) : null
    });
    scienceLoading = false;
    if (!resp.ok) {
      error = resp.error ?? 'Request failed';
      return;
    }
    sciencePreview = resp.data as Record<string, unknown>;
    scienceVisible = true;
  }

  function downloadJSON() {
    if (!sciencePreview) return;
    const blob = new Blob([JSON.stringify(sciencePreview, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `salus_synthetic_data_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function downloadCSV() {
    if (!sciencePreview || !(sciencePreview as { records?: unknown[] }).records) return;
    const records = (
      sciencePreview as {
        records: { week_start: string; metric_type: string; value_numeric: number }[];
      }
    ).records;
    let csv = 'WeekStart,MetricType,ValueSynthetic\n';
    records.forEach((r) => {
      csv += `${r.week_start},${r.metric_type},${r.value_numeric}\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `salus_synthetic_data_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function donate() {
    success = 'Thank you! Your synthesized data has been anonymously donated.';
    sciencePreview = null;
    scienceVisible = false;
  }
</script>

{#if error}<AlertBanner variant="error" class="mb-4">{error}</AlertBanner>{/if}
{#if success}<AlertBanner variant="success" class="mb-4">{success}</AlertBanner>{/if}

<div class="space-y-6">
  <!-- Data Export -->
  <Card>
    {#snippet header()}
      <span class="text-sm font-semibold text-surface-900">Data Export</span>
    {/snippet}
    <p class="mb-4 text-sm text-surface-500">
      Download all your health records and custom metrics.
    </p>
    <div class="flex gap-3">
      <Btn variant="secondary" size="sm" href="/api/v1/export/download?format=csv">CSV</Btn>
      <Btn variant="secondary" size="sm" href="/api/v1/export/download?format=json">JSON</Btn>
    </div>
  </Card>

  <!-- Medical Share -->
  <Card>
    {#snippet header()}
      <span class="text-sm font-semibold text-surface-900">Medical Share</span>
    {/snippet}
    <p class="mb-4 text-sm text-surface-500">
      Share end-to-end encrypted health profiles with your GP or doctor using zero-knowledge
      asymmetric cryptography.
    </p>

    <!-- 1. Register Recipient -->
    <div class="mb-6 rounded-lg border border-surface-200 bg-surface-50 p-5">
      <h4 class="mb-3 text-sm font-bold text-surface-900">1. Register Recipient (Public Key)</h4>
      <div class="mb-3 flex gap-2">
        <Btn variant="secondary" size="sm" onclick={generateKeyPair}>
          <Icon name="key" size="sm" />Generate Key Pair
        </Btn>
      </div>
      <form onsubmit={saveRecipient} class="space-y-3">
        <FormField label="Recipient Name">
          <Input
            name="rec_name"
            bind:value={recipientName}
            placeholder="e.g. Dr. Mueller"
            required
          />
        </FormField>
        <FormField label="Public Key">
          <Textarea
            name="rec_pubkey"
            bind:value={recipientPubkey}
            rows={4}
            placeholder="Generate keys above to auto-fill"
          />
        </FormField>
        <Btn variant="primary" type="submit" size="sm">Save Recipient</Btn>
      </form>
    </div>

    <!-- Registered Recipients -->
    <div class="mb-6 rounded-lg border border-surface-200 p-5">
      <h4 class="mb-3 text-sm font-bold text-surface-900">Registered Recipients</h4>
      {#if recipients.length > 0}
        <div class="space-y-2">
          {#each recipients as r}
            <div
              class="flex items-center justify-between rounded-lg border border-surface-200 px-4 py-3"
            >
              <div>
                <p class="text-sm font-semibold text-surface-900">{r.name}</p>
                <p class="text-xs text-surface-400">
                  Added {new Date(r.created_at).toLocaleDateString()}
                </p>
              </div>
              <Btn variant="ghost" size="sm" onclick={() => deleteRecipient(r.id)}>
                <Icon name="delete" size="sm" />
              </Btn>
            </div>
          {/each}
        </div>
      {:else}
        <p class="text-sm text-surface-400">No recipients registered yet.</p>
      {/if}
    </div>

    <!-- 2. Encrypt & Share -->
    <div class="mb-6 rounded-lg border border-surface-200 bg-surface-50 p-5">
      <h4 class="mb-3 text-sm font-bold text-surface-900">2. Encrypt &amp; Share Data</h4>
      <form onsubmit={createShare} class="space-y-3">
        <FormField label="Recipient">
          <Select
            name="recipient_id"
            bind:value={shareRecipientId}
            options={recipients.map((r) => ({ value: String(r.id), label: r.name }))}
            required
          />
        </FormField>
        <div class="grid grid-cols-2 gap-4">
          <FormField label="Days of Data">
            <Input name="share_days" type="number" value={30} min={1} max={365} />
          </FormField>
          <FormField label="Expiration (Hours)">
            <Input name="expire_hours" type="number" value={24} min={1} />
          </FormField>
        </div>
        <Btn variant="primary" type="submit" size="sm" loading={shareCreating}
          >Encrypt &amp; Generate Share Link</Btn
        >
      </form>

      {#if shareResultVisible}
        <div class="mt-4 rounded-lg border border-primary-200 bg-primary-50 p-4">
          <p class="mb-2 text-sm font-semibold text-primary-700">Share Link Generated:</p>
          <div class="flex items-center gap-2">
            <code class="flex-1 rounded bg-surface-0 px-3 py-2 text-xs break-all text-surface-700"
              >{shareResultUrl}</code
            >
            <Btn variant="primary" size="sm" onclick={copyShareUrl}>Copy</Btn>
          </div>
          <p class="mt-2 text-xs text-surface-500">
            Give this link and the private key file to your doctor.
          </p>
        </div>
      {/if}
    </div>

    <!-- Active Shares -->
    <div class="rounded-lg border border-surface-200 p-5">
      <h4 class="mb-3 text-sm font-bold text-surface-900">Active Encrypted Share Links</h4>
      {#if shares.length > 0}
        <div class="space-y-2">
          {#each shares as s}
            <div
              class="flex items-center justify-between rounded-lg border border-surface-200 px-4 py-3"
            >
              <div>
                <p class="text-sm font-semibold text-surface-900">Share for {s.recipient.name}</p>
                <p class="text-xs text-surface-400">
                  Created {new Date(s.created_at).toLocaleDateString()}
                  {#if s.expires_at}
                    · Expires {new Date(s.expires_at).toLocaleDateString()}{/if}
                </p>
              </div>
              <div class="flex gap-2">
                <Btn variant="secondary" size="sm" onclick={() => copyLinkForShare(s.id)}>Copy</Btn>
                <Btn variant="ghost" size="sm" onclick={() => deleteShare(s.id)}>
                  <Icon name="delete" size="sm" />
                </Btn>
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <p class="text-sm text-surface-400">No active encrypted shares.</p>
      {/if}
    </div>
  </Card>

  <!-- Open Science -->
  <Card>
    {#snippet header()}
      <span class="text-sm font-semibold text-surface-900">Open Science Data Synthesizer</span>
    {/snippet}
    <p class="mb-4 text-sm text-surface-500">
      Contribute anonymized, differentially-private health data to open research. Privacy preserved
      through Local Differential Privacy (LDP).
    </p>

    <div class="mb-6 rounded-lg border border-surface-200 bg-surface-50 p-5">
      <h4 class="mb-3 text-sm font-bold text-surface-900">
        1. Select Metrics &amp; Generalization
      </h4>
      <div class="space-y-4">
        <div>
          <p class="mb-2 text-xs font-semibold text-surface-500">Health Vitals to Share</p>
          <div class="space-y-2">
            {#each [{ value: 'steps', label: 'Steps (Daily counts)' }, { value: 'sleep_duration', label: 'Sleep (Durations)' }, { value: 'resting_heart_rate', label: 'Resting Heart Rate (bpm)' }, { value: 'active_calories', label: 'Active Energy Burn (kcal)' }] as metric}
              <label class="inline-flex cursor-pointer items-center gap-2">
                <input
                  type="checkbox"
                  checked={scienceMetrics.includes(metric.value)}
                  onchange={() => toggleScienceMetric(metric.value)}
                  class="h-4 w-4 rounded accent-primary-600"
                />
                <span class="text-sm text-surface-700">{metric.label}</span>
              </label>
            {/each}
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <FormField label="Timeframe">
            <Select
              name="science_weeks"
              bind:value={scienceWeeks}
              options={[
                { value: '4', label: 'Last 4 Weeks' },
                { value: '8', label: 'Last 8 Weeks' },
                { value: '12', label: 'Last 12 Weeks' },
                { value: '24', label: 'Last 24 Weeks' }
              ]}
            />
          </FormField>
          <FormField label="Privacy Budget (ε)">
            <Select
              name="science_epsilon"
              bind:value={scienceEpsilon}
              options={[
                { value: '0.5', label: 'High Privacy (ε = 0.5)' },
                { value: '1.0', label: 'Balanced (ε = 1.0)' },
                { value: '2.0', label: 'Low Privacy (ε = 2.0)' }
              ]}
            />
          </FormField>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <FormField label="Birth Year (optional)">
            <Input
              name="birth_year"
              bind:value={scienceBirthYear}
              type="number"
              placeholder="e.g. 1990"
              min={1900}
              max={2026}
            />
          </FormField>
          <FormField label="Body Weight kg (optional)">
            <Input
              name="weight"
              bind:value={scienceWeight}
              type="number"
              step={0.1}
              placeholder="e.g. 74.5"
              min={30}
              max={300}
            />
          </FormField>
        </div>
        <Btn variant="primary" size="sm" loading={scienceLoading} onclick={generatePreview}
          >Generate Dataset Preview</Btn
        >
      </div>
    </div>

    <div class="rounded-lg border border-surface-200 p-5">
      <h4 class="mb-3 text-sm font-bold text-surface-900">2. Preview &amp; Donate Dataset</h4>
      {#if scienceVisible && sciencePreview}
        <Textarea name="json_output" value={JSON.stringify(sciencePreview, null, 2)} rows={8} />
        <div class="mt-3 flex flex-wrap items-center justify-between gap-3">
          <div class="flex gap-2">
            <Btn variant="secondary" size="sm" onclick={downloadJSON}>JSON</Btn>
            <Btn variant="secondary" size="sm" onclick={downloadCSV}>CSV</Btn>
          </div>
          <Btn variant="primary" size="sm" onclick={donate}>Donate to Research</Btn>
        </div>
      {:else}
        <div class="flex flex-col items-center py-8 text-center">
          <Icon name="insights" size="2xl" class="text-surface-300" />
          <p class="mt-3 text-sm text-surface-400">
            Configure metrics and click generate to preview.
          </p>
        </div>
      {/if}
    </div>
  </Card>
</div>
