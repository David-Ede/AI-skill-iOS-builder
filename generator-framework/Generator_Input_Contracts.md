# Generator Input Contracts

## Purpose

Define the canonical input contracts for a one-session, single-prompt app generation run.
This document specifies:

- Required input files.
- Exact field-level schemas.
- Markdown structure contracts for PRD and feature specs.
- Cross-file consistency rules.
- Validation and rejection behavior.

---

## Scope

- Profile: `rn-spg-v1`
- Effective Date: `2026-02-17`
- Baseline Repo: `mova-next`
- Package Manager Profile: npm workspaces

---

## 1. Contract Hierarchy

Order of precedence:

1. `Generator_Stack_Profile.md`
2. `Generator_Compatibility_Matrix.md`
3. This document (`Generator_Input_Contracts.md`)
4. Run-specific input files (`generator.input.yaml`, PRD, feature specs, prompt)

If two inputs conflict, higher-precedence contracts win.

---

## 2. Required Input Bundle

Minimum files required for generation:

```text
<input-root>/
  generator.input.yaml
  run.prompt.md
  product.config.yaml
  prd/
    Product_PRD.md
  features/
    FS-<feature-slug>.md
  templates/
    exec-plan.template.md
```

Required counts:

- `generator.input.yaml`: exactly 1
- `run.prompt.md`: exactly 1
- `product.config.yaml`: exactly 1
- `prd/Product_PRD.md`: exactly 1
- `features/FS-*.md`: at least 1
- `templates/exec-plan.template.md`: exactly 1

Optional but recommended:

- `human-gates/Generator_Human_Gates.yaml`
- `brand/tokens-source.json` or `brand/theme-notes.md`
- `references/` (source links, market notes, legal notes)

---

## 3. File Format Rules

- Text encoding: UTF-8
- Line endings: LF or CRLF accepted
- Max file size:
  - `run.prompt.md`: 100 KB
  - `Product_PRD.md`: 250 KB
  - each feature spec: 150 KB
- Markdown headings must be unique per section level where contract says "required heading".
- All IDs are case-sensitive.
- Secrets are not allowed in any input file.

---

## 4. `generator.input.yaml` Contract (Run Manifest)

This file defines the single generation run and file paths.

### 4.1 Schema

| Field                  | Type    | Required | Constraints                              |
| ---------------------- | ------- | -------- | ---------------------------------------- |
| `schemaVersion`        | integer | Yes      | Must be `1`                              |
| `runId`                | string  | Yes      | Regex: `^[a-z0-9][a-z0-9-]{2,63}$`       |
| `profileId`            | string  | Yes      | Must be `rn-spg-v1`                      |
| `mode`                 | string  | Yes      | Enum: `new-app`                          |
| `inputRoot`            | string  | Yes      | Relative path; must exist                |
| `promptPath`           | string  | Yes      | Must point to `run.prompt.md`            |
| `productConfigPath`    | string  | Yes      | Must point to `product.config.yaml`      |
| `prdPath`              | string  | Yes      | Must point to `prd/Product_PRD.md`       |
| `featureSpecGlob`      | string  | Yes      | Glob matching `features/FS-*.md`         |
| `execPlanTemplatePath` | string  | Yes      | Must point to template file              |
| `strictMode`           | boolean | Yes      | Must be `true` for production generation |
| `targetOutputDir`      | string  | Yes      | Relative path; must be writable          |
| `notes`                | string  | No       | Free text                                |

### 4.2 Example

```yaml
schemaVersion: 1
runId: mova-kids-a2
profileId: rn-spg-v1
mode: new-app
inputRoot: .
promptPath: run.prompt.md
productConfigPath: product.config.yaml
prdPath: prd/Product_PRD.md
featureSpecGlob: features/FS-*.md
execPlanTemplatePath: templates/exec-plan.template.md
strictMode: true
targetOutputDir: ../generated/mova-kids-a2
notes: 'Pilot build for one-session generator validation.'
```

---

## 5. `run.prompt.md` Contract (Single-Prompt Envelope)

This file is the human idea input. It must be structured for deterministic parsing.

### 5.1 Required Headings

```markdown
# App Idea

## Problem

## Users

## Core Outcome

## Must-Have Features

## Constraints

## Success Signal
```

### 5.2 Rules

