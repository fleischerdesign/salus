# Specification: Settings Navigation Architecture & Single-Word Labels

## 1. Problem Statement

The Settings tab bar currently uses ambiguous, concatenated labels containing ampersands and multi-word phrases (e.g. "Konto und Profil", "Erscheinungsbild und Design", "Sensoren und Quellen", "Datenschutz und E2EE", "Arzt-Freigaben", "Datensicherung"). This creates visual noise, layout wrapping issues, and semantic ambiguity.

## 2. User Stories

- **As a user**, I want clean, concise, single-word tab labels in the Settings navigation without ambiguous word concatenations (no "&") so that I immediately understand where each setting lives.
- **As a user**, I want all settings categories (Profile, Appearance, Security, Sources, Notifications, Shares, Data) to be logically separated with clear dedicated tabs.

## 3. Acceptance Criteria (Gherkin)

```gherkin
Feature: Single-Word Settings Navigation

  Scenario: Tab labels are single, unambiguous words without ampersands
    Given the user navigates to "/settings"
    Then the navigation bar renders exactly the following 7 tabs in order:
      | Path                     | Label              | Icon            | Tab Key       |
      | /settings/account        | Profil             | person          | account       |
      | /settings/app            | Erscheinungsbild   | palette         | appearance    |
      | /settings/security       | Sicherheit         | lock            | security      |
      | /settings/sources        | Quellen            | sensors         | sources       |
      | /settings/notifications  | Benachrichtigungen | notifications   | notifications |
      | /settings/shares         | Freigaben          | share           | shares        |
      | /settings/data           | Daten              | database        | data          |
    And no tab label contains "&" or "und"

  Scenario: Route and Tab synchronization
    Given the user opens any of the 7 routes
    When the page renders
    Then the corresponding tab is highlighted as active
    And switching tabs updates the route without layout jitter

  Scenario: Content segregation
    Given the user selects the "Sicherheit" tab
    Then security-related controls (App-Sperre/Biometrie, Passwort, 2FA/Sitzungen) are displayed
    And the user selecting the "Benachrichtigungen" tab sees toast and sync notification toggles
    And the user selecting the "Daten" tab sees export, import, and local storage controls
```

## 4. Route Mapping & Compatibility

- `/settings/account` → Tab: `Profil` (`account`)
- `/settings/app` → Tab: `Erscheinungsbild` (`appearance`)
- `/settings/security` (and `/settings/privacy` redirect/proxy) → Tab: `Sicherheit` (`security`)
- `/settings/sources` → Tab: `Quellen` (`sources`)
- `/settings/notifications` → Tab: `Benachrichtigungen` (`notifications`)
- `/settings/shares` → Tab: `Freigaben` (`shares`)
- `/settings/data` (and `/settings/backup` redirect/proxy) → Tab: `Daten` (`data`)

## 5. Out of Scope

- Complete redesign of the external Admin console routes (already modular).
