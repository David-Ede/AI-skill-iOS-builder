# PRD Mapping Contract

## Purpose
Use a completed PRD (based on `PRD_TEMPLATE.md`) as the mandatory planning contract for this skill.

The PRD controls:
- product scope
- enabled modules
- functional and non-functional requirements
- acceptance and release gates

## Required PRD Input
- Input key: `PrdPath`
- Expected file: a project-specific PRD derived from `PRD_TEMPLATE.md`
- If `PrdPath` is missing, unreadable, or incomplete, stop and return `BLOCKED_INPUT`.

## Preflight Validation Rules
Before scaffolding, verify all required PRD sections are present and populated:
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
- Required fields must not keep template placeholders (for example: `[PROJECT_NAME]`).
- `UNKNOWN` is allowed only when uncertainty is explicit and reflected in open questions.

## PRD Module to Skill Flag Mapping
Use `Section 3` module table (`Enabled = Yes/No`) to derive scaffold flags.

| PRD Module ID | If Enabled = Yes | Skill Support | Notes |
| --- | --- | --- | --- |
| `MOD-AUTH` | `WithAuth=true` | Supported | Auth/session scaffold only; provider credentials are human-owned setup. |
| `MOD-ONBOARD` | `WithUiFoundation=true` | Partially supported | Uses baseline routes/screens; complex onboarding logic is custom follow-up work. |
| `MOD-PROFILE` | `WithProfile=true` | Supported | Implies UI foundation. |
| `MOD-MSG` | `WithPush=true` | Partially supported | Push/deep-link baseline only. Email/SMS/in-app chat backends are out of scope. |
| `MOD-OFFLINE` | `WithDataLayer=true` | Partially supported | Retry/cache baseline only; full offline sync/conflict engines are out of scope. |
| `MOD-ANALYTICS` | `WithAnalytics=true` | Supported | Placeholder analytics adapter. |
| `MOD-LOCALE` | `WithLocalization=true` | Supported | Localization scaffold and message catalog baseline. |
| `MOD-ACCESS` | `WithAccessibilityChecks=true` | Supported | Checklist and baseline accessibility guardrails. |
| `MOD-COMPLY` | `WithPrivacyChecklist=true` | Supported | Checklist and privacy readiness scaffold. |

Optional derived flag:
- If PRD telemetry or reliability requirements require crash capture, set `WithCrashReporting=true`.

Unsupported modules:
- `MOD-CONTENT`
- `MOD-TRANSACT`
- `MOD-SOCIAL`
- `MOD-ADMIN`
- `MOD-INTEG`
- `MOD-SEARCH`
- `MOD-MEDIA`

If any unsupported module is `Enabled = Yes`, return `BLOCKED_INPUT`.

## Scope Reconciliation Rules
- Section 2.2 (MVP In Scope) defines what must be implemented.
- Section 2.3 (Out of Scope) defines what must not be implemented.
- If user instructions conflict with PRD scope, stop and request PRD revision or explicit override approval.

## Requirement Traceability Rules
- Every `FR-*` and `NFR-*` must map to at least one implementation task.
- Every P0 requirement must map to at least one verification artifact (unit/integration/E2E/manual test or validator gate).
- If a P0 requirement is unmapped, final status cannot be `pass`.

## BLOCKED_INPUT Response Contract
When preflight fails, return:
- `code`: `BLOCKED_INPUT`
- `missingRequiredFields`: list of missing/empty required PRD fields
- `unresolvedPlaceholders`: list of unresolved required placeholders
- `unsupportedEnabledModules`: list of unsupported modules enabled in PRD
- `scopeConflicts`: list of user-requested items conflicting with PRD scope
- `nextAction`: explicit user action required to proceed

Do not run scaffold, CI setup, or validation gates when `BLOCKED_INPUT` is active.