- `Must-Have Features` must contain 1 or more numbered items.
- `Constraints` must include any hard platform/business/legal limits.
- Avoid implementation-level package requests that conflict with stack profile.
- If request conflicts with profile, generator keeps profile defaults and records override rejection.

---

## 6. `product.config.yaml` Contract

This is the canonical machine-parseable product configuration.

### 6.1 Schema

| Field                          | Type          | Required | Constraints                                                      |
| ------------------------------ | ------------- | -------- | ---------------------------------------------------------------- |
| `schemaVersion`                | integer       | Yes      | Must be `1`                                                      |
| `profileId`                    | string        | Yes      | Must be `rn-spg-v1`                                              |
| `productName`                  | string        | Yes      | 2-50 chars                                                       |
| `slug`                         | string        | Yes      | Regex: `^[a-z0-9]+(?:-[a-z0-9]+)*$`                              |
| `repoName`                     | string        | Yes      | Regex: `^[a-z0-9][a-z0-9-]{2,63}$`                               |
| `description`                  | string        | Yes      | 10-240 chars                                                     |
| `topology`                     | string        | Yes      | Enum: `apps-web` or `root-web`                                   |
| `ios.bundleIdentifier`         | string        | Yes      | iOS bundle identifier format                                     |
| `android.package`              | string        | Yes      | Regex: `^[a-z][a-z0-9_]*(\\.[a-z][a-z0-9_]*)+$`                  |
| `expo.projectId`               | string        | No       | UUID-like string if present                                      |
| `expo.scheme`                  | string        | Yes      | Regex: `^[a-z][a-z0-9-]{1,30}$`                                  |
| `firebase.projectId`           | string        | Yes      | Non-empty                                                        |
| `firebase.authProviders`       | array[string] | Yes      | Unique set, enum: `apple`, `google`, `email`                     |
| `theme.tokensPath`             | string        | Yes      | Must be a repo-relative path                                     |
| `featureFlags`                 | array[string] | No       | Unique values                                                    |
| `release.channels`             | array[string] | Yes      | Subset of `development`, `preview`, `production`                 |
| `release.runtimeVersionPolicy` | string        | Yes      | Must be `appVersion`                                             |
| `release.otaEnabled`           | boolean       | Yes      | Must be true/false                                               |
| `services.billing.web`         | string        | Yes      | Enum: `stripe`, `none`                                           |
| `services.billing.native`      | string        | Yes      | Enum: `iap`, `none`                                              |
| `quality.requiredChecks`       | array[string] | Yes      | Must include `typecheck`, `build`, `native-test`, `validate-ota` |

### 6.2 Example

```yaml
schemaVersion: 1
profileId: rn-spg-v1
productName: Mova Kids
slug: mova-kids
repoName: mova-kids-app
description: 'Ukrainian learning app for families with short daily lessons.'
topology: root-web

ios:
  bundleIdentifier: com.mova.kids

android:
  package: com.mova.kids

expo:
  projectId: '11111111-2222-3333-4444-555555555555'
  scheme: mova-kids

firebase:
  projectId: mova-kids-prod
  authProviders: [apple, google, email]

theme:
  tokensPath: packages/tokens/src/index.ts

featureFlags:
  - onboarding_v2
  - daily_streaks

release:
  channels: [development, preview, production]
  runtimeVersionPolicy: appVersion
  otaEnabled: true

services:
  billing:
    web: stripe
    native: iap

quality:
  requiredChecks:
    - typecheck
    - lint
    - test
    - native-test
    - validate-ota
    - build
```

---

## 7. PRD Contract (`prd/Product_PRD.md`)

The PRD defines product intent and priorities.

### 7.1 Required Headings

```markdown
# Product PRD

## Summary

## Problem

## Target Users

## Goals

## Non-Goals

## Features (Prioritized)

## Success Metrics

## Constraints

## Dependencies

## Release Scope

## Acceptance Criteria
```

### 7.2 Required ID Formats

| Item          | Format   | Example  |
| ------------- | -------- | -------- |
| Feature ID    | `F-###`  | `F-001`  |
| Metric ID     | `M-###`  | `M-001`  |
| Acceptance ID | `AC-###` | `AC-001` |

### 7.3 Rules

