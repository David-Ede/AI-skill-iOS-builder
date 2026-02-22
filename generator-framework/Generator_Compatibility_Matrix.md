# Generator Compatibility Matrix

## Purpose

Define the validated compatibility envelope for the single-prompt generator.
This file prevents stack drift and failed one-session builds by declaring:

- Approved version combinations.
- Risky but allowed combinations.
- Blocked combinations the generator must reject.
- Required preflight checks before generation starts.

---

## Scope

- Profile: `rn-spg-v1`
- Effective date: `2026-02-17`
- Baseline repo: `mova-next`
- Primary package manager: `npm` workspaces

---

## 1. Compatibility Policy

| Tier      | Meaning                                                 | Generator Behavior                       |
| --------- | ------------------------------------------------------- | ---------------------------------------- |
| `Pinned`  | Exact version or constrained set validated in this repo | Use by default                           |
| `Allowed` | Known to work but not primary baseline                  | Use only when explicitly requested       |
| `Risk`    | Works with caveats or preview dependencies              | Allow with warning + mitigation          |
| `Blocked` | Known conflict with this profile                        | Reject and suggest supported alternative |

---

## 2. Core Toolchain Matrix

| Component              | Pinned / Supported                  | Tier    | Notes                                        |
| ---------------------- | ----------------------------------- | ------- | -------------------------------------------- |
| Node.js (local)        | `>=20.19.4`                         | Pinned  | Required by RN 0.83.2 stack                  |
| Node.js (CI primary)   | `22.x`                              | Pinned  | Current main CI baseline                     |
| Node.js (CI secondary) | `20.x`                              | Risk    | Content-validation workflow still on Node 20 |
| npm                    | Workspace mode with single lockfile | Pinned  | Profile uses npm, not pnpm                   |
| TypeScript             | `5.3.3`                             | Pinned  | Shared across web/native/packages            |
| Turborepo              | `^2.0.0`                            | Allowed | Present; not all tasks fully wired yet       |
| ESLint                 | `^9.x`                              | Pinned  | Root lint baseline                           |
| Prettier               | `3.1.0`                             | Pinned  | Formatting baseline                          |

---

## 3. Web Stack Matrix

| Layer         | Pinned / Supported | Tier    | Notes                                |
| ------------- | ------------------ | ------- | ------------------------------------ |
| Next.js       | `^16.1.0`          | Pinned  | Pages Router baseline in current app |
| React (web)   | `19.2.0`           | Pinned  | Must match root override             |
| React DOM     | `19.2.0`           | Pinned  | Must match React                     |
| Tailwind CSS  | `^3.4.1`           | Pinned  | Existing style baseline              |
| Zustand       | `^5.0.8`           | Pinned  | Shared state baseline                |
| Serwist / PWA | `^9.0.9`           | Allowed | Active in current Next config        |
| Vitest        | `^4.0.16`          | Pinned  | Web/shared unit tests                |
| Playwright    | `^1.51.1`          | Allowed | E2E smoke coverage baseline          |

---

## 4. Native Stack Matrix

| Layer                 | Pinned / Supported             | Tier    | Notes                                      |
| --------------------- | ------------------------------ | ------- | ------------------------------------------ |
| Expo                  | `55.0.0-preview.11`            | Risk    | Preview pin; monitor stable tag            |
| React Native          | `0.83.2`                       | Pinned  | Locked via root overrides                  |
| React (native)        | `19.2.0`                       | Pinned  | Must match RN compatibility set            |
| React Navigation      | `^7.0.0`                       | Pinned  | Required by this profile                   |
| Expo Dev Client       | `55.0.1`                       | Allowed | Required only if custom native modules are used |
| Expo Status Bar       | `~55.0.3`                      | Pinned  | Keep aligned with Expo SDK                |
| RN Firebase           | `^21.0.0`                      | Allowed | Platform adapters should isolate SDK usage |
| Jest (native)         | `^29.7.0` + `jest-expo ~55.0.6` | Pinned | Native unit/component testing baseline     |
| Babel preset          | `babel-preset-expo ~55.0.5`    | Pinned  | Must match Expo SDK patch line            |
| EAS CLI compatibility | `cli.version >= 4.0.0`         | Pinned  | Declared in `apps/native/eas.json`         |

---

## 5. Shared Package and Contract Matrix

| Contract Area         | Requirement                                    | Tier    | Notes                                 |
| --------------------- | ---------------------------------------------- | ------- | ------------------------------------- |
| Workspace aliases     | `@mova/*` path mapping in web/native TS config | Pinned  | Required for shared packages          |
| Shared core logic     | `@mova/core` owns domain/store/contracts       | Pinned  | No platform SDK imports in core       |
| Data/content adapters | `@mova/data` + platform fetch/storage adapters | Pinned  | Keep content loading deterministic    |
| Design tokens         | `@mova/tokens` for web + native                | Pinned  | Avoid duplicated style constants      |
| Analytics contract    | `@mova/analytics` typed event interface        | Allowed | Can use noop adapter in fallback mode |

---

## 6. Backend and Service Matrix

