# Exec Plan: App Generator Framework Skill

Last updated: 2026-02-21  
Source input: `C:/Users/David/Desktop/expo-ios-app-builder-skill/TEMP_AUDIT_ADDITIONS.md`  
Plan type: Implementation planning only (no code changes in this phase)

## Objective

Implement all identified gaps from the temporary audit into the app generator framework skill so generated iOS-first apps are:

1. Infrastructure-ready (scaffold, validation, CI, EAS/TestFlight)
2. Product-baseline ready (core UI, auth, push, data, profile/settings)
3. Quality-hardened (testing, observability, accessibility, localization, privacy)

## Scope

Included:
- All `P0`, `P1`, `P2` items from the audit file
- Proposed structure additions (`references/*`, `assets/templates/*`, script updates)
- Definition-of-done upgrades for reliability and feature readiness

Excluded for now:
- Full monetization implementation (IAP/subscriptions) beyond planning hooks
- Existing-repo migrations
- Non-Expo and non-EAS release paths

## Guiding Principles

- Keep the framework modular with feature flags (opt-in modules).
- Keep generated output deterministic and validator-enforced.
- Ensure every enabled module has contract checks and smoke-test coverage.
- Separate "infrastructure pass" from "feature-ready pass" in final reporting.

## Target Skill Architecture (End State)

Core files:
- `SKILL.md` (updated contracts, inputs, feature flags, DoD, status model)
- `agents/openai.yaml` (refresh if prompting metadata changes)

References:
- `references/feature-modules.md`
- `references/ui-foundation.md`
- `references/auth-patterns.md`
- `references/notifications.md`
- `references/testing-quality.md` (expanded gate definitions)
- `references/workflow.md` (phase updates for feature flags)
- `references/privacy-compliance.md` (new)
- `references/accessibility-localization.md` (new)

Assets/templates:
- `assets/templates/feature-modules/ui-foundation/*`
- `assets/templates/feature-modules/auth/*`
- `assets/templates/feature-modules/notifications/*`
- `assets/templates/feature-modules/profile-settings/*`
- `assets/templates/feature-modules/data-layer/*`
- `assets/templates/feature-modules/analytics-crash/*`
- `assets/templates/feature-modules/localization/*`
- `assets/templates/icons-splash/*` (placeholder set)

Scripts:
- `scripts/scaffold_expo_ios_app.ps1` (feature flags + app.config.ts path + branch input)
- `scripts/setup_ci_eas.ps1` (branch parameterization + deterministic CI defaults)
- `scripts/validate_expo_ios_project.py` (feature-aware contract checks + anti-placeholder checks)

## Implementation Workstreams

## WS1: Contract and Interface Upgrade (P0 Foundation)

Goals:
- Normalize framework-skill inputs/outputs around module flags and quality expectations.

Planned changes:
- Add new optional inputs to `SKILL.md` and workflow docs:
  - `UseAppConfigTs`
  - `ReleaseBranch`
  - `WithUiFoundation`
  - `WithProfile`
  - `WithAuth`
  - `WithPush`
  - `WithDataLayer`
  - `WithAnalytics`
  - `WithCrashReporting`
  - `WithLocalization`
  - `WithAccessibilityChecks`
  - `WithPrivacyChecklist`
- Update DoD to require non-placeholder tests and deterministic CI behavior.
- Define reporting modes:
  - `infra_pass`
  - `feature_partial`
  - `feature_pass`

Acceptance criteria:
- All new inputs documented in one contract table.
- DoD aligns with validator checks and workflow gates.
- Final status semantics are unambiguous.

## WS2: Scaffold Reliability and Script Parity (P0)

Goals:
- Ensure both scaffold variants pass baseline quality gates out of the box.

Planned changes:
- Patch scaffold logic for both `blank-typescript` and `tabs` templates:
  - Resolve known lint/typecheck drift on fresh templates.
  - Install and pin required lint/test dependencies deterministically.
- Implement actual `app.config.ts` generation path when `UseAppConfigTs` is enabled.
- Preserve and validate `app.json` path when `UseAppConfigTs` is disabled.
- Ensure release branch from input is propagated to CI template generation.

Acceptance criteria:
- Fresh scaffold succeeds for both template modes.
- `npm run lint`, `npm run typecheck`, `npm run test` pass immediately on both modes.
- `app.config.ts` mode produces valid config with bundle ID + router plugin.

## WS3: Quality Gates and Validator Hardening (P0)

Goals:
- Prevent false-positive "pass" outcomes.

Planned changes:
- Replace placeholder/no-op test script with real smoke-test command.
- Add validator checks to fail when:
  - `scripts.test` is placeholder/no-op
  - required smoke tests are missing
  - enabled modules are missing required files/config/deps
- Expand report schema to include:
  - `moduleChecks[]`
  - `infraStatus`
  - `featureStatus`

Acceptance criteria:
- Validator rejects placeholder test patterns.
- Validator validates module contracts conditionally by enabled flags.
- Report output supports machine-readable release decisions.

## WS4: Core UI Foundation Module (P1)

Goals:
- Ship a practical default UI baseline.

Planned changes:
- Add reusable templates for:
  - Home screen with loading/empty/error states
  - Bottom tab navigation baseline (`Home`, `Explore`, `Profile`)
  - Profile page skeleton (avatar placeholder + account/settings actions)
  - Placeholder app icon/splash assets + replacement checklist
- Add `references/ui-foundation.md` with required routes/state patterns.

Acceptance criteria:
- Generated app with `WithUiFoundation` has complete baseline route structure.
- All UI foundation screens compile and pass lint/typecheck/tests.
- Placeholder icon/splash assets are present and clearly marked for replacement.

## WS5: Auth and Secure Session Module (P1)

