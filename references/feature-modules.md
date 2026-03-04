# Feature Modules

## Module Strategy
- This skill provides scaffold templates for common mobile foundations.
- Scaffold output is not final product behavior.
- Every enabled PRD module must be implemented with real feature code and tests before release.

## Scaffold-Template Flags
- `WithUiFoundation`: base routes and theme tokens.
- `WithProfile`: profile/settings shell.
- `WithAuth`: auth/session baseline.
- `WithPush`: push/deep-link baseline.
- `WithDataLayer`: request + cache baseline.
- `WithAnalytics`: analytics adapter baseline.
- `WithCrashReporting`: crash adapter baseline.
- `WithLocalization`: i18n baseline.
- `WithAccessibilityChecks`: accessibility checklist.
- `WithPrivacyChecklist`: privacy checklist.
- `WithDeploymentLayer`: release intake file (`release/human-inputs.md`).

## Modules Without Direct Scaffold Flags
When PRD enables these modules, implement custom code/tests from PRD requirements:
- `MOD-CONTENT`
- `MOD-TRANSACT`
- `MOD-SOCIAL`
- `MOD-ADMIN`
- `MOD-INTEG`
- `MOD-SEARCH`
- `MOD-MEDIA`

## Default Behavior
- `WithTabs` implies `WithUiFoundation`.
- `WithProfile` implies `WithUiFoundation`.
- `WithDeploymentLayer` defaults to enabled.

## Contract Files
When enabled, template-backed modules must create baseline files:
- UI foundation: `app/(tabs)/*`, `src/ui/*` (including `src/ui/theme.ts`)
- Profile/settings: `app/settings.tsx`, `src/profile/*`
- Auth: `app/sign-in.tsx`, `src/auth/*`, `__tests__/auth-oauth.test.ts`
- Push: `src/notifications/*`, `__tests__/notification-deeplink.test.ts`
- Data layer: `src/data/*`, `__tests__/async-resource.test.ts`
- Analytics/crash: `src/observability/*`
- Localization: `src/localization/*`
- Accessibility/privacy: `docs/*-checklist.md`
- Deployment layer: `release/human-inputs.md`

## Production Implementation Contract
- Replace scaffold placeholder content in `app/`, `src/`, and `__tests__/`.
- Add feature-specific tests for module requirements (not only baseline tests).
- Maintain `<project>/reports/prd-implementation.json` with per-requirement code/test evidence.
- Validator must pass with `--prd-path` before release.
