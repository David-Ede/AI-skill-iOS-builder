# Generator Data Adapter Contract

## Purpose

Define the canonical adapter architecture for generated repositories.
This contract ensures web and native apps share domain behavior while using platform-specific implementations for storage, auth, sync, and content access.

---

## Scope

- Profile: `rn-spg-v1`
- Effective Date: `2026-02-17`
- Applies To:
  - `packages/core` adapter interfaces
  - web adapter implementations
  - native adapter implementations
  - generated dependency wiring

---

## 1. Adapter Principles

1. Domain-first: business logic depends on interfaces, not SDKs.
2. Platform-specific integrations are isolated behind adapters.
3. Offline-first behavior is required for core learning flows.
4. Missing remote config must degrade safely (no hard crash).
5. Adapter behavior must be deterministic and testable.

---

## 2. Canonical Adapter Taxonomy

Generated repos must include these adapter categories:

| Category                | Interface Owner   | Purpose                                                        |
| ----------------------- | ----------------- | -------------------------------------------------------------- |
| Auth adapter            | `@mova/core`      | User session identity and auth state subscription              |
| Progress repository     | `@mova/core`      | Read/write user course progress and optional live subscription |
| Entitlements repository | `@mova/core`      | Resolve Pro/paid status by platform source                     |
| Local store adapter     | `@mova/core`      | Platform persistence abstraction (async key/value)             |
| Content source adapter  | `@mova/data`      | Load course/lesson/grammar/decks/tips payloads                 |
| Analytics adapter       | `@mova/analytics` | Typed event logging with provider/noop implementations         |

---

## 3. Required Core Interfaces

These interfaces are mandatory baseline contracts for generated code.

```ts
export interface AuthAdapter {
  currentUser: AuthUser | null;
  onAuthStateChanged(callback: (user: AuthUser | null) => void): () => void;
  signOut(): Promise<void>;
}

export interface ProgressRepository {
  getProgress(userId: string): Promise<UserCourseProgress | null>;
  saveProgress(userId: string, progress: UserCourseProgress): Promise<void>;
  subscribeProgress?: (
    userId: string,
    callback: (progress: UserCourseProgress | null) => void
  ) => () => void;
}

export interface EntitlementsRepository {
  getEntitlements(userId: string): Promise<Entitlements | null>;
}

export type LocalStoreAdapter = {
  getItem: <T = unknown>(key: string) => Promise<T | null | undefined>;
  setItem: <T = unknown>(key: string, value: T) => Promise<void>;
  removeItem?: (key: string) => Promise<void>;
};
```

Rules:

- Interface signatures must not be changed in profile `rn-spg-v1`.
- Optional methods must degrade gracefully if absent.

---

## 4. Platform Binding Matrix

| Surface           | Web Adapter                        | Native Adapter                     | Fallback                               |
| ----------------- | ---------------------------------- | ---------------------------------- | -------------------------------------- |
| Auth              | Firebase Web Auth                  | RN Firebase Auth                   | `null` user state + safe no-op signout |
| Progress sync     | Firestore web/admin path           | RN Firebase Firestore path         | Memory repository                      |
| Local persistence | IndexedDB (`idb-keyval`)           | AsyncStorage                       | in-memory defaults for missing reads   |
| Content fetch     | HTTP content source (`@mova/data`) | HTTP content source (`@mova/data`) | explicit fetch error state             |
| Analytics         | Provider-backed (consent-aware)    | provider or console/noop           | noop adapter                           |

---

## 5. Storage Contract

### 5.1 Canonical Local Keys

Generated adapters must preserve stable key semantics aligned to shared core constants:

- profile
- progress map
- course progress
- word mastery
- section mastery
- mastery sync metadata
- mastery migration flag
- exercise seed cache
- device seed id
- crossword last section
- quest state
- grammar store state

### 5.2 Serialization Rules

- Stored values must be JSON-serializable.
- Parse failures must not crash app bootstrap.
- Parse failures return safe fallback defaults.

### 5.3 Map/Record Rule

- If data is exposed as `Map` in domain logic, adapters may persist as object records and reconstruct maps on read.

---

## 6. Migration Contract

Adapters must support idempotent legacy migration for persistence keys where legacy keys are known.

Migration requirements:

