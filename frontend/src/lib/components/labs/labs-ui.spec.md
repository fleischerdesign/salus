# Specification: Labs Page UI/UX Cleanup

## 1. Problem Statement

The `/labs` route currently overloads the user with confusing medical and cryptographic jargon (e.g., "Multi-Draw", "ESC/EAS 2024 Leitlinien", "ECDH", "E2EE QR", "Klinische Biomarker-Verlaufsmatrix") and displays misleading static mock badges ("Optimal", "3 Panels", "Nüchternblut (14h Fasten)"). Furthermore, it contains redundant action buttons for PDF export with broken alert placeholders.

## 2. User Stories

- **As a user**, I want clear, natural language on the `/labs` page so that I can understand my biomarker history and share my reports without being overwhelmed by technical and academic jargon.
- **As a user**, I want accurate information instead of misleading hardcoded badges ("Optimal", "Nüchternblut") so that I am not misinformed about my health or data status.
- **As a user**, I want a single, clear button to view and export my clinical PDF report.

## 3. Acceptance Criteria (Gherkin)

```gherkin
Feature: Labs Page UI Simplification

  Scenario: Header and page subtitle display clear language
    Given the user navigates to "/labs"
    Then the header title is "Laborwerte"
    And the header subtitle is "Messwert-Verlauf, Organprofile und Befund-Freigabe für Behandler"
    And there is no static hardcoded "Nüchternblut (14h Fasten)" badge in the header

  Scenario: Navigation tabs have understandable labels and no misleading badges
    Given the user views the labs tab bar
    Then the first tab is labeled "Verlauf" (or "Messwert-Verlauf") without a static "Optimal" badge
    And the second tab is labeled "Organprofile" without a static "3 Panels" badge (or uses dynamic panel count)
    And the third tab is labeled "Arzt-Freigabe" with a neutral/primary icon color (not warning/circadian yellow) and without a static "ECDH" badge

  Scenario: Biomarker table title is clear and friendly
    Given the user views the biomarker timeline tab
    Then the section header is "Laborwert-Verlauf" (or "Messwert-Verlauf")
    And it does not contain the phrase "(Multi-Draw)" or "Verlaufsmatrix"
    And redundant dummy alert buttons ("Arztbericht exportieren") are removed in favor of the unified PDF report action

  Scenario: Action buttons in header are concise
    Given the user views the top action buttons in "/labs"
    Then the share button is labeled "Arzt-Freigabe" (or "Befund teilen")
    And the report button is labeled "PDF-Arztbericht" (or "Arztbericht (PDF)")
```

## 4. Out of Scope

- Backend changes to lab panel storage or sync.
- Real production cryptographic implementation of asymmetric ECDH key exchange (retains current client-side prototype flow with cleaner copy).
- Changes to database schema or `lab_marker` reference data.
