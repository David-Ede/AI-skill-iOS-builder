# Workflow

## Scope
Use this workflow for greenfield Expo Router + TypeScript iOS-first scaffolds with optional feature modules and EAS/TestFlight baseline.

## Contract Hierarchy
Use this precedence when conflicts appear:
1. `SKILL.md`
2. completed project PRD based on `PRD_TEMPLATE.md` (product behavior and scope authority)
3. `references/prd-mapping.md`
4. `references/architecture.md`
5. `references/feature-modules.md`
6. `references/testing-quality.md`
7. `references/eas-testflight.md`
8. user request details that do not violate higher contracts

## Required Inputs
- `AppName`: npm-safe project name.
- `BundleId`: reverse-DNS identifier such as `com.company.product`.
- `OutputDir`: parent directory where project folder is created.
- `PrdPath`: path to completed PRD document derived from `PRD_TEMPLATE.md`.

## Optional Inputs
- `WithTabs`
- `UseAppConfigTs`
- `ReleaseBranch`
- `WithDeploymentLayer` (default: `true`)
- Feature flags: `WithUiFoundation`, `WithProfile`, `WithAuth`, `WithPush`, `WithDataLayer`, `WithAnalytics`, `WithCrashReporting`, `WithLocalization`, `WithAccessibilityChecks`, `WithPrivacyChecklist`

## Lifecycle Phases
### Phase 0: Preflight
- Verify scope is greenfield.
- Verify `PrdPath` exists and is readable.
- Validate PRD required sections and required-field placeholders using `references/prd-mapping.md`.
- Derive feature/module flags from PRD `Section 3` module table.
- If PRD has unsupported enabled modules or required gaps, return `BLOCKED_INPUT` and stop.
- Verify `node`, `npm`, `npx` availability.
- Verify output path is writable.
- Verify blocked combinations are not requested.
- Resolve module defaults and compatibility matrix.

### Phase 1: Scaffold
```powershell
./scripts/scaffold_expo_ios_app.ps1 -AppName weather-app -BundleId com.example.weatherapp -OutputDir C:/work -WithUiFoundation -WithAuth
```

### Phase 2: Contract Validation
```powershell
py ./scripts/validate_expo_ios_project.py --project-dir C:/work/weather-app --report-path C:/work/weather-app/reports/repo-check.report.json
```

### Phase 3: CI and EAS Setup
```powershell
./scripts/setup_ci_eas.ps1 -ProjectDir C:/work/weather-app -RepoProvider github -ReleaseBranch main
```

### Phase 4: Quality Gates
```powershell
npm run lint
npm run typecheck
npm run test
```

### Phase 5: Release Readiness
- Continue with `references/eas-testflight.md`.
- Fill `release/human-inputs.md` using `KEY = value` lines (quotes optional).
- Capture unresolved human dependencies before calling run complete.

## Retry Policy
- Retry only transient deterministic failures.
- Retry scaffold/install failures at most 2 times.
- Retry linter/autofix-type failures once after fix.
- Do not retry input/contract violations without user-provided corrections.

## Stop Conditions
- Required inputs missing.
- PRD contract failure (`BLOCKED_INPUT`).
- Blocked combination requested.
- Output path not writable.
- Blocker contract check fails after allowed retries.

## Status Mapping
Before status mapping, if preflight fails PRD input contract, return `BLOCKED_INPUT`.

- `pass`: infrastructure and enabled feature checks pass, with no unresolved critical human dependencies.
- `partial`: infrastructure passes but conditional release dependencies or optional module dependencies remain.
- `fail`: blocker contract violation, incompatible request, or unrecoverable gate failure.

## Exit Criteria
- Validation script exits `0` (or report status `pass`).
- Project includes `ios.bundleIdentifier`, `ios.config.usesNonExemptEncryption`, Expo Router entrypoint, and EAS profiles.
- GitHub workflow exists at `.github/workflows/eas-ios.yml`.
- Enabled modules satisfy contract checks.
- PRD `FR-*` and `NFR-*` requirements are traceably mapped to implementation tasks/tests.
