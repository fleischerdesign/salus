# Komponentenspezifikation: `JournalEditor.svelte`
**Pfad:** `frontend/src/lib/components/journal/JournalEditor.svelte`  
**Kategorie:** Organismus / Zen-Mode Markdown Journal  
**Zweck:** Ablesefreundlicher, ablenkungsfreier Zen-Modus Markdown-Editor für mentale Reflexion mit Leitfragen-Wähler, Stimmungs-Tagging, Wortzähler und verschlüsselter Auto-Save-Anzeige.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ ✍️ ABEND-REFLEXION                             [ 🔒 Auto-Save: Gesichert ]│
├─────────────────────────────────────────────────────────────┤
│  Geführte Prompts:                                          │
│  [ 💡 Was hat mir heute Energie gegeben? ]  [ 🧘 Worüber bin ich dankbar? ]│
│                                                             │
│  # Reflektierter Tag                                        │
│  Heute war das Training besonders fokussiert. Das 16:8-      │
│  Fasten lief absolut mühelos...                             │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│  Stimmungs-Tag: 😊 Flow & Ruhe      Wortanzahl: 142 Wörter  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  entryDate: string;
  initialContent?: string;
  initialMoodScore?: number;
  onSave: (content: string, moodScore?: number) => Promise<void> | void;
}
```