Goals:
- Provide optional but production-structured auth starter.

Planned changes:
- Add auth template pack:
  - Sign-in screen
  - Session context/provider
  - Secure token storage abstraction
  - Sign-out flow hook
- Add provider slots:
  - Email/password baseline
  - OAuth placeholders (Apple/Google)
- Add `references/auth-patterns.md` for lifecycle and secure-storage rules.

Acceptance criteria:
- `WithAuth` scaffolds all required auth files and wiring.
- Session persistence works via secure storage abstraction.
- Auth smoke tests cover sign-in state transition and sign-out cleanup.

## WS6: Push Notifications Module (P1)

Goals:
- Provide optional end-to-end push baseline.

Planned changes:
- Add notifications template pack:
  - Permission request flow
  - Token registration flow (API contract placeholder)
  - Foreground/background handling stubs
  - Deep-link payload routing placeholder
- Add `references/notifications.md` for APNs/Expo token lifecycle.

Acceptance criteria:
- `WithPush` generates notification setup and permission flow files.
- Build config supports notifications module contract.
- Smoke test validates registration flow logic (mocked).

## WS7: Profile/Settings and Data Layer Module (P1)

Goals:
- Add common app-level foundation beyond UI shell.

Planned changes:
- Profile/settings module:
  - Profile screen sections
  - Settings route + toggles scaffold
  - Account actions placeholders
- Data layer module:
  - API client wrapper
  - Error/retry utilities
  - Offline-aware cache strategy starter
  - Standard loading/error/empty model helpers

Acceptance criteria:
- `WithProfile` and `WithDataLayer` produce wired, typed templates.
- Data layer pattern is documented and used by Home/Profile samples.
- Smoke tests cover success + failure + retry path.

## WS8: Observability and Production Hardening (P2)

Goals:
- Raise default production quality without forcing provider lock-in.

Planned changes:
- Analytics module placeholders with event naming conventions.
- Crash reporting module placeholders (Sentry-compatible pattern).
- Accessibility checklist and gate integration.
- Localization starter (default locale, fallback behavior, string structure).
- Privacy/compliance checklist for App Store submission.

Acceptance criteria:
- Each enabled hardening flag adds required files/config/docs.
- Accessibility and localization checks included in quality workflow.
- Privacy checklist appears in final status report.

## WS9: CI/EAS Release Pipeline Hardening (P0 + P2)

Goals:
- Make CI release path deterministic and safer by default.

Planned changes:
- Parameterize release branch in workflow template generation.
- Pin critical tool versions where practical.
- Introduce safer default release flow:
  - optional manual approval gate for submit
  - explicit environment checks before submit
- Distinguish build success from submit success in reporting.

Acceptance criteria:
- CI branch target follows `ReleaseBranch` input.
- Workflow behavior is deterministic across reruns.
- Submit step is controllable via explicit gate/flag.

## Milestones

1. M1: P0 completion
- WS1 + WS2 + WS3 + WS9 baseline
- Exit: both scaffold variants pass all baseline gates in clean runs

2. M2: P1 completion
- WS4 + WS5 + WS6 + WS7
- Exit: UI/Auth/Push/Profile/Data modules scaffold and validate by flags

3. M3: P2 completion
- WS8 + WS9 hardening refinements
- Exit: observability, a11y, localization, privacy quality gates active

## Task Mapping to Audit Items

P0 mapping:
- Gate reliability: WS2, WS3
- Real tests (no placeholder): WS3
- `app.config.ts` implementation: WS2
- Branch parameterization: WS2, WS9
- Validator anti-placeholder rule: WS3

P1 mapping:
- General UI starter modules: WS4
- Auth starter modules: WS5
- Push starter modules: WS6
- Profile/settings starter: WS7
- API/error/retry/cache starter: WS7

P2 mapping:
- Analytics placeholders: WS8
- Crash reporting placeholders: WS8
- Accessibility gates: WS8
- Localization starter: WS8
- Privacy/App Store checklist: WS8

## Validation Strategy

For each milestone:

1. Generate at least two fresh projects:
- one `blank-typescript`
- one `tabs`
2. Run local quality gates:
- `npm run lint`
- `npm run typecheck`
- `npm run test`
3. Run validator with report output.
4. Verify CI workflow file and branch routing.
5. Verify feature-flag permutations (module-specific smoke checks).

## Risks and Mitigations

- Risk: Dependency drift in Expo ecosystem breaks deterministic gates.
  - Mitigation: Pin and validate dependency ranges; run scheduled smoke scaffolds.
- Risk: Feature flag combinations explode complexity.
  - Mitigation: Define supported combinations matrix in `references/feature-modules.md`.
- Risk: Over-scaffolded apps become bloated.
  - Mitigation: Keep modules opt-in and minimal by default.
- Risk: False confidence in push/auth without backend.
  - Mitigation: Mark backend-dependent steps as explicit placeholders in reports.

## Deliverables Checklist

- [ ] Updated framework skill contracts and status model
- [ ] P0 script and validator upgrades
- [ ] Core UI foundation templates
- [ ] Auth templates + secure session patterns
- [ ] Notifications templates + permission/token flow
- [ ] Profile/settings and data-layer templates
- [ ] Analytics/crash placeholders
- [ ] Accessibility/localization/privacy references and gates
- [ ] CI/EAS branch parameterization and deterministic defaults
- [ ] End-to-end smoke validation reports for each milestone

## Execution Order Recommendation

1. Complete M1/P0 first (stability before breadth).
2. Implement M2/P1 modules in this order: UI -> Data/Profile -> Auth -> Push.
3. Complete M3/P2 hardening and finalize reporting.
4. Re-run full matrix validation and publish updated DoD.

