# Generator Output Contract

## Purpose

Define the required outputs of a successful single-prompt generation run.
This contract specifies:

- Required repository structure and files.
- Required generated documents and reports.
- Determinism/idempotence rules.
- Pass/fail criteria for generation completion.

---

## Scope

- Profile: `rn-spg-v1`
- Effective Date: `2026-02-17`
- Baseline Repo Pattern: `mova-next`
- Input Dependency: `Generator_Input_Contracts.md`

---

## 1. Output Root

The generator writes to:

- `targetOutputDir` from `generator.input.yaml`

All required outputs are evaluated relative to that directory.

---

## 2. Required Output Bundle

A successful run must produce:

```text
<targetOutputDir>/
  package.json
  package-lock.json
  turbo.json
  tsconfig.json
  .gitignore
  .npmrc
  README.md

  .github/workflows/
    ci.yml
    content-validation.yml

  apps/native/
    package.json
    .gitignore
    app.config.ts
    eas.json
    metro.config.js
    tsconfig.json
    index.js
    App.tsx

  packages/core/
    package.json
    src/index.ts
  packages/data/
    package.json
    src/index.ts
  packages/tokens/
    package.json
    src/index.ts
  packages/analytics/
    package.json
    src/index.ts
  packages/config/
    package.json

  scripts/
    validate-ota-config.js
    check-bundle-sizes.js
    check-performance-budgets.js

  planning/generated/
    exec-plan.generated.md
    generation.summary.md

  reports/
    generation.report.json
    input-validation.report.json
    compatibility.report.json
    repo-check.report.json
```

---

## 3. Topology-Specific Requirements

`product.config.yaml.topology` controls web placement:

### 3.1 `root-web` topology

Must include:

- `src/`
- `src/pages/`
- `next.config.ts`
- `playwright.config.ts`
- `vitest.config.mts`
- `vitest.setup.tsx`

### 3.2 `apps-web` topology

Must include:

- `apps/web/package.json`
- `apps/web/src/`
- `apps/web/next.config.ts`
- `apps/web/playwright.config.ts`
- `apps/web/vitest.config.mts`

If `apps-web` is selected, root scripts must delegate to `apps/web` where relevant.

---

## 4. Required `package.json` Script Surface

Root `package.json` must define, at minimum:

- `dev`
- `dev:native`
- `prebuild`
- `build`
- `lint`
- `typecheck`
- `test`
- `test:e2e`
- `validate:ota`
- `check:bundles`
- `check:perf`
- `check:budgets`
- `repo:check`
- `doctor:native`
- `export:native`

Rules:

- `repo:check` must run all required profile checks in one command.
- Script names must match exactly to preserve tool compatibility.
- `lint` must execute a real linter command (placeholder echo/no-op commands are invalid).

---

## 5. Required Config Contracts in Output

### 5.1 Native config (`apps/native/app.config.ts`)

Must include:

- `updates`
- `runtimeVersion`
- `jsEngine`
- `newArchEnabled`
- `ios.bundleIdentifier` from `product.config.yaml`
- `android.package` from `product.config.yaml`

### 5.2 EAS profiles (`apps/native/eas.json`)

Must include build profiles:

- `development`
- `preview`
- `production`

### 5.3 Metro workspace config (`apps/native/metro.config.js`)

Must include workspace-aware resolution while preserving Expo defaults:

- start from `getDefaultConfig(projectRoot)`
- additive `watchFolders` merge (do not replace existing defaults)
- do not override `disableHierarchicalLookup` unless contract explicitly requires it

### 5.4 Native entrypoint contract

`apps/native/package.json` and app bootstrap must satisfy:

- `main` must resolve to `apps/native/index.js` (workspace-safe)
- `apps/native/index.js` must call `registerRootComponent(App)`
- must not rely on `expo/AppEntry` in monorepo output mode

### 5.5 TypeScript path aliases

Must resolve `@mova/*` for both web and native.

### 5.6 Expo local-state ignore policy

Must include ignore rules for Expo local state:

- root `.gitignore` must include `.expo/` and `.expo-shared/`
- `apps/native/.gitignore` must include `.expo/` and `.expo-shared/`

---

## 6. Shared Package Output Requirements

