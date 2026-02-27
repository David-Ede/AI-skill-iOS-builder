# Repo Check Gates

## Purpose

Define the canonical gate set for `repo:check`.
This document specifies:

- Which checks must run.
- In what order they run.
- Which failures are release-blocking.
- How gate results are reported.

---

## Scope

- Profile: `rn-spg-v1`
- Effective Date: `2026-02-17`
- Related Contracts:
  - `Generator_Stack_Profile.md`
  - `Generator_Compatibility_Matrix.md`
  - `Generator_Output_Contract.md`
  - `Generator_Parity_Contract.md`

---

## 1. Gate Execution Policy

### 1.1 Execution Mode

Default mode: `collect-all`

- Run all gates in order.
- Record results for each gate even if an earlier gate fails.
- Final status is computed after all gates complete.

Optional mode: `fail-fast`

- Stop at first blocking failure.
- Allowed only for local speed-up runs.
- CI must use `collect-all`.

### 1.2 Gate Result States

Each gate must end in one of:

- `pass`
- `fail`
- `skipped`

### 1.3 Blocking Levels

| Level           | Meaning                                                  |
| --------------- | -------------------------------------------------------- |
| `Blocker`       | Failing gate makes overall status `fail`                 |
| `Conditional`   | Failing gate can produce `partial` if explicitly allowed |
| `Informational` | Never blocks; reported only                              |

---

## 2. Required Environment Baseline

Before gate execution:

- Node version must satisfy profile policy.
- npm workspace install must complete.
- Required CI dummy env vars must be available for non-secret compile-time config.

Minimum env values for CI/local parity:

- `CI=true` (CI only)
- `NEXT_PUBLIC_SITE_URL`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `EXPO_PUBLIC_API_BASE_URL`
- `EXPO_PUBLIC_FIREBASE_PROJECT_ID`
- `EXPO_PUBLIC_FIREBASE_API_KEY`

---

## 3. Gate Sequence (Canonical)

Run gates in this exact order.

| Gate ID  | Name               | Command (root-web)                          | Blocking    | Skip Allowed                 |
| -------- | ------------------ | ------------------------------------------- | ----------- | ---------------------------- |
| `RG-001` | Workspace Install  | `npm ci`                                    | Blocker     | No                           |
| `RG-002` | Type Check         | `npm run typecheck --if-present`            | Blocker     | No                           |
| `RG-003` | Lint               | `npm run lint --if-present`                 | Blocker     | No                           |
| `RG-004` | Web Unit Tests     | `npm test -- --run`                         | Blocker     | No                           |
| `RG-005` | Native Tests       | `npm --workspace apps/native test`          | Blocker     | No                           |
| `RG-006` | Content Validation | `npm run validate-content --if-present`     | Conditional | Yes (if no content pipeline) |
| `RG-007` | OTA Config         | `node scripts/validate-ota-config.js`       | Blocker     | No                           |
| `RG-008` | Web Build          | `npm run build`                             | Blocker     | No                           |
| `RG-009` | Bundle Budget      | `node scripts/check-bundle-sizes.js`        | Blocker     | Conditional                  |
| `RG-010` | Performance Budget | `node scripts/check-performance-budgets.js` | Conditional | Yes                          |
| `RG-011` | Parity Contract    | `node scripts/check-parity-contract.js`     | Blocker     | Conditional (see policy)     |
| `RG-012` | Output Contract    | `node scripts/check-output-contract.js`     | Blocker     | No                           |
| `RG-013` | Secret Scan        | `node scripts/scan-secrets.js`              | Blocker     | No                           |
| `RG-014` | Native Doctor      | `npm --workspace apps/native run doctor` | Blocker  | No                           |
| `RG-015` | Native Export Smoke | `npm --workspace apps/native run export:android` | Blocker | No |

Notes:

- `RG-011` through `RG-015` are required generator gates even if scripts are introduced incrementally.
- If a required gate script is missing, that gate is `fail` (not `skipped`) unless explicitly marked transitional in run config.
- `RG-003` is valid only when it runs a real linter; placeholder/no-op commands are treated as `fail`.

---

## 4. Topology-Aware Command Mapping

`product.config.yaml.topology` controls command variants:

### 4.1 `root-web`

Use root commands from gate table above.

### 4.2 `apps-web`

Use workspace-scoped web commands:

- Typecheck: `npm --workspace apps/web run typecheck --if-present`
- Lint: `npm --workspace apps/web run lint --if-present`
- Tests: `npm --workspace apps/web test -- --run`
- Build: `npm --workspace apps/web run build`

Native and shared gates remain root/workspace as listed.

---

## 5. Skip Policy

Skips are allowed only when explicitly documented.

### 5.1 Allowed Skip Cases

| Gate ID  | Allowed Skip Condition                                  | Result Treatment                            |
| -------- | ------------------------------------------------------- | ------------------------------------------- |
| `RG-006` | Content pipeline not present in generated profile       | `skipped`, non-blocking                     |
| `RG-009` | Build artifact path intentionally absent and documented | `skipped`, becomes `partial` if strict mode |
| `RG-010` | `reports/performance-metrics.json` missing              | `skipped`, non-blocking                     |
| `RG-011` | Transitional enablement explicitly set in run config    | `skipped`, may still yield `partial`        |

