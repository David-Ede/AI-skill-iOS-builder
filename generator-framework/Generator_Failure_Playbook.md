# Generator Failure Playbook

## Purpose

Provide deterministic diagnosis and recovery steps for single-prompt generator failures.
This playbook maps failures to:

- run phase
- gate ID
- error signature
- root-cause classes
- immediate recovery actions
- prevention actions

---

## Scope

- Profile: `rn-spg-v1`
- Effective Date: `2026-02-17`
- Related Contracts:
  - `Generator_Prompt_Protocol.md`
  - `Generator_Compatibility_Matrix.md`
  - `Repo_Check_Gates.md`
  - `Generator_Output_Contract.md`
  - `Generator_Data_Adapter_Contract.md`
  - `Generator_Parity_Contract.md`

---

## 1. Severity and Status Mapping

| Severity | Meaning                                         | Expected Run Status  |
| -------- | ----------------------------------------------- | -------------------- |
| `S0`     | Blocking contract violation or security risk    | `fail`               |
| `S1`     | Blocking build/test gate failure                | `fail`               |
| `S2`     | Conditional gate failure with valid waiver path | `partial`            |
| `S3`     | Non-blocking warning/informational drift        | `pass` with warnings |

Rule:

- If any blocker gate fails, overall run is `fail`.

---

## 2. Triage Workflow (Mandatory)

Follow this sequence for every failure:

1. Identify failure phase (input, compatibility, scaffold, repo-check, finalization).
2. Capture the first failing gate ID and exact error signature.
3. Classify root cause into one class from section 3.
4. Apply immediate recovery steps for that gate.
5. Re-run only the affected gate, then re-run full `repo:check`.
6. Record resolution in `reports/generation.report.json` and `planning/generated/generation.summary.md`.

---

## 3. Root-Cause Classes

| Class           | Description                                                         |
| --------------- | ------------------------------------------------------------------- |
| `RC-CONTRACT`   | Input/output contract mismatch or missing required artifact         |
| `RC-COMPAT`     | Blocked/incompatible version/toolchain combination                  |
| `RC-ENV`        | Missing env vars, wrong Node version, missing runtime prerequisites |
| `RC-DEP`        | Dependency install/drift/resolution failure                         |
| `RC-BUILD`      | Typecheck/lint/test/build failure in generated code                 |
| `RC-ADAPTER`    | Platform adapter behavior mismatch or missing fallback              |
| `RC-PARITY`     | Missing route/screen/behavior parity against contract               |
| `RC-SECURITY`   | Secret leakage or policy violation                                  |
| `RC-HUMAN-GATE` | Human-supplied credentials/IDs/approvals missing                    |

---

## 4. Fast Diagnostic Commands

Run from repo root:

```bash
node -v
npm -v
npm ci
npm run typecheck --if-present
npm run lint --if-present
npm test -- --run
npm --workspace apps/native test
npx expo install --check
npx expo-doctor
npx expo export --platform android --output-dir dist-android --clear
node scripts/validate-ota-config.js
npm run build
node scripts/check-bundle-sizes.js
node scripts/check-performance-budgets.js
```

Report files to inspect:

- `reports/input-validation.report.json`
- `reports/compatibility.report.json`
- `reports/repo-check.report.json`
- `reports/generation.report.json`

---

## 5. Failure Catalog by Gate

### `RG-001` Workspace Install (`npm ci`)

Common signatures:

- lockfile mismatch / dependency resolution failure
- network/transient registry error
- peer dependency conflict

Likely causes:

- `RC-DEP`, `RC-ENV`

Immediate recovery:

1. Retry once for transient network failure.
2. Confirm Node version matches compatibility policy.
3. Confirm lockfile exists and is not stale against `package.json`.
4. Re-run `npm ci`.

Prevention:

- Keep single lockfile.
- Avoid mixing package managers.
- Pin versions for high-risk toolchain components.

---

### `RG-002` Type Check (`npm run typecheck --if-present`)

Common signatures:

- TS path alias resolution failures
- contract/interface drift across packages
- unsupported API type signatures after dependency changes

Likely causes:

- `RC-BUILD`, `RC-DEP`, `RC-ADAPTER`

Immediate recovery:

1. Verify `@mova/*` path mappings in web/native tsconfig.
2. Check shared interface changes in `packages/core`.
3. Resolve broken imports or incompatible type updates.

Prevention:

- Keep interface changes backward-compatible.
- Add adapter contract tests before widening types.

---

### `RG-003` Lint (`npm run lint --if-present`)

Common signatures:

- rule violations after template merge
- unsupported syntax/config mismatch

Likely causes:

- `RC-BUILD`

Immediate recovery:

1. Run lint autofix where safe.
2. Resolve remaining rule violations manually.

Prevention:

- Generate code with lint-safe templates.
- Reject placeholder lint scripts (echo/no-op) during scaffold validation.

---

### `RG-004` Web Unit Tests (`npm test -- --run`)

Common signatures:

