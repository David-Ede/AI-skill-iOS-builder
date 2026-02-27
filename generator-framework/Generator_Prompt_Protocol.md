# Generator Prompt Protocol

## Purpose

Define the execution protocol for single-prompt app generation.
This document tells the generator exactly how to behave from start to finish:

- What to read and in what order.
- How to resolve conflicts and ambiguity.
- How to generate outputs deterministically.
- When to retry, when to stop, and what to report.

---

## Scope

- Profile: `rn-spg-v1`
- Effective Date: `2026-02-17`
- Applicable Mode: `new-app`
- Input Contract Dependency: `Generator_Input_Contracts.md`
- Output Contract Dependency: `Generator_Output_Contract.md`

---

## 1. Protocol Identity

- Protocol ID: `gpp-v1`
- Run Type: single prompt, single session
- Default Strictness: strict
- Default Determinism: required

---

## 2. Single-Prompt Definition

A single-prompt run means:

1. One user idea prompt (`run.prompt.md`) drives the run.
2. All required structured inputs are loaded once at run start.
3. One continuous generation session produces complete repository output.
4. No manual editing is required between scaffold and validation stages.

---

## 3. Source-of-Truth Read Order

The generator must load and apply context in this exact order:

1. `Generator_Stack_Profile.md`
2. `Generator_Compatibility_Matrix.md`
3. `Generator_Input_Contracts.md`
4. `generator.input.yaml`
5. `product.config.yaml`
6. `prd/Product_PRD.md`
7. `features/FS-*.md`
8. `run.prompt.md`
9. `templates/exec-plan.template.md`

Rule:

- If lower-order input conflicts with higher-order contracts, higher-order contracts win.

---

## 4. Run Lifecycle (Required Phases)

### Phase 0: Bootstrap

- Resolve paths from `generator.input.yaml`.
- Initialize run metadata (`runId`, timestamps, profile, mode).
- Fail immediately if required input files are missing.

### Phase 1: Input Validation

- Validate all input contracts.
- Emit `reports/input-validation.report.json`.
- If any `Error` findings exist, stop with `fail`.

### Phase 2: Compatibility Resolution

- Resolve requested stack vs compatibility matrix.
- Emit `reports/compatibility.report.json`.
- If any blocked combinations are present, stop with `fail`.

### Phase 3: Plan Composition

- Build structured execution plan from PRD + feature specs + template.
- Write `planning/generated/exec-plan.generated.md`.
- Record all inferred decisions and rejected overrides.

### Phase 4: Scaffold Generation

- Generate repository tree and files required by output contract.
- Apply topology rule (`root-web` or `apps-web`).
- Generate config/scripts/workflows/packages with profile-compliant defaults.

### Phase 5: Validation and Repo Checks

- Run required checks (or perform check simulation when explicitly configured).
- Generate `reports/repo-check.report.json`.
- Mark each check as `pass`, `fail`, or `skipped` with reason.

### Phase 6: Finalization and Reporting

- Emit `reports/generation.report.json`.
- Emit `planning/generated/generation.summary.md`.
- Return final status: `pass`, `partial`, or `fail` per output contract.

---

## 5. Prompt Assembly Protocol

The effective prompt context for the generator must include:

1. System behavior constraints.
2. Stack profile constraints.
3. Compatibility constraints.
4. Input contract constraints.
5. Run-specific inputs (prompt, PRD, specs, product config).

Rules:

- Do not treat user prompt text as override for blocked compatibility rules.
- Treat user prompt as product intent, not toolchain authority.
- Convert vague requirements into explicit assumptions and log them.

---

## 6. Decision and Conflict Resolution Rules

When conflicts occur, apply this decision chain:

1. Check whether the request violates `Blocked` compatibility rules.
2. If blocked, reject override and log in summary/report.
3. If not blocked but `Risk`, continue with mitigation notes.
4. If ambiguous and resolvable from context, infer and continue.
5. If ambiguity is not resolvable from context and blocks execution, stop and request clarification.

Priority order:

1. Stack profile
2. Compatibility matrix
3. Input contracts
4. Product config
5. PRD and feature specs
6. Free-form prompt

---

## 7. Retry Protocol

Retries are allowed only for deterministic, transient failures.

| Failure Class                                | Max Retries | Strategy                  |
| -------------------------------------------- | ----------- | ------------------------- |
| File write race / lock                       | 2           | Retry with short backoff  |
| Dependency install transient network failure | 2           | Retry exact same command  |
| Formatting/lint fixable issue                | 1           | Auto-fix then rerun check |
| Input schema error                           | 0           | Stop immediately          |
| Blocked compatibility combo                  | 0           | Stop immediately          |
| Missing required file                        | 0           | Stop immediately          |

Rules:

- Never retry with changed requirements unless user explicitly updates inputs.
- All retries must be logged in `generation.report.json`.

---

## 8. Stop Conditions

The generator must stop immediately when:

- Required input file is missing.
- Input validation reports any `Error`.
- Blocked compatibility combination exists.
- Output root is not writable.
- Required output contract cannot be satisfied in current run.

Stop status mapping:

- Contract/input failure: `fail`
- Compatibility block: `fail`
- Partial generation with unmet checks: `partial`

---

## 9. Human-Decision Policy

Default policy:

- Prefer execution over asking questions.
- Ask for user input only when execution cannot continue without a decision.

Allowed unresolved items in a `partial` result:

- Store credentials
- production secrets
- legal/policy approvals
- app-store account provisioning

All unresolved human dependencies must be listed in `generation.summary.md`.

---

## 10. Determinism Controls

The protocol must enforce deterministic outputs:

- Stable file creation order (sorted path order).
- Stable JSON key order for generated reports.
- Stable section ordering in generated markdown.
- No random IDs unless explicitly required and recorded.
- Any timestamp fields confined to report metadata.

Idempotence rule:

- Running the same run with identical inputs must produce byte-identical tracked source output.

---

## 11. Security and Secret Handling

During generation:

- Reject secret-like values in inputs.
- Never write real secrets into output files.
- Write only placeholders in `.env.example`.
- Redact any detected secret-like value in reports.

If secret leakage is detected:

- mark run `fail`
- include finding in `input-validation.report.json` or `generation.report.json`

---

## 12. Required Run Logs and Reports

The protocol requires these artifacts:

- `reports/input-validation.report.json`
- `reports/compatibility.report.json`
- `reports/repo-check.report.json`
- `reports/generation.report.json`
- `planning/generated/exec-plan.generated.md`
- `planning/generated/generation.summary.md`

`generation.report.json` minimum event sequence:

1. `bootstrap_started`
2. `input_validation_completed`
3. `compatibility_resolved`
4. `plan_generated`
5. `scaffold_completed`
6. `repo_check_completed`
7. `run_completed`

---

## 13. Final Response Protocol

At end of run, generator must return:

1. Final status (`pass|partial|fail`)
2. Short summary of what was generated
3. List of failed/skipped checks
4. List of unresolved human dependencies
5. Paths to generated reports and execution plan

Do not claim success if required checks failed.

---

## 14. Non-Goals (v1)

- Interactive multi-round design sessions during generation.
- Dynamic toolchain switching mid-run.
- Automatic store submission.
- Policy/legal auto-approval logic.

---

## 15. Changelog

### 2026-02-17

- Initial prompt protocol created.
- Added strict lifecycle phases, retry policy, stop conditions, and deterministic execution controls.
