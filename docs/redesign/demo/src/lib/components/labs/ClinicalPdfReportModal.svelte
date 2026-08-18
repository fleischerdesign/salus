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
</script>

{#if open}
  <div
    class="fixed inset-0 bg-black/70 backdrop-blur-sm z-100 flex items-center justify-center p-4"
    onclick={(e) => {
      if (e.target === e.currentTarget) onclose();
    }}
    role="presentation"
  >
    <div class="bg-white text-slate-900 border border-slate-200 rounded-2xl max-w-[650px] w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-sans">
      <!-- Modal Header -->
      <div class="bg-slate-50 border-b border-slate-200 px-6 py-3.5 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-xs font-mono font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded">ISO 27001 / DIN EN 15224</span>
          <span class="text-xs font-bold text-slate-700">Klinischer Längsschnittbericht</span>
        </div>
        <button type="button" class="text-slate-400 hover:text-slate-700 font-bold text-sm cursor-pointer" onclick={onclose}>&times;</button>
      </div>

      <!-- Printable Document Preview -->
      <div class="p-8 overflow-y-auto space-y-6 text-xs text-slate-800 bg-white">
        <!-- Letterhead -->
        <div class="flex justify-between items-start border-b border-slate-200 pb-4">
          <div>
            <h1 class="text-lg font-black tracking-tight text-slate-900">SALUS HEALTH RECORD</h1>
            <p class="text-[0.6875rem] text-slate-500 font-mono">Patient: Philipp • Geb: 1994 • ID: #SAL-8402-E2EE</p>
          </div>
          <div class="text-right text-[0.6875rem] font-mono text-slate-500">
            <div>Erstellt am: 14.08.2026</div>
            <div>Validierungs-Hash: SHA-256 (Verifiziert)</div>
          </div>
        </div>

        <!-- Clinical Summary -->
        <div>
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-900 mb-2">1. Kardiovaskuläre und Metabolische Stabilität</h2>
          <table class="w-full border-collapse border border-slate-200 text-left">
            <thead class="bg-slate-50">
              <tr>
                <th class="p-2 border border-slate-200">Parameter</th>
                <th class="p-2 border border-slate-200">Aktueller Wert</th>
                <th class="p-2 border border-slate-200">Referenz (ESC/EAS)</th>
                <th class="p-2 border border-slate-200">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="p-2 border border-slate-200 font-bold">Blutdruck (7T-EMA)</td>
                <td class="p-2 border border-slate-200 font-mono">119 / 77 mmHg</td>
                <td class="p-2 border border-slate-200 font-mono">&lt; 120 / 80 mmHg</td>
                <td class="p-2 border border-slate-200 text-emerald-700 font-bold">Optimal</td>
              </tr>
              <tr>
                <td class="p-2 border border-slate-200 font-bold">Ruhepuls</td>
                <td class="p-2 border border-slate-200 font-mono">64 bpm</td>
                <td class="p-2 border border-slate-200 font-mono">60–80 bpm</td>
                <td class="p-2 border border-slate-200 text-emerald-700 font-bold">Optimal</td>
              </tr>
              <tr>
                <td class="p-2 border border-slate-200 font-bold">LDL-Cholesterin</td>
                <td class="p-2 border border-slate-200 font-mono">68 mg/dL</td>
                <td class="p-2 border border-slate-200 font-mono">&lt; 70 mg/dL</td>
                <td class="p-2 border border-slate-200 text-emerald-700 font-bold">Optimal</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Doctor Signature Area -->
        <div class="pt-4 border-t border-slate-200 flex justify-between items-end text-[0.6875rem] text-slate-500 font-mono">
          <div>
            <div>Klinische Software: Salus Health Platform v2.0</div>
            <div>Zero-Knowledge End-to-End Cryptography</div>
          </div>
          <div class="border-t border-slate-400 pt-1 w-48 text-center">
            Unterschrift / Stempel Arzt
          </div>
        </div>
      </div>

      <!-- Action Footer -->
      <div class="bg-slate-50 border-t border-slate-200 p-4 flex justify-between items-center">
        <span class="text-xs text-slate-500 font-mono">Format: PDF/A-1b (Langzeitarchiv)</span>
        <div class="flex gap-2">
          <button type="button" class="btn btn-secondary" onclick={onclose}>Schließen</button>
          <button type="button" class="btn btn-primary" onclick={() => { alert('PDF wird heruntergeladen...'); onclose(); }}>
            PDF Herunterladen (DIN A4)
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