1. Check canonical key first.
2. If missing, probe known legacy keys.
3. If legacy value found, write-through to canonical key.
4. Return migrated value.
5. Never re-migrate when canonical value exists.

Rules:

- Migration must be safe to re-run.
- Migration must not erase canonical values.
- Migration outcomes should be observable in debug logs when enabled.

---

## 7. Auth and Sync Contract

### 7.1 Auth Adapter Requirements

- `currentUser` returns normalized user object or `null`.
- `onAuthStateChanged` always returns unsubscribe function.
- If provider unavailable, callback must be invoked with `null` and unsubscribe remains safe.

### 7.2 Progress Repository Requirements

- Progress data is user-scoped.
- `saveProgress` must be merge-safe for partial updates where supported.
- `subscribeProgress` is optional but if implemented must provide unsubscribe cleanup.

### 7.3 Memory Fallback Requirement

- Generated code must include a memory progress repository fallback for unavailable remote provider states.

---

## 8. Content Source Contract

Generated content adapters must expose these capabilities:

- course structure
- lesson payload by `unitId/sectionId`
- wordlist
- alphabet
- decks
- grammar topics/modules
- tips payload
- audio URL resolution

Rules:

- Non-2xx responses must raise structured fetch errors.
- Base URL normalization must avoid trailing slash path bugs.
- Content contract types should be shared from `@mova/data`.

---

## 9. Error Handling Contract

### 9.1 Error Classes

Adapter errors should be categorized as:

- `adapter_unavailable`
- `adapter_timeout`
- `adapter_parse_error`
- `adapter_remote_error`
- `adapter_auth_error`

### 9.2 Behavior Rules

- Local storage read/write failures: degrade with fallback and continue.
- Remote sync failures: preserve local state and mark sync as deferred.
- Auth provider missing: operate in signed-out mode without throwing.
- Content fetch failures: surface explicit UI error states, not silent nulls.

---

## 10. Performance Contract

Adapter implementations must satisfy:

- Non-blocking I/O on UI-critical paths.
- Avoid synchronous storage APIs in web.
- Keep initialization side effects bounded and predictable.
- Repeated reads should avoid unnecessary re-parsing where caching is safe.

---

## 11. Security Contract

Adapter implementations must:

- Never embed secrets in source.
- Respect App Check / auth enforcement on protected routes.
- Scope data access by authenticated user ID where applicable.
- Avoid cross-user reads/writes in default repository paths.

---

## 12. Test Contract for Adapters

Generated repos must include adapter-focused tests:

| Test Area                    | Minimum Coverage                               |
| ---------------------------- | ---------------------------------------------- |
| Local store fallback         | Read failure returns defaults                  |
| Local migration              | Legacy key migrates to canonical key           |
| Auth adapter unavailable     | Returns safe null state and no-op unsubscribe  |
| Progress repository fallback | Uses memory repository when remote unavailable |
| Content source errors        | Non-OK responses raise handled errors          |
| Serialization                | Stored and loaded values preserve shape        |

Test levels:

- Unit tests for each adapter category.
- Integration tests for store initialization flow (content -> profile -> course -> mastery).

---

## 13. Repo Check Gate Mapping

Adapter contract enforcement maps to gates:

- `RG-002` Type check: interface compatibility.
- `RG-004`/`RG-005` tests: adapter behavior.
- `RG-011` parity: consistent platform behavior.
- `RG-012` output contract: required adapter files present.
- `RG-013` secret scan: no credential leakage.

Recommended future dedicated gate:

- `RG-016` Adapter Contract Check (`node scripts/check-adapter-contract.js`).

---

## 14. Required Output Artifacts for Adapter Layer

Generated output should include:

- shared adapter interfaces in `packages/core`
- web adapter bindings in web app source
- native adapter bindings in `apps/native/src/lib`
- fallback implementations for unavailable providers
- adapter contract test files

Optional report:

- `reports/adapter-contract.report.json`

---

## 15. Versioning and Change Control

- Contract version: `1`
- Any interface signature change requires:
  - Stack profile update
  - Parity contract impact review
  - output contract update
  - adapter migration plan

Backward compatibility rule:

- Additive fields/methods are allowed only if optional and default-safe.

---

## 16. Changelog

### 2026-02-17

- Initial adapter contract created.
- Added mandatory adapter taxonomy, platform bindings, migration semantics, fallback rules, and test/gate requirements.