Each required workspace package must provide:

- `package.json` with stable package name (`@mova/...`)
- export entrypoint (`src/index.ts`)
- type-compatible public surface

Boundary rules:

- `@mova/core` must not import platform SDK packages directly.
- `@mova/data` may depend on `@mova/core`.
- `@mova/tokens` must be platform-agnostic.

---

## 7. Generated Planning Artifacts

### 7.1 `planning/generated/exec-plan.generated.md`

Must include:

- run ID
- selected profile ID
- feature scope summary
- implementation phases
- validation plan
- risks and mitigations
- acceptance tests

### 7.2 `planning/generated/generation.summary.md`

Must include:

- generated topology (`root-web` or `apps-web`)
- key decisions and rejected overrides
- unresolved human-gate dependencies
- final output status (`pass|partial|fail`)

---

## 8. Machine-Readable Report Contracts

### 8.1 `reports/generation.report.json`

Required schema:

| Field            | Type                   | Required |
| ---------------- | ---------------------- | -------- | ------ | --- |
| `schemaVersion`  | integer                | Yes      |
| `runId`          | string                 | Yes      |
| `profileId`      | string                 | Yes      |
| `status`         | string (`pass          | partial  | fail`) | Yes |
| `startedAt`      | string (ISO timestamp) | Yes      |
| `finishedAt`     | string (ISO timestamp) | Yes      |
| `outputDir`      | string                 | Yes      |
| `topology`       | string                 | Yes      |
| `generatedFiles` | integer                | Yes      |
| `warnings`       | array                  | Yes      |
| `errors`         | array                  | Yes      |

### 8.2 `reports/input-validation.report.json`

Required fields:

- `status`
- `errorCount`
- `warningCount`
- `findings[]` with `code`, `severity`, `message`, `path`

### 8.3 `reports/compatibility.report.json`

Required fields:

- `selectedProfile`
- `blockedCombinations[]`
- `riskCombinations[]`
- `resolvedVersions` object
- `status`

### 8.4 `reports/repo-check.report.json`

Required fields:

- `status`
- `checks[]` with `name`, `command`, `result`, `durationMs`
- `failedChecks[]`

---

## 9. Determinism and Idempotence Requirements

For identical input bundle and runtime profile:

- Generated tracked source output must be byte-stable.
- Running generator twice must not create unintended diffs.
- File ordering and key ordering in JSON reports must be stable.

Allowed non-deterministic fields (must be isolated):

- `startedAt`
- `finishedAt`
- `durationMs`

No other generated content may vary between identical runs.

---

## 10. Output Security Requirements

Generated output must not contain:

- plaintext secrets
- service account JSON values
- private key material
- production credentials

Allowed:

- `.env.example` placeholders
- variable names only (no secret values)

---

## 11. Completion Criteria

Generation is `pass` only if:

1. Input validation has zero errors.
2. Compatibility check has zero blocked combinations.
3. Required output bundle exists and is complete.
4. `repo:check` passes.
5. `exec-plan.generated.md` and all required reports are generated.
6. No secret-policy violations found.

Generation is `partial` if:

- source scaffolding is complete, but one or more required checks fail, or
- required human-gate dependencies block full readiness.

Generation is `fail` if:

- required outputs are missing, or
- blocked compatibility combinations exist, or
- input contract errors are present.

---

## 12. Rejection Conditions

Output must be rejected if any of the following are true:

- output topology does not match `product.config.yaml.topology`
- required scripts are missing
- required workflows are missing
- required reports are missing
- app config does not include required OTA/runtime fields
- generated files include secrets

---

## 13. Backward Compatibility

- Current output contract version: `1`
- Breaking output changes require contract version bump and migration notes.
- Generators must stamp report schema versions to support future migrations.

---

## 14. Changelog

### 2026-02-17

- Initial output contract created for deterministic single-prompt generation.
- Added mandatory repository structure, report schemas, determinism rules, and pass/fail criteria.

### 2026-02-18

- Added explicit native entrypoint requirements (`apps/native/index.js`, `main: index.js`) for monorepo outputs.
- Updated Metro contract to require additive default-preserving configuration.
- Added required `doctor:native` and `export:native` script surface.
