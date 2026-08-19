<script lang="ts">
  import Btn from '../ui/Btn.svelte';
  import Modal from '../ui/Modal.svelte';

  let { open = false, onclose } = $props<{
    open: boolean;
    onclose: () => void;
  }>();
</script>

<Modal
  {open}
  title="Klinischer Längsschnittbericht"
  subtitle="ISO 27001 / DIN EN 15224 • Validierter PDF/A Export"
  icon="description"
  size="lg"
  {onclose}
>
  <div class="space-y-5 text-xs">
    <!-- Printable Document Preview -->
    <div
      class="space-y-5 rounded-2xl border border-slate-200 bg-white p-6 text-slate-800 shadow-inner"
    >
      <!-- Letterhead -->
      <div class="flex items-start justify-between border-b border-slate-200 pb-4">
        <div>
          <h1 class="text-base font-black tracking-tight text-slate-900">SALUS HEALTH RECORD</h1>
          <p class="mt-0.5 font-mono text-[0.6875rem] text-slate-500">
            Patient: Philipp • Geb: 1994 • ID: #SAL-8402-E2EE
          </p>
        </div>
        <div class="text-right font-mono text-[0.6875rem] text-slate-500">
          <div>Erstellt am: 14.08.2026</div>
          <div>Validierungs-Hash: SHA-256 (Verifiziert)</div>
        </div>
      </div>

      <!-- Clinical Summary -->
      <div>
        <h2 class="mb-2 text-xs font-bold tracking-wider text-slate-900 uppercase">
          1. Kardiovaskuläre und Metabolische Stabilität
        </h2>
        <table class="w-full border-collapse border border-slate-200 text-left">
          <thead class="bg-slate-50">
            <tr>
              <th class="border border-slate-200 p-2">Parameter</th>
              <th class="border border-slate-200 p-2">Aktueller Wert</th>
              <th class="border border-slate-200 p-2">Referenz (ESC/EAS)</th>
              <th class="border border-slate-200 p-2">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="border border-slate-200 p-2 font-bold">Blutdruck (7T-EMA)</td>
              <td class="border border-slate-200 p-2 font-mono">119 / 77 mmHg</td>
              <td class="border border-slate-200 p-2 font-mono">&lt; 120 / 80 mmHg</td>
              <td class="border border-slate-200 p-2 font-bold text-emerald-700">Optimal</td>
            </tr>
            <tr>
              <td class="border border-slate-200 p-2 font-bold">Ruhepuls</td>
              <td class="border border-slate-200 p-2 font-mono">64 bpm</td>
              <td class="border border-slate-200 p-2 font-mono">60–80 bpm</td>
              <td class="border border-slate-200 p-2 font-bold text-emerald-700">Optimal</td>
            </tr>
            <tr>
              <td class="border border-slate-200 p-2 font-bold">LDL-Cholesterin</td>
              <td class="border border-slate-200 p-2 font-mono">68 mg/dL</td>
              <td class="border border-slate-200 p-2 font-mono">&lt; 70 mg/dL</td>
              <td class="border border-slate-200 p-2 font-bold text-emerald-700">Optimal</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Doctor Signature Area -->
      <div
        class="flex items-end justify-between border-t border-slate-200 pt-4 font-mono text-[0.6875rem] text-slate-500"
      >
        <div>
          <div>Klinische Software: Salus Health Platform v2.0</div>
          <div>Zero-Knowledge End-to-End Cryptography</div>
        </div>
        <div class="w-48 border-t border-slate-400 pt-1 text-center text-slate-600">
          Unterschrift / Stempel Arzt
        </div>
      </div>
    </div>

    <!-- Action Footer -->
    <div class="flex items-center justify-between border-t border-border-subtle pt-3">
      <span class="font-mono text-xs text-text-muted">Format: PDF/A-1b (Langzeitarchiv)</span>
      <div class="flex gap-2">
        <Btn variant="secondary" size="md" onclick={onclose}>Schließen</Btn>
        <Btn
          variant="primary"
          size="md"
          onclick={() => {
            alert('PDF wird heruntergeladen...');
            onclose();
          }}
        >
          PDF Herunterladen (DIN A4)
        </Btn>
      </div>
    </div>
  </div>
</Modal>
