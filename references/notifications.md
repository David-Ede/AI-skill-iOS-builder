# Notifications

## Scope
This module scaffolds client-side push notification setup patterns with deep-link payload handling.

## Required Components
- Permission request flow.
- Push token registration helper and backend payload contract placeholder.
- Notification provider wrapper.
- Deep-link payload parser (`src/notifications/notificationDeepLink.ts`).
- Expo config plugin entry for `expo-notifications`.

## Lifecycle Guidance
- Request permissions only at a meaningful user action point.
- Handle denied permission state with clear fallback behavior.
- Treat token registration endpoint as backend-owned contract.
- Route deep links from notification payload data (`deepLink`, `deeplink`, `url`, `path`) through a single parser.

## Validation Expectations
- Notification files exist when `WithPush` is enabled.
- Push registration helper compiles.
- Deep-link parser file exists.
- Notification deep-link test (`__tests__/notification-deeplink.test.ts`) exists.
