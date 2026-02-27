# Expo iOS Skill Audit Additions (Temporary)

Last updated: 2026-02-21
Audit target: `C:/Users/David/Desktop/expo-ios-app-builder-skill`
Intent: Track additions needed before this skill can be treated as "fast path to launch."

## What the skill currently does well

- Greenfield Expo + TypeScript + Expo Router scaffold.
- Contract checks for app config, bundle ID, EAS profiles, basic scripts, and CI file presence.
- EAS/TestFlight baseline docs and GitHub Actions workflow template.
- Clear status model (`pass`, `partial`, `fail`) and human-gate handling.

## Current launch blockers already confirmed in smoke tests

- Quality gates do not reliably pass out of the box across scaffold variants.
- `app.config.ts` is documented as an option but not implemented in scripts.
- Release branch preference is documented but workflow is hard-coded to `main`.
- `test` gate can pass with a placeholder script and no real app behavior coverage.

## Common baseline iOS app feature stack (2026 practical baseline)

The list below reflects common "basic" product features expected in modern consumer/business iOS apps, beyond infrastructure and CI.

| Feature Area | Common Baseline | Current Skill Coverage | Gap |
| --- | --- | --- | --- |
| Core UI foundation | Home screen, bottom tab navigation, profile page, placeholder icon/splash, empty/loading/error states | Partial (router shell and optional tabs only) | High |
| Navigation & shell | Router, tabs/stack, app shell | Present | Low |
| Authentication | Email/password and/or OAuth/SSO; session persistence | Missing | High |
| Push notifications | APNs token flow, permission prompt strategy, deep link handling | Missing | High |
| User profile/settings | Profile screen, settings, sign-out, account delete hooks | Missing | High |
| Data layer | API client, error/retry handling, offline-aware cache strategy | Missing | High |
| State management | Selected default pattern and conventions | Missing | Medium |
| Forms & validation | Shared validation schema/patterns | Missing | Medium |
| Secure storage | Token storage using secure primitives | Missing | High |
| Permissions | Camera/location/photos/notifications policy pattern | Missing | Medium |
| Deep linking | URL scheme + universal link handling beyond router basics | Partial | Medium |
| Analytics | Event tracking baseline and naming conventions | Missing | Medium |
| Crash reporting | Error boundary + crash tool bootstrap | Missing | Medium |
| In-app updates/content | OTA strategy and safety rules | Partial | Medium |
| Accessibility | Baseline checks and acceptance criteria | Missing | Medium |
| Localization | i18n setup and fallback rules | Missing | Medium |
| Privacy/compliance | Privacy manifest guidance and data-usage notes | Missing | Medium |
| Monetization (if applicable) | IAP/subscription scaffolding | Missing | Context-dependent |
| Testing | Real smoke tests for critical user flows | Missing (policy says required) | High |

## Direct answers to current audit questions

- Push notifications included: **No**.
- Login/auth included: **No**.
- General UI baseline included (home, bottom bar, profile, placeholder icon): **Partial only**.
- "Basic iOS app features" support level: **infrastructure-strong, product-feature-light**.
- Fit to "build and launch an app fast with little groundwork": **good for scaffold and CI release plumbing, weak for app feature completeness**.

## Additions to implement in this skill (priority order)

### P0 (must-have for reliable baseline)

1. Make quality gates pass out of the box for both scaffold paths (`blank-typescript`, `tabs`).
2. Replace placeholder `test` script with real smoke tests and minimal fixtures.
3. Implement actual `app.config.ts` generation path when requested.
4. Parameterize workflow branch target instead of hard-coded `main`.
5. Improve validator to fail if `test` script is placeholder/no-op.

### P1 (core product feature starter packs)

1. Add optional general UI starter module templates:
- Home screen template with loading, empty, and error states.
- Bottom tab navigation baseline (Home, Explore, Profile or equivalent).
- Profile page template with avatar placeholder, account actions, and settings entrypoint.
- Placeholder icon/splash asset set and naming conventions.
2. Add optional auth module templates:
- Email/password baseline.
- OAuth provider slot (Apple/Google placeholder wiring).
- Secure session storage pattern.
3. Add optional push module templates:
- Expo notifications package setup.
- Permission prompt flow.
- Token registration endpoint contract placeholder.
4. Add optional app settings/profile route templates.
5. Add optional API client + fetch error handling + retry + cache guidance.

### P2 (quality and production hardening)

1. Add analytics integration placeholders and event naming reference.
2. Add crash reporting setup option (Sentry or equivalent placeholder).
3. Add accessibility checklist as a required quality gate section.
4. Add localization starter structure and required default language config.
5. Add privacy/compliance checklist for App Store submission readiness.

## Proposed skill structure changes

- `references/feature-modules.md`:
  - Feature flags supported by scaffold (`WithAuth`, `WithPush`, `WithProfile`, `WithAnalytics`, etc.).
  - Dependency contracts and incompatibilities.
- `references/ui-foundation.md`:
  - Required base routes, tab model, and screen state patterns.
  - Icon/splash placeholder policy and replacement checklist.
- `references/auth-patterns.md`:
  - Session lifecycle, secure storage, sign-in/out flows.
- `references/notifications.md`:
  - Permission timing, token lifecycle, APNs/Expo setup checklist.
- `assets/templates/feature-modules/...`:
  - Reusable route/components/hooks for UI foundation, auth, notifications, profile/settings.
- `scripts/scaffold_expo_ios_app.ps1`:
  - Add new switches and deterministic template copy/patch logic.
- `scripts/validate_expo_ios_project.py`:
  - Add optional feature-contract checks when switches enabled.

## Definition-of-done updates for skill quality

Add explicit requirement that generated apps include:

1. Passing `lint`, `typecheck`, and non-placeholder smoke tests.
2. Deterministic CI behavior with pinned critical versions.
3. Feature module contracts validated when corresponding switches are enabled.
4. Clear "infrastructure only" vs "feature-ready" status in final report.

## Recommended status for this skill today

- Infrastructure readiness: **Good**.
- Product baseline readiness (common app features): **Insufficient**.
- Overall for "ship a full app fast": **Partial** until P0 + selected P1 modules land.
