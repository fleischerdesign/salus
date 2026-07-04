# Active Session

**Anatomy:** Recovery score badge + Exercise list (with target sets/reps/RPE) + Body notes textarea + Complete Session button

**States:** Active · Completing · Completed (redirect)

**Exercise rows:** Name + Target (sets×reps @ RPE) + Logged sets sub-list + Log Set button

**Logged set:** Weight input + Reps input + RPE display + Check button. Logged sets dim to 0.75 opacity.

**Autoregulation indicator:** Show "Autoregulated" chip when plan has autoreg mode enabled. Show calculated 1RM progression.

**Complete Session:** POST form with notes textarea. Full-page redirect on success.

**Do:** Show real-time autoreg calculated targets · Disable log button when set count exceeds target · Show progress toward target sets

**Don't:** Allow logging without weight/reps · Omit warmup indicator · Forget rest timer between sets
