# Testing and Quality

## Gate Policy
- Default mode: collect all gate results before final status.
- Gate statuses: `pass`, `fail`, `skipped`.
- Any `Blocker` failure returns overall `fail`.

## Canonical Gate Set
Run in this order:

| Gate ID | Name | Command | Blocking |
| --- | --- | --- | --- |
| `QG-001` | Lint | `npm run lint` | Blocker |
| `QG-002` | Typecheck | `npm run typecheck` | Blocker |
| `QG-003` | Test | `npm run test` | Blocker |
| `QG-004` | Contract Validate (PRD) | `py scripts/validate_expo_ios_project.py --project-dir <dir> --prd-path <prd>` | Blocker |
| `QG-005` | EAS Build Preview | `npx eas build --platform ios --profile preview` | Conditional |
| `QG-006` | EAS Submit Production | `npx eas submit --platform ios --profile production --latest` | Conditional |

## Gate Expectations
- `lint`: no blocking lint violations.
- `typecheck`: zero TypeScript errors.
- `test`: real tests with assertions, not no-op commands.
- Validator:
  - requires PRD parsing
  - requires `reports/prd-implementation.json`
  - requires complete FR/NFR mapping
  - requires P0 code/test evidence
  - fails on placeholder markers in `app/`, `src/`, or `__tests__/`

## Minimum Test Contract
- App shell route renders without crash.
- Secondary route compiles and renders.
- Module baseline tests exist for enabled template modules.
- Feature-specific tests exist for PRD module requirements.

## CI Expectations
- Run `lint`, `typecheck`, `test`, and PRD-aware validator before EAS build.
- Fail fast on blocker failures.
- Pin Node version and use lockfile install.
- Keep Node runtime aligned with Expo policy (minimum Node 20).
- Use guarded submit behavior (manual/explicit trigger) instead of unconditional submit.

## Validator Report Contract
If `--report-path` is provided, report includes:
- `schemaVersion`
- `status`
- `infraStatus`
- `featureStatus`
- `checks[]`
- `moduleChecks[]`
- `failedChecks[]`
- `prdRequirementIds[]`
- `p0RequirementIds[]`
- `missingRequirementMappings[]`
- `p0ImplementationFailures[]`
- `placeholderFindings[]`
- `unresolvedHumanDependencies[]`