### 5.2 Invalid Skips

A gate marked `No` in "Skip Allowed" cannot be skipped.
If skipped, treat as `fail`.

---

## 6. Gate Failure Policy

### 6.1 Blocker Failures

Any blocker failure makes overall repo-check status `fail`.

### 6.2 Conditional Failures

Conditional failures may produce:

- `partial` if explicitly allowed and documented in summary.
- `fail` in strict production mode when no waiver exists.

### 6.3 Informational Failures

Informational failures do not block status but must be reported.

---

## 7. Parity Gate Contract (`RG-011`)

`RG-011` validates generated parity evidence against `Generator_Parity_Contract.md`.

Minimum required checks:

- All P0 routes present in generated output.
- No P0 route marked `fail`.
- P1 pass rate meets threshold for overall `pass`.
- Allowed divergences are explicitly documented.

Failure mapping:

- Missing P0 route -> blocker fail.
- P1 threshold miss -> conditional fail (`partial` default).

---

## 8. Output Contract Gate (`RG-012`)

`RG-012` validates generated repository against `Generator_Output_Contract.md`.

Minimum required checks:

- Required files/folders exist.
- Required scripts exist in root `package.json`.
- Required reports exist.
- Required native config keys exist.

Any missing required artifact is blocker fail.

---

## 9. Secret Scan Gate (`RG-013`)

`RG-013` checks generated output for secret leakage.

Minimum patterns to detect:

- PEM/private key blocks
- service account JSON key signatures
- API keys in known key formats
- high-entropy token patterns

Policy:

- Any confirmed leak -> blocker fail.
- False positives must be allowlisted explicitly in scan config.

---

## 10. Native Doctor Gate (`RG-014`)

`RG-014` validates Expo project health in native workspace output.

Minimum required checks:

- No dependency mismatch warnings from Expo SDK validation.
- No duplicate native module dependency findings.
- `.expo` and `.expo-shared` directories are ignored in git.
- Native `app.config.ts` schema check passes.

Failure mapping:

- Any failed `expo-doctor` check -> blocker fail.

---

## 11. Native Export Smoke Gate (`RG-015`)

`RG-015` validates that the app can be bundled in non-interactive CI mode.

Minimum required checks:

- `expo export` completes with exit code `0`.
- Entry point resolution succeeds (`apps/native/index.js` path).
- Metro resolver loads workspace packages without custom invariant-breaking overrides.

Failure mapping:

- Any bundle/export failure -> blocker fail.

---

## 12. `repo-check.report.json` Contract

Output file: `reports/repo-check.report.json`

Required top-level fields:

- `schemaVersion` (integer)
- `runId` (string)
- `status` (`pass|partial|fail`)
- `startedAt` (ISO timestamp)
- `finishedAt` (ISO timestamp)
- `checks` (array)
- `failedChecks` (array)

Each `checks[]` item must include:

- `id` (e.g., `RG-001`)
- `name`
- `command`
- `blocking` (`Blocker|Conditional|Informational`)
- `result` (`pass|fail|skipped`)
- `durationMs`
- `reason` (required for `fail` or `skipped`)

Optional fields:

- `artifacts`
- `warnings`
- `metrics`
- `parity` (for `RG-011`)

---

## 13. Overall Status Computation

Compute final status with this precedence:

1. If any blocker gate failed -> `fail`.
2. Else if any conditional gate failed/skipped with waiver -> `partial`.
3. Else if any informational gate failed -> `pass` with warnings.
4. Else -> `pass`.

Strict production rule:

- In strict mode, conditional failures without explicit waiver become `fail`.

---

## 14. Timeouts and Stability Controls

Recommended max durations:

- Install/build gates: 20 minutes each
- Test gates: 15 minutes each
- Script gates: 5 minutes each

Stability rules:

- No interactive prompts allowed.
- No destructive git commands in gates.
- Commands must be deterministic and repeatable.

---

## 15. Implementation Notes for Current Baseline

Already available gates in current repo:

- `RG-001` through `RG-010` (with some conditional behavior in scripts).

Planned/required for full generator enforcement:

- `RG-011` parity checker script.
- `RG-012` output contract checker script.
- `RG-013` secret scan script.
- `RG-014` native doctor command wiring.
- `RG-015` native export smoke command wiring.

Until full implementation, runs must report missing scripted gates explicitly and set status accordingly.

---

## 16. Changelog

### 2026-02-17

- Initial gate contract created for `repo:check`.
- Added gate IDs, execution order, blocking policy, topology mapping, skip rules, and report schema.

### 2026-02-18

- Added `RG-014` (`expo-doctor`) and `RG-015` (native export smoke) as blocking gates.
- Clarified that Expo health and export checks are mandatory to catch entrypoint and Metro regressions.
