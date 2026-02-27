# Testing and Quality

## Gate Policy
- Default mode: collect all gate results before final status.
- Gate statuses: `pass`, `fail`, `skipped`.
- Blocking classes:
  - `Blocker`: any failure returns overall `fail`.
  - `Conditional`: failure can return `partial` when explicitly waived.
  - `Informational`: never blocks but must be reported.

## Canonical Gate Set
Run in this order:

| Gate ID | Name | Command | Blocking |
| --- | --- | --- | --- |
| `QG-001` | Lint | `npm run lint` | Blocker |
| `QG-002` | Typecheck | `npm run typecheck` | Blocker |
| `QG-003` | Test (Smoke) | `npm run test` | Blocker |
| `QG-004` | Contract Validate | `py scripts/validate_expo_ios_project.py --project-dir <dir>` | Blocker |
| `QG-005` | EAS Build Preview | `npx eas build --platform ios --profile preview` | Conditional |
| `QG-006` | EAS Submit Production | `npx eas submit --platform ios --profile production --latest` | Conditional |

## Baseline Local Checks
Run these before build submit:
```powershell
npm run lint
npm run typecheck
npm run test
```

## Gate Expectations
- `lint`: no blocking lint violations.
- `typecheck`: zero TypeScript errors.
- `test`: must run non-placeholder smoke tests.

## Smoke Test Minimum Contract
- App shell route renders without crash.
- Secondary route module compiles and renders.
- Data-layer client path covers retry and cache behavior when `WithDataLayer` is enabled.

## Module Test Expectations
- `WithAuth`: include `__tests__/auth-oauth.test.ts` for provider slot baseline.
- `WithPush`: include `__tests__/notification-deeplink.test.ts` for payload parsing baseline.
- `WithDataLayer`: include `__tests__/async-resource.test.ts` with retry/cache assertions.

## CI Expectations
- Run the same three gates in CI before EAS build.
- Fail fast on any gate failure.
- Keep CI workflow deterministic by pinning Node version and using lockfile install.
- Keep Node runtime aligned with current Expo support policy (minimum Node 20, preferred Node 22 in CI).
- Use guarded submit behavior (manual or explicit flag) instead of unconditional auto-submit.

## Validator Report Contract
If `--report-path` is provided to the validator, expect:
- `schemaVersion`
- `status`
- `infraStatus`
- `featureStatus`
- `startedAt`
- `finishedAt`
- `projectDir`
- `checks[]`
- `moduleChecks[]`
- `failedChecks[]`
- `warnings[]`
