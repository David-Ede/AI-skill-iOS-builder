# Accessibility and Localization

## Accessibility Baseline Checklist
- Interactive controls expose accessible labels.
- Touch targets are large enough for standard mobile accessibility expectations.
- Color contrast is reviewed for primary surfaces.
- App appearance follows system light/dark mode (`userInterfaceStyle: "automatic"`).
- Screens/components use shared semantic theme tokens instead of per-screen hard-coded palette values.
- Screen reader order is logical for Home and Profile screens.

## Localization Baseline Checklist
- Centralize app strings in localization files.
- Define default locale and fallback locale.
- Avoid hard-coding user-facing strings in screens where localization module is enabled.

## Validation Expectations
- If `WithAccessibilityChecks` is enabled, `docs/accessibility-checklist.md` exists.
- If `WithLocalization` is enabled, localization files exist and compile.
