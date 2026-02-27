# Feature Modules

## Supported Module Flags
- `WithUiFoundation`: tabs baseline (`Home`, `Explore`, `Profile`) and UI state patterns.
- `WithProfile`: profile/settings placeholders.
- `WithAuth`: sign-in and secure session scaffolding.
- `WithPush`: push permission and token registration scaffolding.
- `WithDataLayer`: API client and async state helper scaffolding.
- `WithAnalytics`: analytics placeholder utilities.
- `WithCrashReporting`: crash reporter placeholder utilities.
- `WithLocalization`: localization scaffolding.
- `WithAccessibilityChecks`: accessibility checklist doc.
- `WithPrivacyChecklist`: privacy checklist doc.

## Default Behavior
- `WithTabs` implies `WithUiFoundation`.
- `WithProfile` implies `WithUiFoundation`.
- Other modules are opt-in.

## Compatibility Rules
- `WithUiFoundation` and `WithTabs` are compatible and intended together.
- `WithAuth` can be enabled without backend integration; generated code uses placeholders.
- `WithPush` requires manual backend/API integration for token registration.
- `WithAnalytics` and `WithCrashReporting` add placeholder adapters only.

## Module Contract Files
When enabled, each module must create files under these roots:
- UI foundation: `app/(tabs)/*`, `src/ui/*`
- Profile/settings: `app/settings.tsx`, `src/profile/*`
- Auth: `app/sign-in.tsx`, `src/auth/*`
- Push: `src/notifications/*`
- Data layer: `src/data/*`
- Analytics/crash: `src/observability/*`
- Localization: `src/localization/*`
- Accessibility/privacy: `docs/*-checklist.md`

## Validator Expectations
- `skill.modules.json` must exist with boolean flags.
- Enabled flags require matching module contract files.
- Disabled flags do not require module contract files.
