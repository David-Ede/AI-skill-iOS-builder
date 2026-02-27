# Auth Patterns

## Scope
This module scaffolds auth/session structure, not a full backend integration.

## Required Components
- Auth context/provider for signed-in state.
- Sign-in screen scaffold.
- Secure storage adapter for token/session persistence.
- Sign-out path that clears persisted session.

## Secure Storage
- Use `expo-secure-store` abstraction layer.
- Keep keys centralized and namespaced.
- Never persist secrets in plain text files.

## Provider Slots
- Email/password placeholder workflow.
- OAuth placeholder methods for Apple/Google sign-in.

## Validation Expectations
- Auth files exist when `WithAuth` is enabled.
- Session storage abstraction compiles.
- Smoke test (or unit test) covers sign-in -> sign-out state transitions.
