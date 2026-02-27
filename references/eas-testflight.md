# EAS and TestFlight

## Prerequisites
- Expo account and `eas-cli` access.
- Apple Developer account with proper app permissions.
- Repository secret `EXPO_TOKEN` for CI automation.
- App Store Connect app record for the configured bundle identifier.

## Human Gate Dependencies
Mark unresolved dependencies instead of claiming full completion:
- Apple developer membership and App Store Connect access.
- Bundle identifier reserved and mapped to the correct App Store app.
- Signing credentials for iOS distribution.
- CI secret provisioning (`EXPO_TOKEN` and any submit credentials).

If these are missing, return overall `partial` with explicit missing items and owners.

## Local Login and Project Setup
```powershell
npx expo login
npx eas login
npx eas build:configure
```

## Build Commands
Preview (internal distribution):
```powershell
npx eas build --platform ios --profile preview
```

Production:
```powershell
npx eas build --platform ios --profile production
```

## Submit to TestFlight
```powershell
npx eas submit --platform ios --profile production --latest
```

## OTA Updates
Use OTA only for JS-safe changes:
```powershell
npx eas update --branch production --message "chore: OTA update"
```

## Release Checklist
- Confirm validator passes (`infraStatus=pass`).
- Confirm `ios.bundleIdentifier` matches App Store Connect app.
- Confirm build profile used matches target environment.
- Confirm TestFlight processing completes before tester notification.
- Confirm unresolved human dependencies list is empty for full `pass`.