| Service                 | Pinned / Supported                                    | Tier    | Notes                     |
| ----------------------- | ----------------------------------------------------- | ------- | ------------------------- |
| Firebase Web SDK        | `^12.6.0`                                             | Pinned  | Web auth/data path        |
| Firebase Admin SDK      | `^13.6.0`                                             | Pinned  | API/server tasks          |
| Firestore rules testing | `@firebase/rules-unit-testing ^3.0.1`                 | Allowed | Emulator-backed checks    |
| Stripe (web billing)    | `stripe ^20.0.0`, `@stripe/stripe-js ^8.5.3`          | Allowed | Web billing baseline      |
| Sentry                  | `@sentry/nextjs ^8.20.0`                              | Allowed | Error monitoring baseline |
| Upstash                 | `@upstash/redis ^1.34.3`, `@upstash/ratelimit ^2.0.4` | Allowed | API rate-limit baseline   |

---

## 7. Known Good Combination Set (Default for Generator)

Use this exact set unless user explicitly requests variation:

| Area              | Default                      |
| ----------------- | ---------------------------- |
| Node              | Local `>=20.19.4`, CI `22.x` |
| Package manager   | npm workspaces               |
| Web framework     | Next.js Pages Router         |
| Native framework  | Expo managed + Dev Client    |
| Navigation        | React Navigation             |
| React / React DOM | `19.2.0`                     |
| React Native      | `0.83.2`                     |
| Expo              | `55.0.0-preview.11`          |
| State             | Zustand                      |
| Backend           | Firebase                     |

---

## 8. Blocked Combinations (Must Reject in v1)

| Requested Combination                          | Status  | Why Blocked                                          | Fallback                        |
| ---------------------------------------------- | ------- | ---------------------------------------------------- | ------------------------------- |
| `pnpm` generator profile + current `rn-spg-v1` | Blocked | Current baseline scripts/workflows are npm-based     | Use npm workspaces              |
| Expo Router with `rn-spg-v1`                   | Blocked | Native baseline and parity plan use React Navigation | Use React Navigation            |
| Node `<20.19.4` with RN `0.83.2`               | Blocked | Known runtime incompatibility                        | Upgrade Node                    |
| Multi-navigation strategy in one run           | Blocked | Increases drift and codegen ambiguity                | Single nav strategy per profile |
| Multiple package managers in one repo profile  | Blocked | Non-deterministic CI and lockfile behavior           | Use single manager              |

---

## 9. Risk Combinations (Allowed with Warning)

| Combination                                     | Risk                                       | Required Mitigation                                 |
| ----------------------------------------------- | ------------------------------------------ | --------------------------------------------------- |
| Expo `55.0.0-preview.11`                        | Preview dependency can change unexpectedly | Pin exact version and validate native build in CI   |
| Mixed CI Node versions (`22` + `20`)            | Potential subtle behavior differences      | Normalize workflows to one major (recommended `22`) |
| RN Firebase without native config files present | Runtime adapter fallback / disabled sync   | Enforce human-gate checklist for config files       |

---

## 10. Generator Preflight Checks

Generator must run and pass these checks before writing scaffold output:

| Check                   | Command / Rule                        | Pass Criteria                           |
| ----------------------- | ------------------------------------- | --------------------------------------- |
| Node version            | `node -v`                             | Meets policy for requested profile      |
| npm workspace readiness | `npm -v` + workspace config exists    | npm available and workspaces configured |
| Dependency install      | `npm ci`                              | Completes with no lockfile drift        |
| Type system             | `npm run typecheck --if-present`      | Pass                                    |
| Web tests               | `npm test -- --run`                   | Pass                                    |
| Native tests            | `npm --workspace apps/native test`    | Pass                                    |
| Expo dependency sync    | `npx expo install --check`             | No dependency mismatch warnings         |
| Expo doctor             | `npx expo-doctor`                      | All checks pass                         |
| Expo cache ignore       | `.gitignore` contains `.expo/` and `.expo-shared/` (root + `apps/native`) | No Expo doctor setup warnings |
| Native export smoke     | `npx expo export --platform android --output-dir dist-android --clear` | Bundle export succeeds |
| OTA baseline            | `node scripts/validate-ota-config.js` | Pass                                    |
| Web build               | `npm run build`                       | Pass                                    |
| Bundle budgets          | `node scripts/check-bundle-sizes.js`  | Pass or explicit skip conditions met    |

---

## 11. Compatibility Decision Rules for LLM Runs

When generating from one prompt:

1. Resolve requested stack against this matrix.
2. If any `Blocked` combination is requested, stop and return a structured incompatibility report.
3. If `Risk` combinations are used, include explicit warnings and required mitigations in the generated execution plan.
4. Record the chosen compatibility set in generated artifacts (`exec-plan.generated.md` and run metadata).

---

## 12. Upgrade Workflow

Any stack upgrade must:

1. Update this matrix first.
2. Update `Generator_Stack_Profile.md`.
3. Re-run full repo checks.
4. Update `Generator_Failure_Playbook.md` with new failure modes.
5. Tag the matrix revision date and changed components.

---

## 13. Changelog

### 2026-02-17

- Initial matrix created from current `mova-next` baseline.
- Marked Expo SDK 55 preview as `Risk`.
- Captured npm-workspace + React Navigation profile as default.

### 2026-02-18

- Updated native compatibility pins to Expo `55.0.0-preview.11` and React Native `0.83.2`.
- Added Expo package alignment (`expo install --check`) and `expo-doctor` preflight requirements.
- Added native export smoke preflight to catch app entrypoint and Metro resolution failures.
