# Specification: Workouts & Programs UI/UX Redesign

## 1. Problem Statement

The current workout plans and programs pages (`/workouts/plans` and `/workouts/programs`) display cards with inline action buttons ("Training starten", "Aktivieren", "Löschen"), leading to visual clutter, accidental clicks, and lack of dedicated detail views for deep inspection of training days and multi-day periodization structures. Users need clean, information-rich cards that navigate to dedicated, highly functional detail pages (`/workouts/plans/[id]` and `/workouts/programs/[id]`) offering full exercise breakdowns, progression insights, history, and deliberate action triggers.

---

## 2. User Stories

### Story 1: Workout Plan Exploration & Execution

As an athlete  
I want to click on a workout plan card to open a comprehensive workout plan detail page  
So that I can examine all planned exercises, target sets, reps, RPE, rest intervals, and target muscle groups before starting my training.

### Story 2: Training Program Inspection & Activation

As an athlete  
I want to click on a program card to open a dedicated program detail page  
So that I can review the complete weekly split, assigned workout routines, progression mechanics, and activate/pause the program with full transparency.

---

## 3. Acceptance Criteria (Gherkin Scenarios)

```gherkin
Feature: Workouts & Programs UI/UX Overhaul

  Scenario: Navigating from Workout Plan Card to Detail Page
    Given the user is on "/workouts/plans"
    When the user clicks anywhere on a workout plan card (e.g. "wo-fb-a")
    Then the browser navigates to "/workouts/plans/wo-fb-a"
    And the card itself contains no inline start or delete action buttons

  Scenario: Viewing Workout Plan Detail Page
    Given the user is on "/workouts/plans/wo-fb-a"
    Then the page displays the plan name, description, system/custom badge, and exercise count
    And a structured exercise list is rendered showing sequence, name, primary muscle, sets, reps, RPE, and rest seconds
    And clicking on an exercise navigates to its exercise detail page "/workouts/exercises/[id]"
    And an action bar provides a primary "Training starten" button
    And if the plan has completed session history, the past sessions are listed with dates, duration, and tonnage

  Scenario: Starting a Workout from the Plan Detail Page
    Given the user is on "/workouts/plans/wo-fb-a"
    When the user clicks "Training starten"
    Then an active WorkoutSession is created referencing "wo-fb-a"
    And the browser navigates to "/workouts/active"

  Scenario: Navigating from Program Card to Program Detail Page
    Given the user is on "/workouts/programs"
    When the user clicks anywhere on a program card (e.g. "prog-full-body-3d")
    Then the browser navigates to "/workouts/programs/prog-full-body-3d"
    And the card itself contains no inline activate or delete action buttons

  Scenario: Viewing Program Detail Page & Activating Program
    Given the user is on "/workouts/programs/prog-full-body-3d"
    Then the page displays the program title, description, progression scheme, and active/inactive status
    And a 7-day schedule grid shows assigned workouts for each weekday (e.g. Mo: GK A, Mi: GK B, Fr: GK A)
    And clicking an assigned workout card navigates to that workout's detail page
    When the user clicks "Programm aktivieren"
    Then the program status updates to active
    And the button updates to "Programm pausieren"

  Scenario: Weekly Periodization Overview in Programs Tab
    Given the user is on "/workouts/programs"
    Then the top "Wöchentliche Periodisierung" card summarizes active program slots
    And each scheduled day chip displays the day name and workout name
    And clicking a scheduled workout navigates to its detail page
```

---

## 4. Edge Cases & Scope

- **System vs Custom Plans**: System plans (`user_id === null`) display a "Standard-Vorlage" badge and offer "Als Vorlage anpassen / Duplizieren" instead of direct edit/delete.
- **Empty Program Slots / Rotation**: Programs without fixed weekdays display rotation sequence queues.
- **No Active Programs**: When no program is active, `WorkoutSplitCard` shows an inviting empty state encouraging the user to explore and activate a program.
