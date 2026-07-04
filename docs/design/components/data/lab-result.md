# Lab Result

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Test name + Value (bold) + Unit + Reference range + Status indicator

**States:** Normal (tertiary/green indicator) · Borderline Low/High (warning/amber) · Abnormal Low/High (error/red) · Critical (error, pulsing or bold-red)

**Reference range:** Shown as muted text: "(Ref: 3.5–5.2)". Status dot or colored background on abnormal values.

**Formatting:** Value: headline-md, bold. Unit: body-sm, muted. Range: body-sm, muted. Status: 8px colored dot left of value.

**Grouping:** Multiple lab results grouped by category (Chemistry, Hematology, etc.) with category header.

**Do:** Show reference range · Color-code abnormal values · Group by category · Show critical values prominently

**Don't:** Show value without range · Use color alone for abnormal · Hide units
