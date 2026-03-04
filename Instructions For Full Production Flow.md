# Full Production Flow

Use this runbook from planning to TestFlight for a new app generated with this skill.

## 1. Prerequisites

Verify local tooling:

```powershell
node -v
npm -v
npx --version
py --version
git --version
```

Required accounts:
1. GitHub repository access
2. Expo account (EAS)
3. Apple Developer Program membership
4. App Store Connect access with app-management permissions

## 2. Create the Product Contract (PRD)

```powershell
Copy-Item .\AI-skill-iOS-builder\Prd Template.md .\PRD.md
```

Complete `PRD.md`:
1. Fill all required fields.
2. Keep requirement IDs stable (`FR-*`, `NFR-*`).
3. Replace template placeholders.
4. Put unknown values as `UNKNOWN` and list them in open questions.

If required fields are missing, required placeholders remain, or scope conflicts exist, stop with `BLOCKED_INPUT`.

## 3. Derive Scaffold Flags from PRD

From PRD Section 3:
- Use mapped flags for template-backed modules (`MOD-AUTH`, `MOD-ONBOARD`, `MOD-PROFILE`, `MOD-MSG`, `MOD-OFFLINE`, `MOD-ANALYTICS`, `MOD-LOCALE`, `MOD-ACCESS`, `MOD-COMPLY`).
- For modules without direct flags (`MOD-CONTENT`, `MOD-TRANSACT`, `MOD-SOCIAL`, `MOD-ADMIN`, `MOD-INTEG`, `MOD-SEARCH`, `MOD-MEDIA`), plan custom implementation in Phase 5.

## 4. Run Scaffold Baseline

```powershell
.\scripts\scaffold_expo_ios_app.ps1 `
  -AppName <APP_NAME> `
  -BundleId <BUNDLE_ID> `
  -OutputDir <OUTPUT_DIR> `
  -ReleaseBranch <RELEASE_BRANCH> `
  -WithUiFoundation `
  -WithAuth `
  -WithProfile `
  -WithPush `
  -WithDataLayer `
  -WithAnalytics `
  -WithCrashReporting `
  -WithLocalization `
  -WithAccessibilityChecks `
  -WithPrivacyChecklist
```

Remove flags for PRD modules that are not enabled.

## 5. Bootstrap Requirement Mapping

```powershell
py .\scripts\bootstrap_prd_implementation.py --project-dir .\<APP_NAME> --prd-path .\PRD.md
```

This creates `.<APP_NAME>\reports\prd-implementation.json`.

## 6. Implement Product Features

Before CI/release steps:
1. Implement all P0 requirements and critical journeys.
2. Replace scaffold placeholder/starter content in app code.
3. Add feature-specific tests beyond baseline shell tests.
4. Update `reports/prd-implementation.json` with:
   - `status`
   - `code[]`
   - `tests[]`

## 7. Validate and Configure CI/EAS

```powershell
py .\scripts\validate_expo_ios_project.py --project-dir .\<APP_NAME> --prd-path .\PRD.md --report-path .\<APP_NAME>\reports\validator.pre-ci.json
.\scripts\setup_ci_eas.ps1 -ProjectDir .\<APP_NAME> -RepoProvider github -ReleaseBranch <RELEASE_BRANCH>
py .\scripts\validate_expo_ios_project.py --project-dir .\<APP_NAME> --prd-path .\PRD.md --report-path .\<APP_NAME>\reports\validator.post-ci.json
```

Do not continue while validator has blocker failures.

## 8. Run Quality Gates

```powershell
cd .\<APP_NAME>
npm run lint
npm run typecheck
npm run test
cd ..
```

## 9. Commit and Push

```powershell
git add -A
git commit -m "feat: implement <APP_NAME> PRD scope"
git push origin <RELEASE_BRANCH>
```

## 10. Configure EAS Project

```powershell
cd .\<APP_NAME>
npx eas-cli login
npx eas-cli whoami
npx eas-cli init --force
```

Confirm app identity:
1. `expo.name` matches product name
2. `expo.slug` matches app slug
3. `ios.bundleIdentifier` matches `<BUNDLE_ID>`
4. `ios.config.usesNonExemptEncryption` is set explicitly

## 11. Fill Human Release Inputs

Fill `<APP_NAME>/release/human-inputs.md` required `KEY = value` entries.

## 12. App Store Connect Setup (Manual)

1. Accept latest Apple agreements.
2. Create app record with exact bundle ID match.
3. Confirm role permissions.
4. Create App Store Connect API key (recommended for automation).

## 13. Configure iOS Credentials (Interactive)

```powershell
cd .\<APP_NAME>
npx eas-cli credentials:configure-build --platform ios --profile production
```

## 14. Build and Submit

Build:
```powershell
npx eas-cli build --platform ios --profile production
```

Submit:
```powershell
npx eas-cli submit --platform ios --profile production --latest
```

## 15. Finish TestFlight Setup

1. Wait for processing.
2. Add internal testing group/testers.
3. For external testers, complete Beta App Information and Beta App Review.

## 16. CI Secrets

Configure repository secrets:
1. `EXPO_TOKEN`
2. `ASC_API_KEY_ID`
3. `ASC_API_KEY_ISSUER_ID`
4. `ASC_API_KEY_P8`

## 17. Final Acceptance Checklist

1. PRD is complete and committed.
2. `reports/prd-implementation.json` covers all requirements.
3. Validator passes with `--prd-path` and no blocker failures.
4. `lint`, `typecheck`, and `test` pass.
5. Placeholder marker scan has zero findings.
6. Production build is complete.
7. Build is submitted to TestFlight.
