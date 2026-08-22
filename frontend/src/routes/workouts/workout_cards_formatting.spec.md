# Specification: Workout Cards Muscle Formatting & UI Decluttering

## Problem Statement

In `/workouts`, Workout Plan cards display target muscles using raw database snake_case strings (e.g., `erector_spinae`), and combine multiple muscles from comma-separated exercise attributes into single awkward pills (e.g., `erector_spinae, gluteus_maximus, hamstrings`). Additionally, cards are visually cluttered with text buttons like `+1 weitere Übungen →` instead of a modern, subtle fade-out overflow indicator.

## User Story

As an athlete reviewing workout plans on the `/workouts` dashboard,
I want target muscles to be displayed as individual, cleanly formatted Title Case tags (e.g. "Erector Spinae", "Gluteus Maximus"),
and exercise lists in cards to have a clean, subtle fade-out when more exercises are present,
so that the cards look polished, readable, and visually uncluttered.

## Acceptance Criteria (Gherkin)

```gherkin
Feature: Workout Cards Muscle Formatting and UI Decluttering

  Scenario: Format snake_case muscle names to Title Case
    Given a muscle identifier "erector_spinae"
    When formatMuscleName is called
    Then the result should be "Erector Spinae"

  Scenario: Format compound snake_case muscles
    Given a muscle identifier "latissimus_dorsi"
    When formatMuscleName is called
    Then the result should be "Latissimus Dorsi"

  Scenario: Preserve existing Title Case or German muscle names
    Given a muscle name "Brust" or "Rücken"
    When formatMuscleName is called
    Then the result should remain "Brust" or "Rücken"

  Scenario: Safe handling of null, undefined, or empty strings
    Given a null or empty muscle string
    When formatMuscleName is called
    Then the result should be an empty string without throwing

  Scenario: Separate muscle pills in plan cards
    Given a workout plan with exercises having primary muscles "erector_spinae, gluteus_maximus, hamstrings"
    When the plan card focus pills are generated
    Then each muscle is parsed into its own distinct token
    And each pill contains a single formatted muscle (e.g. "Erector Spinae", "Gluteus Maximus", "Hamstrings")
    And no single pill contains comma-separated muscles

  Scenario: Decluttered exercise list with subtle overflow fade
    Given a workout plan with more than 3 exercises
    When the plan card is rendered
    Then the "+X weitere Übungen →" text button is removed
    And the exercise list has a subtle bottom gradient fade-out mask indicating additional items
```

## Edge Cases

- **Covered**:
  - Exercises with missing or empty `primary_muscles` (falls back gracefully)
  - Duplicate muscles across multiple exercises in the same plan (deduplicated via `Set`)
  - Plans with ≤ 3 exercises (rendered with full opacity, no fade mask needed)
  - Plans with > 3 exercises (rendered with subtle bottom fade mask)
- **Out of Scope**:
  - Restructuring database schema for exercise muscles
  - Altering workout execution / active session logging logic
