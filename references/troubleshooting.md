# Troubleshooting

## Root-Cause Classes
- `RC-CONTRACT`: missing or invalid required config.
- `RC-ENV`: toolchain/runtime mismatch, missing env setup.
- `RC-DEP`: dependency install or resolution failure.
- `RC-BUILD`: lint/typecheck/test/build failures.
- `RC-MODULE`: optional module contract not satisfied.
- `RC-SECURITY`: secret leak or policy violation.
- `RC-HUMAN-GATE`: missing credentials, approvals, or account provisioning.

## create-expo-app Fails
Symptoms:
- Command exits non-zero during scaffold.

Actions:
- Confirm `node`, `npm`, and `npx` are in PATH.
- Retry on a clean directory with network access.
- Run `npx create-expo-app@latest --help` to verify package resolution.

## Lint/Typecheck Fails on Fresh Scaffold
Symptoms:
- Local quality gates fail before feature edits.

Actions:
- Confirm lint/test dependencies were installed.
- Confirm `eslint.config.js` and `jest.config.js` exist.
- Confirm tabs/UI templates were applied consistently.

## Module Contract Failures
Symptoms:
- Validator reports missing files for enabled flags.

Actions:
- Inspect `skill.modules.json` for enabled module set.
- Re-run scaffold with the same flags in a clean directory.
- Verify templates exist under `assets/templates/feature-modules/<module>`.

## Missing expo-router Behavior
Symptoms:
- App does not resolve routes.

Actions:
- Check `package.json.main` equals `expo-router/entry`.
- Check Expo config plugin list contains `expo-router`.
- Re-run validator script and patch indicated failures.

## EAS Build Credential Errors
Symptoms:
- Build fails during signing or credential step.

Actions:
- Run `npx eas credentials` and verify iOS credentials.
- Confirm Apple roles and team access.
- Confirm bundle identifier matches App Store Connect app.

## EAS Submit Failures
Symptoms:
- Submit job fails to upload to TestFlight.

Actions:
- Verify App Store Connect app exists for bundle identifier.
- Verify app-specific password or API key configuration.
- Retry submit with explicit `--latest` build.

## CI Workflow Cannot Build
Symptoms:
- GitHub Action fails before build or on auth.

Actions:
- Confirm repository secret `EXPO_TOKEN` exists.
- Confirm Node and npm install step succeed.
- Confirm quality scripts exist and pass locally.

## Secret or Credential Leakage
Symptoms:
- Secret-like values found in tracked files or CI logs.

Actions:
- Remove leaked values and replace with placeholders.
- Rotate leaked credentials if exposure is real.
- Re-run validation and any secret scan checks before proceeding.

## Failure Record Template
Use this in final status reporting when recovery is needed:

```markdown
## Failure Record
- Phase:
- Gate ID:
- Severity:
- Error signature:
- Root-cause class:
- Fix applied:
- Retry count:
- Current result:
- Next action:
```

## Escalation Rules
Escalate when:
- Same blocker failure repeats after allowed retries.
- Security leak is detected.
- Required human credentials/approvals are missing for release steps.

Escalation report must include:
- Failed gate(s)
- Attempted fixes
- Remaining blockers
- Required human decisions
