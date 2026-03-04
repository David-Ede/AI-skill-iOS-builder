# PRD Mapping Contract

## Purpose
Use a completed PRD (based on `Prd Template.md`) as the mandatory product contract.

The PRD controls:
- product scope
- enabled modules
- FR/NFR requirements
- implementation evidence and release gates

## Required PRD Input
- Input key: `PrdPath`
- Expected file: project-specific PRD derived from `Prd Template.md`
- If `PrdPath` is missing, unreadable, or incomplete, stop and return `BLOCKED_INPUT`.

## Preflight Validation Rules
Before scaffolding, verify these sections are present and populated:
- Section 0: Document Control
- Section 1: Product Definition
- Section 2.1 to 2.3: Objectives, MVP scope, out of scope
- Section 3: Modular Architecture Selection
- Section 5: End-to-End Journeys
- Section 6: Global Functional Requirements
- Section 7.1: Data Strategy
- Section 8: Non-Functional Requirements
- Section 9: Security, Privacy, and Compliance
- Section 10.1: Product Metrics
- Section 11: Release and Environment Contract
- Section 12: QA and Test Strategy
- Section 14: Risks, Assumptions, Open Questions
- Section 15: Definition of Ready and Done

Placeholder policy:
- Required fields must not keep template placeholders (for example `[PROJECT_NAME]`).
- `UNKNOWN` is allowed only when uncertainty is explicit in open questions and does not block current execution.

## PRD Module to Scaffold Flag Mapping
Use Section 3 (`Enabled = Yes/No`) to derive scaffold flags where direct templates exist.

| PRD Module ID | Scaffold Flag | Scaffold Coverage | Implementation Requirement |
| --- | --- | --- | --- |
| `MOD-AUTH` | `WithAuth=true` | Baseline template | Implement product auth behavior + tests from PRD. |
| `MOD-ONBOARD` | `WithUiFoundation=true` | Baseline template | Replace starter states with product onboarding flows. |
| `MOD-PROFILE` | `WithProfile=true` | Baseline template | Implement real profile/settings behavior and persistence. |
| `MOD-MSG` | `WithPush=true` | Baseline template | Implement reminder/notification domain flows and tests. |
| `MOD-OFFLINE` | `WithDataLayer=true` | Baseline template | Implement real local persistence/sync contracts from PRD. |
| `MOD-ANALYTICS` | `WithAnalytics=true` | Baseline template | Wire real event taxonomy from PRD Section 10. |
| `MOD-LOCALE` | `WithLocalization=true` | Baseline template | Implement locale behavior required by PRD. |
| `MOD-ACCESS` | `WithAccessibilityChecks=true` | Checklist + baseline | Apply and verify accessibility requirements in shipped UI. |
| `MOD-COMPLY` | `WithPrivacyChecklist=true` | Checklist + baseline | Implement real policy/compliance controls from PRD. |
| `MOD-CONTENT` | none | No direct scaffold | Implement custom feature code/tests in implementation phase. |
| `MOD-TRANSACT` | none | No direct scaffold | Implement custom purchase/paywall/subscription flows + tests. |
| `MOD-SOCIAL` | none | No direct scaffold | Implement custom social/community flows + tests. |
| `MOD-ADMIN` | none | No direct scaffold | Implement custom admin/internal tooling + tests. |
| `MOD-INTEG` | none | No direct scaffold | Implement external integration contracts + failure handling tests. |
| `MOD-SEARCH` | none | No direct scaffold | Implement search/filter/ranking behavior + tests. |
| `MOD-MEDIA` | none | No direct scaffold | Implement media upload/playback pipelines + tests. |

Optional derived flag:
- If PRD reliability requirements include crash capture, set `WithCrashReporting=true`.

## Scope Reconciliation Rules
- Section 2.2 (MVP In Scope) defines what must be implemented.
- Section 2.3 (Out of Scope) defines what must not be implemented.
- If user instructions conflict with PRD scope, stop and request PRD revision or explicit override approval.

## Traceability Rules
- Every `FR-*` and `NFR-*` must exist in `<project>/reports/prd-implementation.json`.
- Every P0 requirement must include:
  - `status: implemented`
  - at least one existing code evidence file
  - at least one existing test evidence file
- P0 module requirements must include feature-specific tests beyond baseline shell/module smoke tests.
- If any P0 requirement is unmapped or lacks evidence, final status cannot be `pass`.

## BLOCKED_INPUT Response Contract
When preflight fails, return:
- `code`: `BLOCKED_INPUT`
- `missingRequiredFields`: list of missing/empty required PRD fields
- `unresolvedPlaceholders`: list of unresolved required placeholders
- `scopeConflicts`: list of user-requested items conflicting with PRD scope
- `nextAction`: explicit user action required to proceed

Do not run scaffold, CI setup, or validation gates while `BLOCKED_INPUT` is active.