- `Features (Prioritized)` must list P0/P1/P2 for each feature ID.
- Every P0 feature must map to one feature spec file in `features/`.
- `Constraints` must include any legal, compliance, or platform blockers.

---

## 8. Feature Spec Contract (`features/FS-*.md`)

Each feature file defines implementation-ready requirements.

### 8.1 Filename Rule

- Pattern: `FS-<feature-slug>.md`
- `<feature-slug>` regex: `^[a-z0-9]+(?:-[a-z0-9]+)*$`

### 8.2 Required Headings

```markdown
# Feature

## Metadata

## Goal

## User Flows

## Routes

## Data Contracts

## Permissions

## Analytics

## Acceptance Criteria

## Out of Scope
```

### 8.3 Required Metadata Keys

In `## Metadata`, these keys are required:

- `Feature ID:` (`F-###`)
- `Priority:` (`P0|P1|P2`)
- `Owner:` (string)
- `Status:` (`draft|approved`)

### 8.4 Section Rules

| Section               | Rule                                                   |
| --------------------- | ------------------------------------------------------ |
| `User Flows`          | Must include at least one `FL-###` flow                |
| `Routes`              | Must include route table or list with explicit path(s) |
| `Data Contracts`      | Must define entities/payloads touched                  |
| `Permissions`         | Must declare `none` or explicit OS/app permissions     |
| `Analytics`           | Must include event names and trigger points            |
| `Acceptance Criteria` | Must include one or more `AC-###` items                |
| `Out of Scope`        | Must include at least one explicit exclusion           |

---

## 9. Execution Plan Template Contract (`templates/exec-plan.template.md`)

This template is compiled with PRD + feature specs into `exec-plan.generated.md`.

Required placeholders:

- `{{RUN_ID}}`
- `{{PROFILE_ID}}`
- `{{PRODUCT_NAME}}`
- `{{SUMMARY}}`
- `{{FEATURE_SCOPE}}`
- `{{REQUIRED_CHECKS}}`
- `{{RISKS}}`
- `{{ACCEPTANCE_TESTS}}`

Rules:

- Missing placeholders are validation errors.
- Extra placeholders are warnings unless used by plan composer config.

---

## 10. Cross-File Consistency Rules

All rules below must pass:

1. `generator.input.yaml.profileId == product.config.yaml.profileId == rn-spg-v1`.
2. PRD feature IDs (P0) must have matching feature spec files.
3. Feature spec `Priority` must match PRD priority for the same feature ID.
4. Any declared permission in specs must be reflected in release/readiness planning.
5. `release.channels` in product config must be compatible with stack profile.
6. `quality.requiredChecks` must include the profile minimum check set.
7. `topology` must be one of allowed profile topologies.

---

## 11. Input Validation Outcomes

| Level     | Meaning                  | Behavior                         |
| --------- | ------------------------ | -------------------------------- |
| `Error`   | Hard contract violation  | Stop generation                  |
| `Warning` | Non-blocking quality gap | Continue, but log in plan/report |
| `Info`    | Advisory note            | Continue                         |

Common error codes:

| Code     | Description                                           |
| -------- | ----------------------------------------------------- |
| `IC-001` | Required input file missing                           |
| `IC-002` | Invalid YAML or malformed markdown heading contract   |
| `IC-003` | Profile mismatch (`profileId`)                        |
| `IC-004` | Product config field invalid                          |
| `IC-005` | P0 feature missing corresponding feature spec         |
| `IC-006` | Unsupported topology or blocked compatibility combo   |
| `IC-007` | Execution plan template missing required placeholders |
| `IC-008` | Secret-like token found in input file                 |

---

## 12. Secrets and Sensitive Data Policy

Inputs must never include:

- API keys
- service account JSON
- private key blocks
- live store credentials

Allowed:

- Secret variable names (for contract definition only)
- Placeholder values like `YOUR_API_KEY_HERE`

---

## 13. Backward Compatibility Policy

- Current schema version: `1`
- Minor field additions allowed if optional.
- Breaking changes require `schemaVersion` increment and migration notes.
- Generator must reject unknown `schemaVersion` values.

---

## 14. Changelog

### 2026-02-17

- Initial input contract created for deterministic single-prompt generation.
- Added strict schemas for run manifest, prompt envelope, product config, PRD, and feature specs.
