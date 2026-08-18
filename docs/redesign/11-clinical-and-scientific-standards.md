# Salus 2.0 — Klinische & Wissenschaftliche Standards
**Dokument:** `11-clinical-and-scientific-standards.md`  
**Status:** Verbindlich  
**Zielgruppe:** Ärzte, Kardiologen, Endokrinologen, klinische Ernährungsberater, Sportwissenschaftler & ambitionierte Health-Nutzer.

---

## 1. Das Dual-Layer-Prinzip (*Accessible on Surface, Clinical on Demand*)

Salus ist **keine oberflächliche Gamification- oder Spaß-App**, sondern eine **akademisch fundierte, klinisch exakte Plattform für metabolische Gesundheit, Prävention und Leistungsdiagnostik**.

Um sowohl dem gesundheitsinteressierten Alltagsläufer als auch dem behandelnden Facharzt gerecht zu werden, folgt Salus dem **Dual-Layer-Prinzip**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ SCHICHT 1: TÄGLICHER NUTZER (Glanceable, Emotional, Motivierend)                       │
│ • Intuitive visuelle Metaphern (Wellen-Glas, Stoffwechsel-Uhr, Ringe)                   │
│ • Erfassung unter 2 Sekunden (Zero-Friction Logging)                                    │
│ • Klare Handlungsempfehlungen ohne Fachchinesisch                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                 ↕ [ 1-KLICK PRO-/KLINIK-ANSICHT ]                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ SCHICHT 2: ARZT, ERNAEHRUNGSBERATER & WISSENSCHAFTLER (Klinische Exaktheit)             │
│ • Vollständige SI- & Klinische Einheiten (mg/dL, mmol/L, µg/L, mmHg, g/kg KG)           │
│ • Leitlinienkonforme Referenzbereich-Tachos (ESC/EAS, ADA, WHO)                         │
│ • Statistische Gütemaße (Pearson r, Spearman ρ, p-Werte, R², 80%/95% Konfidenzbänder)   │
│ • Pharmakokinetische Halbwertszeiten & Adhärenz-Metriken (PDC / MPR)                     │
│ • Druckfertiger, strukturierter PDF-Klinikbericht für die Krankenakte                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Klinische Labordiagnostik & Biomarker-Standards

### 2.1 Standardisierte Einheiten & Automatische Konvertierung
Salus unterstützt die parallele Anzeige und nahtlose Konvertierung zwischen SI-Einheiten und konventionellen klinischen Einheiten:
- **Glukose / HbA1c:** $\text{mg/dL} \leftrightarrow \text{mmol/L}$ und $\% \leftrightarrow \text{mmol/mol}$ (IFCC Standard).
- **Lipid-Panel:** $\text{mg/dL} \leftrightarrow \text{mmol/L}$ für Gesamtcholesterin, LDL-C, HDL-C, Triglyzeride, ApoB, Lp(a).
- **Hormone & Vitamine:** $\text{ng/mL} \leftrightarrow \text{nmol/L}$ (z.B. Vitamin D3 25-OH, Testosteron, TSH, fT3, fT4).