- failing feature behavior tests
- test runner dependency/ESM resolution issues (example: `ERR_REQUIRE_ESM`)

Likely causes:

- `RC-BUILD`, `RC-DEP`

Immediate recovery:

1. Identify first failing suite and assertion.
2. If resolver/ESM issue, align dependency versions and test runner config.
3. Re-run targeted test, then full test suite.

Prevention:

- Pin test runner and plugin versions.
- Keep compatibility notes up to date when library APIs drift.

---

### `RG-005` Native Tests (`npm --workspace apps/native test`)

Common signatures:

- missing native mocks
- adapter initialization crash in test environment

Likely causes:

- `RC-ADAPTER`, `RC-BUILD`

Immediate recovery:

1. Ensure required RN/Jest mocks are present in setup.
2. Confirm adapter code handles missing native runtime services.

Prevention:

- Maintain stable native test setup with SDK mocks.
- Test fallback mode explicitly.

---

### `RG-006` Content Validation (`npm run validate-content --if-present`)

Common signatures:

- prebuild script failures
- missing/invalid content payload fields
- strict-mode missing entry reports

Likely causes:

- `RC-CONTRACT`, `RC-BUILD`

Immediate recovery:

1. Inspect content generation errors and missing-entry reports.
2. Fix malformed/missing content inputs.
3. Re-run validation in strict mode.

Prevention:

- Keep content schema validation in pipeline.
- Treat missing-content warnings early, not at release time.

---

### `RG-007` OTA Config (`node scripts/validate-ota-config.js`)

Known signatures from current script:

- `apps/native/app.config.ts not found`
- `Missing: updates, runtimeVersion, newArchEnabled, jsEngine`

Likely causes:

- `RC-CONTRACT`, `RC-BUILD`

Immediate recovery:

1. Ensure `apps/native/app.config.ts` exists.
2. Add required OTA/runtime fields.
3. Re-run OTA validation.

Prevention:

- Keep app config template contract-locked.

---

### `RG-008` Web Build (`npm run build`)

Common signatures:

- compile errors
- unresolved imports
- runtime config requirements missing at build time

Likely causes:

- `RC-BUILD`, `RC-ENV`

Immediate recovery:

1. Fix first compile error.
2. Verify required build env vars are set.
3. Re-run build.

Prevention:

- Keep CI dummy env contract and local `.env.example` aligned.

---

### `RG-009` Bundle Budget (`node scripts/check-bundle-sizes.js`)

Common signatures:

- web static/server bundle exceeds budget
- Android build outputs exceed budget
- `.next` missing (script may skip in some contexts)

Likely causes:

- `RC-BUILD`, `RC-DEP`

Immediate recovery:

1. Confirm build artifacts exist.
2. Investigate largest bundles/dependencies.
3. Reduce payload size or adjust documented budgets with rationale.

Prevention:

- Track bundle trends and enforce regressions in CI.

---

### `RG-010` Performance Budget (`node scripts/check-performance-budgets.js`)

Common signatures:

- budget file or metrics file missing (skip)
- metric exceeds budget

Likely causes:

- `RC-ENV`, `RC-BUILD`

Immediate recovery:

1. If metrics absent, document skip reason.
2. If over budget, optimize startup/bundle/resource usage.

Prevention:

- Capture and update performance metrics regularly.

---

### `RG-011` Parity Contract (`node scripts/check-parity-contract.js`)

Common signatures:

- missing P0 route on native
- P0 parity dimension fail
- P1 threshold not met

Likely causes:

- `RC-PARITY`, `RC-ADAPTER`

Immediate recovery:

1. Add missing P0 route/screen wiring.
2. Fix behavior mismatch for failing parity dimensions.
3. Document allowed divergence if applicable.

Prevention:

- Keep parity matrix updated with route-level evidence.
- Add parity checks before release candidate generation.

---

### `RG-012` Output Contract (`node scripts/check-output-contract.js`)

Common signatures:

- missing required file/folder
- missing required scripts in root `package.json`
- missing generated reports/planning artifacts

Likely causes:

- `RC-CONTRACT`, `RC-BUILD`

Immediate recovery:

1. Regenerate missing artifacts.
2. Validate output tree against output contract list.
3. Re-run output-contract check.

Prevention:

- Keep scaffold templates aligned with output contract revisions.

---

### `RG-013` Secret Scan (`node scripts/scan-secrets.js`)

Common signatures:

- private key / token-like string detected
- credentials accidentally written into output

Likely causes:

- `RC-SECURITY`

Immediate recovery:

1. Remove or redact secrets from tracked files.
2. Replace with placeholders in `.env.example`.
3. Rotate exposed credentials if leak was real.
4. Re-run secret scan.

Prevention:

- Never inject secret values into generator inputs/outputs.
- Add denylist + allowlist tuning for false positives.

---

### `RG-014` Native Doctor (`npm --workspace apps/native run doctor`)

Common signatures:

- dependency mismatch warnings
- duplicate native module version findings
- `.expo`/`.expo-shared` ignore warnings

Likely causes:

