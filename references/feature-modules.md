# Feature Modules

## PRD-Driven Module Selection
- Feature flags are derived from PRD `Section 3` using `references/prd-mapping.md`.
- If PRD enables unsupported modules, return `BLOCKED_INPUT` before scaffold.
- Manual flag overrides are allowed only when they do not conflict with PRD scope.

## Supported Module Flags
- `WithUiFoundation`: tabs baseline (`Home`, `Explore`, `Profile`) and UI state patterns.
- `WithProfile`: profile/settings placeholders.
- `WithAuth`: sign-in, secure session storage, and OAuth provider slot scaffolding.
- `WithPush`: push permission flow, token registration helpers, and deep-link payload parsing.
- `WithDataLayer`: API client baseline with retry policy and cache policy helpers.
- `WithAnalytics`: analytics placeholder utilities.
- `WithCrashReporting`: crash reporter placeholder utilities.
- `WithLocalization`: localization scaffolding.
- `WithAccessibilityChecks`: accessibility checklist doc.
- `WithPrivacyChecklist`: privacy checklist doc.
- `WithDeploymentLayer`: release human-input intake doc (`release/human-inputs.md`).

## Default Behavior
- `WithTabs` implies `WithUiFoundation`.
- `WithProfile` implies `WithUiFoundation`.
- Other modules are opt-in.
- `WithDeploymentLayer` defaults to enabled.

## Compatibility Rules
- `WithUiFoundation` and `WithTabs` are compatible and intended together.
- `WithAuth` can be enabled without backend integration; generated OAuth flows are explicit provider slots with setup guidance.
- `WithPush` includes client-side deep-link parsing and still requires backend token registration endpoint integration.
- `WithDataLayer` defaults to safe retries and in-memory cache; replace with product-specific persistence for offline-first apps.
- `WithAnalytics` and `WithCrashReporting` add placeholder adapters only.

## Module Contract Files
When enabled, each module must create files under these roots:
- UI foundation: `app/(tabs)/*`, `src/ui/*`
- Profile/settings: `app/settings.tsx`, `src/profile/*`
- Auth: `app/sign-in.tsx`, `src/auth/*`, `__tests__/auth-oauth.test.ts`
- Push: `src/notifications/*`, `__tests__/notification-deeplink.test.ts`
- Data layer: `src/data/*`, `__tests__/async-resource.test.ts`
- Analytics/crash: `src/observability/*`
- Localization: `src/localization/*`
- Accessibility/privacy: `docs/*-checklist.md`
- Deployment layer: `release/human-inputs.md`

## Validator Expectations
- `skill.modules.json` must exist with boolean flags.
- Enabled flags require matching module contract files (including module-specific tests).
- Disabled flags do not require module contract files.
- When `withDeploymentLayer` is enabled, validator checks `release/human-inputs.md` for required `KEY = value` entries.
