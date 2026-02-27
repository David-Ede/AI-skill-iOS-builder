# Auth Patterns

## Scope
This module scaffolds auth/session structure and provider slots, not a production backend integration.

## Required Components
- Auth context/provider for signed-in state.
- Sign-in screen scaffold with email/password and provider slot actions.
- Secure storage adapter for token/session persistence.
- OAuth provider slot contract (`src/auth/oauthProviders.ts`) for Apple/Google.
- Sign-out path that clears persisted session.

## Secure Storage
- Use `expo-secure-store` abstraction layer.
- Keep keys centralized and namespaced.
- Never persist secrets in plain text files.

## OAuth Provider Slots
- Keep provider config in one place (`buildOAuthProviderConfig`).
- Build redirect URIs with Expo AuthSession helpers.
- Treat client IDs and backend token exchange as human-owned setup.
- Return explicit setup guidance when placeholder values are still present.

## Validation Expectations
- Auth files exist when `WithAuth` is enabled.
- Session storage abstraction compiles.
- OAuth provider slot contract file exists.
- Auth test (`__tests__/auth-oauth.test.ts`) exists and validates provider slot behavior.
