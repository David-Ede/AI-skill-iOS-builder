# Architecture

## App Architecture Defaults
- Framework: Expo managed workflow.
- Navigation: Expo Router file-based routes.
- Language: TypeScript.
- Platform emphasis: iOS-first, parity-safe where low cost.
- Package manager baseline: npm.

## Folder Conventions
- `app/_layout.tsx`: root navigation container.
- `app/index.tsx`: initial entry route.
- `app/(tabs)/*`: tabs routes when tabs/UI module is enabled.
- `src/`: feature and shared app code.
- `__tests__/`: smoke tests and feature tests.
- `assets/`: static assets and placeholders.
- `eas.json`: EAS profile configuration.
- `.github/workflows/eas-ios.yml`: CI workflow added by setup script.

## Configuration Contract
- `package.json.main` must be `expo-router/entry`.
- `app.json` or `app.config.ts` must include `ios.bundleIdentifier`.
- Expo config plugins must include `expo-router`.
- If `WithPush` is enabled, active Expo config must include `expo-notifications` plugin.
- `eas.json.build.preview` and `eas.json.build.production` must exist.
- `.gitignore` should include `.expo/` and `.expo-shared/`.
- `skill.modules.json` must exist and reflect enabled feature flags.

## Quality Contract
- Keep scripts present in `package.json`:
  - `lint`
  - `typecheck`
  - `test`
- `scripts.test` cannot be a placeholder/no-op.
- Smoke tests must include app-shell coverage.
- Enabled feature modules must include their contract test files.

## Compatibility Boundaries
Blocked for this skill:
- React Navigation baseline replacement.
- Bare React Native CLI scaffold path.
- Non-npm package manager assumptions.
- Non-EAS release pipeline requirements.

Risk conditions:
- Missing App Store Connect app record for the bundle identifier.
- Missing signing credentials or CI secrets for submit flow.
- Node version drift that breaks Expo ecosystem commands.
- Unsupported feature-flag combinations.

## Non-Goals
- Do not treat this skill as the primary path for migrating large existing repositories.
- Do not optimize for bare React Native or UIKit-native module authoring.
- Do not treat optional module templates as fully production-integrated backend implementations.
