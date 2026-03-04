# Human Build Checklist

Use this as a quick solo-developer checklist.

## 1. Before Scaffold

1. `PRD.md` exists and is based on `Prd Template.md`.
2. Required PRD fields are filled (or explicitly `UNKNOWN` with open question).
3. `AppName`, `BundleId`, `OutputDir`, and `ReleaseBranch` are chosen.
4. Tooling works: `node`, `npm`, `npx`, `py`, `git`.

## 2. Baseline Generation

1. Run `scripts/scaffold_expo_ios_app.ps1`.
2. Run `py scripts/bootstrap_prd_implementation.py --project-dir <app> --prd-path <PRD.md>`.
3. Confirm `<app>/reports/prd-implementation.json` exists.

## 3. Feature Implementation

1. Implement all P0 requirements from PRD.
2. Replace starter/placeholder content in `app/`, `src/`, and `__tests__/`.
3. Add feature-specific tests.
4. Update `reports/prd-implementation.json` with `status`, `code[]`, and `tests[]`.

## 4. Validate and CI

1. Run validator pre-CI:
   - `py scripts/validate_expo_ios_project.py --project-dir <app> --prd-path <PRD.md> --report-path <app>/reports/validator.pre-ci.json`
2. Run `scripts/setup_ci_eas.ps1`.
3. Run validator post-CI:
   - `py scripts/validate_expo_ios_project.py --project-dir <app> --prd-path <PRD.md> --report-path <app>/reports/validator.post-ci.json`
4. In app folder run:
   - `npm run lint`
   - `npm run typecheck`
   - `npm run test`

## 5. Release Setup

1. Fill `<app>/release/human-inputs.md`.
2. Confirm App Store Connect app exists and bundle ID matches app config exactly.
3. Configure iOS credentials with `npx eas-cli credentials:configure-build --platform ios --profile production`.
4. Add required GitHub secrets (`EXPO_TOKEN`, App Store Connect key fields).

## 6. Build and Submit

1. Run `npx eas-cli build --platform ios --profile production`.
2. Run `npx eas-cli submit --platform ios --profile production --latest`.
3. Wait for TestFlight processing.
4. Add testers in App Store Connect.

## 7. Done Means

1. Validator has no blocker failures.
2. No placeholder findings remain.
3. P0 requirements are mapped with implementation/test evidence.
4. `lint`, `typecheck`, and `test` pass.
5. TestFlight build is available to testers.
