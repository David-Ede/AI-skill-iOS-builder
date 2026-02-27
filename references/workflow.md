# Workflow

## Scope
Use this workflow for greenfield Expo Router + TypeScript iOS-first scaffolds with optional feature modules and EAS/TestFlight baseline.

## Contract Hierarchy
Use this precedence when conflicts appear:
1. `SKILL.md`
2. `references/architecture.md`
3. `references/feature-modules.md`
4. `references/testing-quality.md`
5. `references/eas-testflight.md`
6. user request details that do not violate higher contracts

## Required Inputs
- `AppName`: npm-safe project name.
- `BundleId`: reverse-DNS identifier such as `com.company.product`.
- `OutputDir`: parent directory where project folder is created.

## Optional Inputs
- `WithTabs`
- `UseAppConfigTs`
- `ReleaseBranch`
- Feature flags: `WithUiFoundation`, `WithProfile`, `WithAuth`, `WithPush`, `WithDataLayer`, `WithAnalytics`, `WithCrashReporting`, `WithLocalization`, `WithAccessibilityChecks`, `WithPrivacyChecklist`

## Lifecycle Phases
### Phase 0: Preflight
- Verify scope is greenfield.
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
- Capture unresolved human dependencies before calling run complete.

## Retry Policy
- Retry only transient deterministic failures.
- Retry scaffold/install failures at most 2 times.
- Retry linter/autofix-type failures once after fix.
- Do not retry input/contract violations without user-provided corrections.

## Stop Conditions
- Required inputs missing.
- Blocked combination requested.
- Output path not writable.
- Blocker contract check fails after allowed retries.

## Status Mapping
- `pass`: infrastructure and enabled feature checks pass, with no unresolved critical human dependencies.
- `partial`: infrastructure passes but conditional release dependencies or optional module dependencies remain.
- `fail`: blocker contract violation, incompatible request, or unrecoverable gate failure.

## Exit Criteria
- Validation script exits `0` (or report status `pass`).
- Project includes `ios.bundleIdentifier`, Expo Router entrypoint, and EAS profiles.
- GitHub workflow exists at `.github/workflows/eas-ios.yml`.
- Enabled modules satisfy contract checks.
