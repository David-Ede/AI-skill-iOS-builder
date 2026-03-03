# UI Foundation

## Required Routes
When UI foundation is enabled:
- `app/index.tsx` redirects to `/(tabs)`.
- `app/(tabs)/index.tsx` exists (`Home`).
- `app/(tabs)/explore.tsx` exists (`Explore`).
- `app/(tabs)/profile.tsx` exists (`Profile`).
- `app/(tabs)/_layout.tsx` configures bottom tabs.
- `src/ui/theme.ts` defines semantic tokens and color-scheme hooks.

## Screen State Pattern
Home screen should provide baseline UI states:
- `loading`
- `empty`
- `error`
- `ready`

## Appearance Baseline
- Use system appearance by default (`userInterfaceStyle: "automatic"` in app config).
- Use semantic theme tokens in screens/components instead of hard-coded colors.
- Set status bar style from active color scheme (`light` in dark mode, `dark` in light mode).

## Placeholder Assets Policy
Generated app must include placeholder tracking notes for:
- App icon replacement
- Splash image replacement

Use `assets/templates/icons-splash/` content as source and keep replacement notes explicit.

## Baseline UX Expectations
- Home route renders on launch.
- Explore route exists for second-route smoke coverage.
- Profile route includes a path to settings/account actions.
