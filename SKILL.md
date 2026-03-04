---
name: expo-ios-app-builder
description: Use for greenfield iOS-first React Native app delivery with Expo Router, TypeScript, PRD-driven feature implementation, deterministic quality gates, and EAS Build/Submit TestFlight setup. Trigger on requests for a new Expo iOS app where the result must include implemented product features (not scaffold-only placeholders), PRD traceability, and release readiness. Do not use for existing-repo migrations, React Navigation architecture requests, bare React Native workflows, or non-EAS release pipelines.
---

# Expo iOS App Builder

## Purpose
Create new iOS-first Expo applications from PRD to production-ready implementation. Use scaffold templates only as a starting point, then implement the in-scope product features, tests, and PRD traceability before any TestFlight submission.

## Inputs
Required:
- `AppName`
- `BundleId`
- `OutputDir`
- `PrdPath` (completed project PRD based on `Prd Template.md`)

Optional:
- `WithTabs`
- `UseAppConfigTs`
- `ReleaseBranch` (default: `main`)
- `WithUiFoundation`
- `WithProfile`
- `WithAuth`
- `WithPush`
- `WithDataLayer`
- `WithAnalytics`
- `WithCrashReporting`
- `WithLocalization`
- `WithAccessibilityChecks`
- `WithPrivacyChecklist`
- `WithDeploymentLayer` (default: `true`)

Notes:
- Derive scaffold flags from PRD Section 3 using `references/prd-mapping.md`.
- If PRD enables a module without a scaffold template, keep moving and implement it as custom code/tests in the implementation phase.

## Outputs
Required outputs in generated app:
- `<project>/skill.modules.json`
- `<project>/reports/prd-implementation.json`
- Feature code and tests mapped to PRD requirements
- `<project>/release/human-inputs.md` (when `WithDeploymentLayer` is enabled)

Validator must run with PRD:
- `py scripts/validate_expo_ios_project.py --project-dir <project> --prd-path <PrdPath>`

## Safety And Constraints
- Never write real secrets into tracked source files.
- Keep `.env` values as placeholders unless user explicitly handles secure injection.
- Treat PRD as authoritative for scope and behavior.
- If required PRD fields are missing or unresolved placeholders remain, return `BLOCKED_INPUT`.
- If user asks for out-of-scope items, stop and ask for PRD revision/override.
- Never mark status `pass` when source/tests still include placeholder markers.

## Workflow
1. Preflight
- Confirm greenfield scope and writable output path.
- Validate PRD required sections/fields with `references/prd-mapping.md`.
- Derive module flags from PRD Section 3.
- Confirm `node`, `npm`, `npx` availability and Node policy in `references/testing-quality.md`.

2. Scaffold baseline
- Run `scripts/scaffold_expo_ios_app.ps1` with PRD-derived flags.
- Treat output as bootstrap only, not release-ready product behavior.

3. Bootstrap PRD traceability
- Run:
```powershell
py scripts/bootstrap_prd_implementation.py --project-dir <project> --prd-path <PrdPath>
```
- Populate `<project>/reports/prd-implementation.json` while implementing.

4. Implement product scope
- Implement all PRD P0 requirements and in-scope journeys in app code.
- Replace scaffold placeholder copy/components with actual product behavior.
- Add feature-specific tests (not only shell/module baseline tests).
- Keep `reports/prd-implementation.json` updated with per-requirement code/test evidence.

5. Validate contracts
- Run validator with PRD contract:
```powershell
py scripts/validate_expo_ios_project.py --project-dir <project> --prd-path <PrdPath> --report-path <project>/reports/validator.pre-ci.json
```
- Fix all blocker failures before CI/EAS setup.

6. CI and release setup
- Run `scripts/setup_ci_eas.ps1`.
- Re-run validator:
```powershell
py scripts/validate_expo_ios_project.py --project-dir <project> --prd-path <PrdPath> --report-path <project>/reports/validator.post-ci.json
```

7. Quality gates and submit
- Run `npm run lint`, `npm run typecheck`, `npm run test`.
- Continue to EAS build/submit only after validator and gates pass.

## Definition Of Done
- Scaffold succeeded and app contracts are valid.
- Validator passes with `--prd-path` and zero blocker failures.
- `reports/prd-implementation.json` maps all PRD requirements.
- Every P0 requirement is marked implemented with existing code and test evidence.
- Placeholder marker scan passes in `app/`, `src/`, and `__tests__/`.
- Feature-specific tests exist beyond baseline shell/module smoke checks.
- `lint`, `typecheck`, `test` pass.
- CI workflow and EAS profiles are present.

## Scripts
- `scripts/scaffold_expo_ios_app.ps1`: create baseline app + selected modules.
- `scripts/bootstrap_prd_implementation.py`: generate/refresh PRD mapping report.
- `scripts/validate_expo_ios_project.py`: enforce infra + PRD implementation contracts.
- `scripts/setup_ci_eas.ps1`: install CI workflow and EAS defaults.

## References
- `Prd Template.md`
- `references/prd-mapping.md`
- `references/workflow.md`
- `references/feature-modules.md`
- `references/testing-quality.md`
- `references/eas-testflight.md`
- `references/troubleshooting.md`

## Assets
- `assets/templates/app.config.ts.template`
- `assets/templates/eas.json.template`
- `assets/templates/github-actions-eas.yml`
- `assets/templates/feature-modules/*`
- `assets/templates/release/*`