### 2.2 Leitlinienkonforme 4-Stufen-Referenzbalken (`ClinicalGaugeMeter`)
Jeder Biomarker wird im Verhältnis zu evidenzbasierten Fachgesellschafts-Leitlinien visualisiert:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ LDL-CHOLESTERIN (ESC/EAS Leitlinie)                                 Aktuell: 68 mg/dL   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│   KRITISCH NIEDRIG   │     OPTIMAL / ZIEL     │    GRENZWERTIG   │    KRITISCH HOCH     │
│     < 40 mg/dL       │      40 - 70 mg/dL     │   70 - 115 mg/dL │      > 116 mg/dL     │
│   ░░░░░░░░░░░░░░░░░░ │ ██████████████████████ │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                      │           ▲ (68 mg/dL) │                  │                      │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```
- **Kardiovaskuläre Risiko-Ratios:** Automatische Berechnung klinischer Quotienten:
  - $\text{Triglyzeride} / \text{HDL-C}$ Ratio (Surrogatmarker für Insulinresistenz und Small Dense LDL).
  - $\text{ApoB} / \text{ApoA1}$ Ratio (Atherogenitäts-Index).
  - $\text{HOMA-IR}$ Score ($\frac{\text{Nüchternglukose [mg/dL]} \times \text{Nüchterninsulin [µU/mL]}}{405}$).

---

## 3. Pharmakologie & Medikamenten-Sicherheit

1. **Pharmakokinetische Transparenz:**
   - Visualisierung von Eliminations-Halbwertszeiten ($t_{1/2}$) bei Stimulanzien (z. B. Koffein $t_{1/2} \approx 5-7\text{h}$) und Medikamentenspiegeln.
2. **Therapietreue-Metriken (Adhärenz):**
   - Berechnung des wissenschaftlichen **PDC (Proportion of Days Covered)** zur Beurteilung der Therapietreue für behandelnde Ärzte.
3. **Interaktions- & Einnahmehinweise:**
   - Kennzeichnung von Mahlzeiten-Abhängigkeiten (*„Nüchtern mit Wasser einnehmen“*, *„Zu einer fetthaltigen Mahlzeit“*).

---

## 4. Ernährungswissenschaftliche & Stoffwechsel-Präzision

1. **Dynamische Energiebedarfs-Modelle:**
   - Berechnung des Grundumsatzes (BMR) wahlweise nach **Mifflin-St Jeor** oder **Katch-McArdle** (bei gemessenem Körperfettanteil).
   - Differenzierung von BMR, TEF (Thermischer Effekt der Nahrung), NEAT und EAT (Trainingsenergie).
2. **Aminosäuren- & Fettsäuren-Tiefe:**
   - Neben den Makronährstoffen (P/C/F) können Ernährungsberater Details wie Leucin-Gehalt, Ballaststoff-Zusammensetzung und Omega-3/Omega-6-Verhältnisse einsehen.
3. **Glykämische Last & Fasten-Metabolismus:**
   - Zuordnung der metabolischen Fastenphasen anhand wissenschaftlicher Schwellenwerte (Glykogen-Entleerung, Ketogenese, lysosomale Autophagie).

---

## 5. Trainingswissenschaft & Sportphysiologie

1. **Autoregulation & RPE-Skala:**
   - Saubere Trennung von planmäßigem Satz-Schema und tatsächlicher subjektiver Belastung (Borg-Skala / RPE 1–10 und RIR - Reps in Reserve).
2. **Wissenschaftliche 1RM-Formeln:**
   - Maximalkraft-Schätzung wahlweise nach **Epley** ($w \cdot (1 + r/30)$) oder **Brzycki** ($w \cdot \frac{36}{37 - r}$) mit mathematischer Begrenzung auf $r \le 10$ Wiederholungen zur Vermeidung von Verzerrungen.
3. **Akute zu chronische Belastungssteuerung (ACWR):**
   - Verhältnis des 7-Tage-Volumens (akut) zum 28-Tage-Volumen (chronisch) zur Vermeidung von Überlastungsschäden und Übertraining.

---

## 6. Statistische Integrität & Methodik

Jedes Analyse-Panel in Salus legt seine statistische Methodik transparent über das [`MethodologyBadge.svelte`](file:///home/philipp/dev/salus/frontend/src/lib/components/ui/MethodologyBadge.svelte) offen:
- **Korrelationen:** Ausweisung des Korrelationskoeffizienten ($r$ bzw. $\rho$), der Stichprobengröße ($n$), der Freiheitsgrade ($df$) und des statistischen Signifikanzniveaus ($p$-Wert).
- **Trend-Glättung:** Klare Kennzeichnung von exponentiell geglätteten Kurven (7-Tage-EMA) vs. Rohdatenpunkten.
- **Konfidenzbänder:** Statistische Vorhersagen weisen stets das 80%- und 95%-Konfidenzintervall aus.

---

## 7. Der Klinische PDF-Bericht (Arztbrief-Standard)

Für den Arztbesuch oder die Konsultation beim Ernährungsberater generiert Salus auf Knopfdruck einen **hochauflösenden, klinisch strukturierten PDF-Gesundheitsbericht**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ KLINISCHER VERLAUFSBERICHT — SALUS HEALTH                                               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ Patient: Philipp M. | Geb.: 14.03.1992 | Zeitraum: 01.06.2026 – 31.08.2026 (90 Tage)    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. KARDIOVASKULÄRE VITALWERTE                                                           │
│ • Blutdruck (Mittelwert): 118 / 76 mmHg (92 Messungen, 98% im Zielbereich < 120/80)    │
│ • Ruhepuls (Mittelwert): 56 ± 4 bpm | HRV (rMSSD): 64 ± 8 ms                            │
│                                                                                         │
│ 2. KLINISCHE BIOMARKER & LABORWERTE (Auszug)                                            │
│ Marker            Ergebnis     Einheit    Referenzbereich    Status      Verlauf (90T)  │
│ ─────────────────────────────────────────────────────────────────────────────────────── │
│ Nüchternglukose    84          mg/dL      70 - 99            Optimal     [ 86 → 84 ]    │
│ HbA1c              5.1         %          < 5.7              Optimal     [ 5.2 → 5.1 ]  │
│ LDL-Cholesterin    68          mg/dL      < 70 (ESC Ziel)    Optimal     [ 82 → 68 ] ↘  │
│ HDL-Cholesterin    62          mg/dL      > 40               Optimal     [ 58 → 62 ] ↗  │
│ Triglyzeride       74          mg/dL      < 150              Optimal     [ 88 → 74 ] ↘  │
│ hs-CRP             0.4         mg/L       < 1.0 (Low Risk)   Optimal     [ 0.6 → 0.4 ]  │
│ Ferritin           142         µg/L       30 - 300           Optimal     [ 138 → 142 ]  │
│ 25-OH Vitamin D3   54          ng/mL      40 - 70            Optimal     [ 42 → 54 ] ↗  │
│                                                                                         │
│ 3. MEDIKATION & ADHÄRENZ                                                                │
│ • Telmisartan 20mg (1-0-0) — Adhärenz: 98.9% (PDC)                                     │
│ • Omega-3 2000mg EPA/DHA (1-0-0) — Adhärenz: 96.7%                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Asymmetrische E2EE-Verschlüsselung & Medizinische Datensicherheit

1. **Zero-Knowledge-Architektur:** Keine unverschlüsselte Ablage medizinischer Daten auf Fremdservern.
2. **Kryptographisches Sharing:** Asymmetrischer Schlüsselaustausch (RSA-OAEP 4096-bit + AES-256-GCM) für Arzt-Freigabelinks. Der Arzt entschlüsselt die Daten lokal in seinem Browser mit dem Einmal-PIN/Passwort des Patienten.
3. **Audit-Log:** Vollständige Protokollierung jedes Datenzugriffs im `FederatedAccessLog`.
