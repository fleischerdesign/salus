# Komponentenspezifikation: `FileUpload.svelte`
**Pfad:** `frontend/src/lib/components/ui/FileUpload.svelte`  
**Kategorie:** Molekül / Drag & Drop Datei-Upload  
**Zweck:** Drag & Drop Upload-Bereich für Laborbefund-PDFs, CSV-Datenimporte, Apple Health Export-Archive und Profilbilder mit Fortschrittsbalken und Dateityp-Validierung.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐│
│    [ 📁 PDF/CSV Icon ]                                      │
│    Laborbericht oder CSV hierher ziehen oder [ Durchsuchen ]│
│    Unterstützt: PDF, CSV, XML (Apple Health) • Max. 25 MB   │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘│
│                                                             │
│  Ausgewählt: 📄 Labor_Befund_2026.pdf (1.4 MB)  [ 🗑️ ]      │
│  [████████████████████████████████░░░░░] 78% Upload         │
└─────────────────────────────────────────────────────────────┘
```

- **Drag-Over-State:** `border-2 border-dashed border-primary-500 bg-primary-50/50 scale-[1.01] transition-transform`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  accept?: string; // z.B. ".pdf,.csv,.xml,image/*"
  maxSizeMb?: number; // Standard: 25
  multiple?: boolean;
  onUpload: (files: File[]) => Promise<void> | void;
}
```
