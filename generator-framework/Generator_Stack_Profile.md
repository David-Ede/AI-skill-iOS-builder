# Generator Stack Profile

## Purpose

Define the authoritative technical stack for the single-prompt app generator.
This file is the source of truth for:

- What the generator is allowed to build.
- What must be consistent across generated projects.
- What is intentionally excluded to keep one-session generation reliable.

Use this profile before writing PRDs, feature specs, execution plans, or scaffold logic.

---

## 1. Profile Identity

- Profile Name: `react-native-monorepo-single-prompt`
- Profile ID: `rn-spg-v1`
- Status: Active
- Effective Date: `2026-02-17`
- Repository Baseline: `mova-next`

---

## 2. Non-Negotiable Invariants

These are hard constraints for generated repos.

- Monorepo structure is required.
- Package manager is `npm` with workspaces (not `pnpm` for this profile).
- Native navigation is `React Navigation` (not Expo Router for this profile).
- Native app entrypoint must be workspace-safe (`apps/native/index.js` + `main: index.js`).
- Shared business logic lives in workspace packages, not copied per app.
- Platform adapters (web/native) own platform-specific SDK integrations.
- TypeScript strict mode is required across apps/packages.
- CI must run web and native tests plus release-readiness checks.

---

## 3. Runtime and Toolchain

| Area                 | Standard                                           |
| -------------------- | -------------------------------------------------- |
| Node runtime         | CI pinned to Node 22.x; local minimum Node 20.19.4 |
| Package manager      | npm (workspace mode)                               |
| Monorepo task runner | Turborepo                                          |
| Language             | TypeScript                                         |
| Lint/format          | ESLint + Prettier                                  |
| Git hooks            | Husky + lint-staged                                |

Notes:

- Keep a single lockfile at repo root.
- Keep React/React Native versions aligned via root overrides.
- Keep Expo ecosystem packages aligned with `npx expo install --check`.

---

## 4. Repository Topology

Required shape:

- `apps/web` (or root web app, if migration deferred)
- `apps/native`
- `packages/core`
- `packages/data`
- `packages/tokens`
- `packages/analytics`
- `packages/config`
- `scripts`
- `planning`
- `.github/workflows`

Current baseline notes:

- Web currently lives at repo root (`src`, `pages`) and native in `apps/native`.
- Generator may output either:
  - Target topology (preferred): `apps/web` + `apps/native`, or
  - Transitional topology (allowed): root web + `apps/native`.
- Selected topology must be declared in `product.config.yaml`.

---

## 5. Framework and Platform Stack

### 5.1 Web

- Framework: Next.js (Pages Router for this profile)
- UI: React + Tailwind CSS
- PWA: Serwist service worker
- State: Zustand

### 5.2 Native

- Framework: Expo managed workflow + Dev Client
- Native runtime: React Native
- Navigation: `@react-navigation/native` + native stack
- Entrypoint: `apps/native/index.js` registered via `registerRootComponent`
- JS engine: Hermes
- New architecture: enabled
- Build/Release: EAS (`development`, `preview`, `production`)

### 5.3 Backend and Services

- Auth/DB/Sync: Firebase
- Billing:
  - Web: Stripe
  - Native: Store IAP endpoints + server validation scaffolding
- Error monitoring: Sentry
- API rate limits: Upstash Redis ratelimit

---

## 6. Shared Package Boundaries

### `@mova/core`

- Domain logic, shared types, route contracts, state factories, utility logic.
- No direct platform SDK imports.

### `@mova/data`

- Content loading, data mappers, parsing helpers, HTTP content source wrappers.
- Depends on `@mova/core` types/contracts.

### `@mova/tokens`

- Design tokens: colors, spacing, radii, typography, shadows.
- Platform-agnostic token exports.

### `@mova/analytics`

- Event names, payload types, analytics client interface, noop/default adapters.

### `@mova/config`

- Shared TS/ESLint config artifacts.

---

## 7. Persistence and Adapter Model

- Web local persistence: IndexedDB (`idb-keyval`) via shared local-store contract.
- Native local persistence: AsyncStorage via shared local-store contract.
- Remote sync: Firebase adapters per platform.
- Fallback behavior: if Firebase config is unavailable, app must degrade safely with local mode where possible.

Contract rule:

- Storage keys and migration logic are owned in shared package code, not duplicated per platform.

---

## 8. Content Pipeline Contract

- Content source is structured data + wordlist + intro content.
- Prebuild step generates deterministic lesson artifacts in `public/data/lessons/**`.
- Generated artifacts are treated as build outputs with explicit commit policy.
- Generator must include:
  - prebuild command,
  - strict validation mode,
  - manifest output for generated lessons.

---

## 9. Testing and Quality Gates

Minimum required test stack:

- Unit/integration: Vitest (web/shared)
- Native unit/component: Jest + React Native Testing Library
- E2E web smoke: Playwright
- Firestore rules tests (emulator-backed)

Minimum required repo checks:

- Typecheck
- Lint
- Web tests
- Native tests
- Build
- Expo dependency sync check (`npx expo install --check`)
- Expo doctor (`npx expo-doctor`)
- Native export smoke (`npx expo export --platform android --output-dir dist-android --clear`)
- OTA config validation
- Bundle/performance budget checks (when metrics are present)

---

## 10. CI and Release Baseline

CI must include:

- Web + native install/build/test paths.
- Dummy env coverage for non-secret compile-time variables.
- OTA config validation script.
- Bundle size validation script.

Release baseline must include:

- `apps/native/app.config.ts` with `updates`, `runtimeVersion`, `jsEngine`, `newArchEnabled`.
- `apps/native/eas.json` with `development`, `preview`, `production` profiles.
- Release-readiness report artifact generation.

---

## 11. Generator Output Requirements from This Profile

A generated repo is compliant only if it includes:

- The required monorepo structure from this profile.
- Configured workspace aliases for `@mova/*`.
- Native metro config that extends Expo defaults (avoid overriding resolver invariants).
- Shared package boundaries preserved (no logic duplication).
- CI workflows for both app targets.
- A single `repo:check` entrypoint script that enforces required gates.

---

## 12. Versioning and Drift Policy

- This profile is versioned independently of feature specs.
- Any stack change (framework, package manager, navigation, release flow, runtime versions) must update:
  - this file,
  - input contracts,
  - output contract,
  - repo check gates.
- Do not mix incompatible profile assumptions in one generation run.

---

## 13. Explicitly Out of Scope (v1)

- Full automatic App Store / Play Store submission.
- Multi-backend provider abstraction beyond Firebase baseline.
- Multiple package-manager profiles in the same run.
- Expo Router profile support in the same generator track.
