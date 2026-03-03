# Human Build Checklist

Use this as a quick solo-developer checklist.

## 1. Before You Scaffold

1. `PRD.md` exists and is based on `Prd Template.md`.
2. Required PRD fields are filled (or set to `UNKNOWN` with an open question).
3. Unsupported modules are set to `No`.
4. `AppName`, `BundleId`, `OutputDir`, and `ReleaseBranch` are chosen.
5. Tooling works: `node`, `npm`, `npx`, `python`, `git`.

## 2. Generate and Validate

1. Run `scripts/scaffold_expo_ios_app.ps1`.
2. Run validator pre-CI (`validator.pre-ci.json`).
3. Run `scripts/setup_ci_eas.ps1`.
4. Run validator post-CI (`validator.post-ci.json`).
5. In the app folder run:
   - `npm run lint`
   - `npm run typecheck`
   - `npm run test`

## 3. Release Setup

1. Fill `<APP_NAME>/release/human-inputs.md`.
2. Confirm App Store Connect app exists and bundle ID matches app config exactly.
3. Configure iOS credentials with `npx eas-cli credentials:configure-build --platform ios --profile production`.
4. Add required GitHub secrets (`EXPO_TOKEN`, App Store Connect key fields).

## 4. Build and Submit

1. Run `npx eas-cli build --platform ios --profile production`.
2. Run `npx eas-cli submit --platform ios --profile production --latest`.
3. Wait for TestFlight processing to complete.
4. Add testers in App Store Connect.

## 5. Done Means

1. Validator has no blocker failures.
2. `lint`, `typecheck`, and `test` pass.
3. TestFlight build is available to your testers.