- `RC-DEP`, `RC-BUILD`

Immediate recovery:

1. Run `npx expo install --check` and align package versions.
2. Ensure `.expo/` and `.expo-shared/` are ignored at root and `apps/native`.
3. If duplicates persist, clear `node_modules` + lockfile and reinstall from root.

Prevention:

- Add `expo-doctor` as blocker gate in `repo:check`.
- Keep Expo SDK patch line and companion packages synchronized.

---

### `RG-015` Native Export Smoke (`npm --workspace apps/native run export:android`)

Common signatures:

- `Unable to resolve module ../../App from ... expo/AppEntry.js`
- Metro resolver mismatch after custom config changes
- workspace package import resolution errors during bundle

Likely causes:

- `RC-BUILD`, `RC-DEP`

Immediate recovery:

1. Ensure `apps/native/package.json` `main` points to `index.js`.
2. Ensure `apps/native/index.js` registers the app with `registerRootComponent`.
3. Revert Metro to Expo defaults and apply only additive workspace `watchFolders`.
4. Re-run export smoke, then full `repo:check`.

Prevention:

- Ban `expo/AppEntry` for monorepo-native output.
- Require native export smoke pass before marking run `pass`.

---

## 6. Compatibility Failure Playbooks

### 6.1 Blocked Combination Requested

Signature:

- blocked compatibility in `reports/compatibility.report.json`

Recovery:

1. Reject blocked combination.
2. Apply recommended fallback from compatibility matrix.
3. Re-run compatibility phase.

### 6.2 Node Version Incompatible

Known example:

- RN 0.83.2 requires Node `>=20.19.4`.

Recovery:

1. Upgrade Node to compliant version.
2. Re-run install + gates.

### 6.3 Preview Dependency Drift (Expo 55 preview)

Signature:

- unexpected install/build/runtime break after dependency refresh

Recovery:

1. Pin exact preview version.
2. Run `npx expo install --check` and align related Expo packages.
3. Re-run install/typecheck/build.
4. If unresolved, rollback to last known good lockfile state.

---

## 7. Adapter Failure Playbooks

### 7.1 Firebase Native Config Missing

Known signature:

- warning indicating Firebase native config missing; auth/sync disabled

Recovery:

1. Treat as expected degraded mode if run target allows partial.
2. Mark unresolved human gate for Firebase config files and bundle IDs.
3. Ensure fallback repositories/local mode are active and non-crashing.

### 7.2 Progress Sync Fails but Local Works

Likely cause:

- remote provider unavailable or auth/config mismatch

Recovery:

1. Preserve local state.
2. Queue/defer remote sync.
3. Surface non-blocking sync status to user/log.

### 7.3 Storage Migration Regression

Signature:

- legacy data not available after upgrade path

Recovery:

1. Verify canonical key checks + legacy key probes + write-through migration path.
2. Add regression test for migrated key path.

---

## 8. Human-Gate Blockers (`RC-HUMAN-GATE`)

Typical blockers:

- missing store credentials
- missing Firebase native app registrations
- missing App Check/provider configuration
- missing bundle/package IDs
- missing IAP keys/API credentials

Recovery:

1. Mark run status `partial` unless blocker gate requires `fail`.
2. Record unresolved dependency in `generation.summary.md`.
3. Link to corresponding checklist item in human-gates docs.

Rule:

- Never fake completion for human-supplied secrets/credentials.

---

## 9. Failure Record Template

Use this template in run artifacts when a failure occurs:

```markdown
## Failure Record

- Timestamp:
- Run ID:
- Phase:
- Gate ID:
- Severity:
- Error Signature:
- Root Cause Class:
- Immediate Fix Applied:
- Retry Count:
- Result After Fix:
- Prevention Action:
```

---

## 10. Recovery Exit Criteria

A failure is considered recovered only when:

1. The specific failed gate passes.
2. Full `repo:check` is re-run.
3. No new blocker failures are introduced.
4. Report artifacts reflect final state accurately.

---

## 11. Escalation Rules

Escalate to manual intervention when:

- same blocker failure repeats after max retries
- security leak is detected
- contract ambiguity prevents deterministic resolution
- toolchain drift introduces incompatible runtime state

Escalation output must include:

- exact failed gate(s)
- attempted fixes
- remaining blockers
- required human decisions

---

## 12. Preventive Maintenance Cadence

After any significant failure:

1. Add/update failure signature in this playbook.
2. Update compatibility matrix if version/toolchain-related.
3. Update gates or scripts if detection was weak.
4. Add/adjust automated test coverage for recurrence prevention.

---

## 13. Changelog

### 2026-02-17

- Initial failure playbook created.
- Added gate-specific diagnosis/recovery paths (`RG-001` to `RG-013`), compatibility playbooks, adapter playbooks, and escalation workflow.

### 2026-02-18

- Added `RG-014` and `RG-015` failure playbooks for Expo doctor and native export smoke failures.
- Added explicit recovery path for monorepo entrypoint resolution errors (`expo/AppEntry` mismatch).
