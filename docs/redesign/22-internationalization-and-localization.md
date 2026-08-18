# Salus 2.0 — Internationalisierung & Lokalisierung (i18n / l10n)
**Dokument:** `22-internationalization-and-localization.md`  
**Status:** Verbindlich  
**Zweck:** Typsichere Mehrsprachigkeit (Deutsch Standard `de-DE`, Englisch `en-US`, Französisch `fr-FR`), medizinische Fachwörterbücher und native Formatierung.

---

## 1. Native Formatierungs-Engines (`Intl` API)

Keine externen schweren Datums- oder Zahlenbibliotheken (Zero Overhead):

```typescript
export class Formatter {
  private static locale = 'de-DE';

  static setLocale(loc: string) {
    this.locale = loc;
  }

  // Zahl mit lokaler Tausender- & Dezimaltrennung (z.B. "1.840 kcal" vs. "1,840 kcal")
  static number(val: number, decimals = 1): string {
    return new Intl.NumberFormat(this.locale, {
      minimumFractionDigits: 0,
      maximumFractionDigits: decimals
    }).format(val);
  }

  // Relativer Zeitstempel (z.B. "vor 2 Stunden", "in 45 Minuten")
  static relativeTime(date: Date): string {
    const rtf = new Intl.RelativeTimeFormat(this.locale, { numeric: 'auto' });
    const diffSeconds = Math.round((date.getTime() - Date.now()) / 1000);
    if (Math.abs(diffSeconds) < 3600) {
      return rtf.format(Math.round(diffSeconds / 60), 'minute');
    }
    return rtf.format(Math.round(diffSeconds / 3600), 'hour');
  }
}
```

---

## 2. Medizinisches Fachwörterbuch

```typescript
export const MEDICAL_I18N = {
  'de-DE': {
    systolic_bp: 'Systolischer Blutdruck',
    diastolic_bp: 'Diastolischer Blutdruck',
    fasting_glucose: 'Nüchternglukose',
    ldl_c: 'LDL-Cholesterin',
    hdl_c: 'HDL-Cholesterin',
    optimal: 'Optimal',
    elevated: 'Erhöht',
    critical: 'Kritisch'
  },
  'en-US': {
    systolic_bp: 'Systolic Blood Pressure',
    diastolic_bp: 'Diastolic Blood Pressure',
    fasting_glucose: 'Fasting Glucose',
    ldl_c: 'LDL Cholesterol',
    hdl_c: 'HDL Cholesterol',
    optimal: 'Optimal',
    elevated: 'Elevated',
    critical: 'Critical'
  }
};
```
