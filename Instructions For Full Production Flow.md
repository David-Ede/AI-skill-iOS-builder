# Full Production Flow

Use this runbook from planning to TestFlight for a new app generated with this skill.

## 1. Prerequisites

Verify local tooling:

```powershell
node -v
npm -v
npx --version
python --version
git --version
```

Required accounts:

1. GitHub repository access
2. Expo account (EAS)
3. Apple Developer Program membership
4. App Store Connect access with app-management permissions

## 2. Create the Product Contract (PRD)

From your workspace root:

```powershell
Copy-Item .\AI-skill-iOS-builder\Prd Template.md .\PRD.md
```

Then complete `PRD.md`:

1. Fill all required fields.
2. Keep requirement IDs stable (`FR-*`, `NFR-*`).
3. Replace template placeholders.
4. Put unknown values as `UNKNOWN` and list them in open questions.

If required fields are missing, placeholder values remain, or unsupported modules are enabled, the workflow must stop with `BLOCKED_INPUT`.

## 3. Choose Module Flags from PRD

Derive script flags from PRD Section 3 (module table):

| PRD Module | Script Flag |
| --- | --- |
| `MOD-AUTH` | `-WithAuth` |
| `MOD-ONBOARD` | `-WithUiFoundation` |
| `MOD-PROFILE` | `-WithProfile` |
| `MOD-MSG` | `-WithPush` |
| `MOD-OFFLINE` | `-WithDataLayer` |
| `MOD-ANALYTICS` | `-WithAnalytics` |
| `MOD-LOCALE` | `-WithLocalization` |
| `MOD-ACCESS` | `-WithAccessibilityChecks` |
| `MOD-COMPLY` | `-WithPrivacyChecklist` |

Unsupported modules for scaffold phase (must remain disabled):

- `MOD-CONTENT`
- `MOD-TRANSACT`
- `MOD-SOCIAL`
- `MOD-ADMIN`
- `MOD-INTEG`
- `MOD-SEARCH`
- `MOD-MEDIA`

## 4. Run Scaffold

From repo root:

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

Remove flags for modules that are not enabled in your PRD.

## 5. Validate and Configure CI/EAS

```powershell
py .\scripts\validate_expo_ios_project.py --project-dir .\<APP_NAME> --report-path .\<APP_NAME>\reports\validator.pre-ci.json
.\scripts\setup_ci_eas.ps1 -ProjectDir .\<APP_NAME> -RepoProvider github -ReleaseBranch <RELEASE_BRANCH>
py .\scripts\validate_expo_ios_project.py --project-dir .\<APP_NAME> --report-path .\<APP_NAME>\reports\validator.post-ci.json
```

## 6. Run Quality Gates

```powershell
cd .\<APP_NAME>
npm run lint
npm run typecheck
npm run test
cd ..
```

## 7. Commit and Push

```powershell
git add -A
git commit -m "feat: scaffold/update <APP_NAME>"
git push origin <RELEASE_BRANCH>
```

## 8. Configure EAS Project

From app directory:

```powershell
cd .\<APP_NAME>
npx eas-cli login
npx eas-cli whoami
npx eas-cli init --force
```

Confirm app identity in app config:

1. `expo.name` matches product name
2. `expo.slug` matches app slug
3. `ios.bundleIdentifier` matches `<BUNDLE_ID>`
4. `ios.config.usesNonExemptEncryption` is set explicitly

## 9. Fill Human Release Inputs

Open generated file:

```text
<APP_NAME>/release/human-inputs.md
```

Fill all required `KEY = value` entries before release. The validator checks this file when deployment layer is enabled.

## 10. App Store Connect Setup (Manual)

In App Store Connect:

1. Accept latest Apple agreements.
2. Create app record with exact bundle ID match.
3. Confirm role permissions.
4. Create App Store Connect API key (recommended for automation).

## 11. Configure iOS Credentials (Interactive)

```powershell
cd .\<APP_NAME>
npx eas-cli credentials:configure-build --platform ios --profile production
```

During prompts:

1. Let EAS manage credentials.
2. Sign in to Apple.
3. Create or reuse distribution certificate and provisioning profile.

## 12. Build and Submit

Build:

```powershell
npx eas-cli build --platform ios --profile production
```

Submit:

```powershell
npx eas-cli submit --platform ios --profile production --latest
```

## 13. Finish TestFlight Setup

In App Store Connect > TestFlight:

1. Wait for processing.
2. Add internal testing group/testers.
3. For external testers, complete Beta App Information and Beta App Review.

## 14. Prepare App Store Listing

Before App Review submission, complete required listing metadata:

1. Screenshots
2. Description
3. Keywords
4. Support URL
5. Privacy Policy URL
6. Age rating
7. App Privacy questionnaire

## 15. Submit for App Review (When Ready)

1. Select build in App Store Connect.
2. Complete export compliance questions.
3. Add review notes (include demo credentials if login is required).
4. Choose release strategy (manual or automatic).
5. Submit for review.

## 16. Post-Release Monitoring

1. Monitor crashes and analytics.
2. Triage user feedback and tester reports.
3. Prepare patch release if required.

## 17. CI Secrets

Configure repository secrets (names only):

1. `EXPO_TOKEN`
2. `ASC_API_KEY_ID`
3. `ASC_API_KEY_ISSUER_ID`
4. `ASC_API_KEY_P8` (or equivalent secure key strategy)

## 18. Final Acceptance Checklist

1. PRD is complete and committed.
2. Scaffold + validator + quality gates pass.
3. App config identity matches App Store Connect.
4. EAS project is initialized and credentials configured.
5. Human release inputs are complete.
6. Production build is complete.
7. Build is submitted to TestFlight.
