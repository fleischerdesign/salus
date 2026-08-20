# Programming Domain — Specification

> Status: agreed · Supersedes: none · Related ADR: (to be written after this spec)

## Problem Statement

Salus models a training program as a flat list of exercises
(`WorkoutPlan` → `WorkoutPlanExercise`). Three capabilities are missing:

1. There is no **training-day layer** between a single exercise and a
   program, so a "Push Day" cannot be defined once and reused across
   programs.
2. Programs have no **time dimension**: training days cannot be arranged
   over time except an implicit "do the list in order". There is no
   rotating, weekly, or dated schedule.
3. There is no **systematic progression** of training targets. The only
   existing mechanism (autoregulation) adjusts load *downward* on poor
   recovery, never *upward* on successful sessions. The athlete must
   compute their own progressive overload — the single highest-value
   calculation a strength tracker should perform for them.

## User Story

As a strength trainee,
I want to organize exercises into reusable training days, arrange those
days into a program over time (rotating, weekly, or dated), and have the
app propose the next session's load from my past performance,
so that I follow a progressive, adaptive program without manual math.

---

## Feature 1: Reusable training days

A **training day** (workout) is an ordered list of exercises, each with
base targets (sets, reps, RPE, rest). A training day is reusable across
programs; editing it updates every program that uses it.

### Scenarios

**Scenario: Create a training day**
Given a catalog exercise "Bench Press" exists
When I create a training day "Push Day" containing "Bench Press" with target 3×8
Then the day is saved and lists "Bench Press" with target sets 3 and reps 8

**Scenario: Reuse a training day in multiple programs**
Given training day "Push Day" exists
When I add "Push Day" to two different programs
Then both programs reference the same day, and editing the day updates both

**Scenario: Remove an exercise from a training day**
Given training day "Push Day" contains "Bench Press" and "Overhead Press"
When I remove "Bench Press" from the day
Then "Overhead Press" remains, and programs using the day reflect the change

**Scenario: Delete a training day still in use (error)**
Given training day "Push Day" is used by program "Push-Pull-Legs"
When I attempt to delete "Push Day"
Then the system rejects the deletion with a clear reason (program still references it)

---

## Feature 2: Program schedule (rotation / weekly / dated)

A **program** is an ordered sequence of training days, each with an
optional timing rule:

| Timing rule | Meaning |
|---|---|
| *(none)* — rotation | next day in sequence; wraps to the first after the last |
| weekday | this day is performed on that weekday |
| date | this day is performed on that specific date |

The timing rule is **per training day**, not a property of the program, so
a single program may mix all three modes.

### Scenarios

**Scenario: Rotating schedule (default)**
Given a program with training days [A, B, C] and no timing rules
When I ask "what is the next training day after B?"
Then the system answers C, and after C it wraps to A

**Scenario: Weekly schedule**
Given a program with "Push" on Monday and "Pull" on Wednesday
When I ask "what is scheduled for Wednesday?"
Then the system answers "Pull"

**Scenario: Dated schedule**
Given a program with a training day dated 2026-04-01
When I ask "what is scheduled for 2026-04-01?"
Then the system answers that training day

**Scenario: Mixed timing rules (edge)**
Given a program with day A (rotation), day B (Monday), and day C (dated 2026-04-01)
When I ask "what is the next training day after A?"
Then the system answers B, because B has the next explicit timing rule in sequence

**Scenario: Invalid weekday (error)**
Given I try to assign a training day to weekday "Funday"
When I save the schedule
Then the system rejects it with a validation error naming the valid weekdays

---

## Feature 3: Progressive overload

The system proposes the next session's load for an exercise, derived from
the athlete's most recent completed performance of that exercise and a
per-exercise increment rule. The proposal is a suggestion the athlete can
accept, adjust, or lock.

### Scenarios

**Scenario: Successful session → increase**
Given exercise "Bench Press" has base target 3×8 at 60 kg and an increment of 2.5 kg
And my most recent completed session hit all 3 sets of 8 reps at RPE ≤ target
When the system proposes the next session's load
Then it proposes 62.5 kg for the same sets and reps

**Scenario: Missed target → hold**
Given exercise "Bench Press" has base target 3×8 at 60 kg
And my most recent completed session failed to reach 8 reps on the final set
When the system proposes the next session's load
Then it proposes 60 kg (no increase)

**Scenario: Rep-range progression**
Given exercise "Bench Press" has target range 8–12 reps
And my most recent session hit 12 reps (top of range) at 60 kg
When the system proposes the next session's load
Then it proposes 62.5 kg at 8 reps (bottom of range)

**Scenario: Manual lock**
Given exercise "Bench Press" is locked (exempt from progression)
When the system proposes the next session's load
Then it returns the locked target unchanged, regardless of performance

**Scenario: No prior history**
Given exercise "Bench Press" has base target 3×8 at 60 kg and no completed sessions
When the system proposes the next session's load
Then it proposes the base target 60 kg

**Scenario: Session with no logged sets (edge)**
Given my most recent session for "Bench Press" contains no logged sets
When the system proposes the next session's load
Then it falls back to the base target rather than failing

**Scenario: Increase exceeds a maximum jump (edge)**
Given my most recent performance would imply an increase beyond the configured maximum jump
When the system proposes the next session's load
Then it caps the increase at the configured maximum jump

**Scenario: Missing increment configuration (error)**
Given exercise "Bench Press" has no increment configured
When the system proposes the next session's load
Then it uses the plan's default increment rather than failing

---

## Edge Cases

Covered:
- Empty history → base target (Feature 3, "No prior history")
- Session with no sets → base target (Feature 3, "Session with no logged sets")
- Reuse across programs (Feature 1, "Reuse a training day")
- Deletion while in use → rejected (Feature 1, "Delete a training day still in use")
- Mixed timing modes (Feature 2, "Mixed timing rules")
- Invalid weekday → validation error (Feature 2, "Invalid weekday")
- Manual lock → target unchanged (Feature 3, "Manual lock")
- Increase capped at maximum jump (Feature 3, "Increase exceeds a maximum jump")

Not covered (explicitly out of scope for this spec):
- Cardio / distance / duration-based activities (separate spec — "Sport")
- Concurrent editing of the same program from two devices (handled by the
  existing sync conflict-resolution path, unchanged)
- Percentage-of-1RM and block-periodization progression schemes (future
  strategies; this spec covers only linear/rep-range progression)

## Out of Scope

- **Cardio and endurance activities** — a later spec (point "Sport").
- **Program templates and federation/sharing of programs** — a later spec.
- **Additional progression strategies** (percentage-of-1RM, block
  periodization, AMRAP) — the architecture must accommodate them
  (open/closed), but only linear/rep-range progression is implemented now.
- **UI redesign** — this spec defines behavior; presentation is out of scope.

## Sizing

This is a two-phase feature and is intentionally split:

1. **Structure + schedule** (Features 1 and 2, plus migration) — one
   focused session.
2. **Progressive overload** (Feature 3) — one focused session.

Each phase is right-sized (~2–4 h) and independently shippable.

## Open Design Questions (handoff to ADR)

These are *decisions*, not spec scenarios; they are resolved in the
architecture-design step that follows:

1. The contract of the progression "context" (what a strategy is allowed to read).
2. How multiple strategies compose (linear + deload + autoregulation).
3. The target data model (sets, rep range vs. fixed reps, weight, %1RM, RPE, rest, AMRAP).
4. Stateless (recomputed from history) vs. stateful (persisted working weight) progression.
5. The migration mapping of existing flat plans into the training-day model.
