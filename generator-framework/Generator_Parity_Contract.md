# Generator Parity Contract

## Purpose

Define the required parity between web (PWA) and native (React Native) outputs for generator runs.
This contract ensures generated apps preserve product behavior across platforms without forcing identical implementation details.

---

## Scope

- Profile: `rn-spg-v1`
- Effective Date: `2026-02-17`
- Parity Targets: Web mobile experience to native app experience
- Source Baseline:
  - `planning/Platform-Expansion-UI-Inventory.md`
  - `planning/Platform-Expansion-UI-Execution-Plan.md`
  - `packages/core/src/routes.ts`
  - `apps/native/App.tsx`

---

## 1. Parity Principles

1. Behavior parity over code parity.
2. Mobile web parity baseline (not desktop web pixel parity).
3. Shared business logic first, platform UI second.
4. Explicitly documented differences are allowed.
5. Any undocumented parity gap is treated as a defect.

---

## 2. Parity Dimensions

Each feature is evaluated across these dimensions:

| Dimension              | Definition                                                              |
| ---------------------- | ----------------------------------------------------------------------- |
| Route parity           | Equivalent navigable destination exists on native                       |
| Shell parity           | Equivalent app shell behavior (visibility, navigation, layout zones)    |
| Interaction parity     | Core actions and user flows produce equivalent outcomes                 |
| Data parity            | Equivalent data contracts, state transitions, and persistence behavior  |
| Content parity         | Equivalent content rendering for lesson/tips/grammar/reference          |
| State parity           | Equivalent domain/store behavior for progress, mastery, profile, social |
| Instrumentation parity | Equivalent analytics event intent and key attributes                    |
| Error-state parity     | Equivalent empty/loading/error/retry behavior                           |

---

## 3. Parity Tiers

| Tier | Meaning                                              | Release Impact                                              |
| ---- | ---------------------------------------------------- | ----------------------------------------------------------- |
| `P0` | Core path parity required for baseline app viability | Release blocking                                            |
| `P1` | High-value parity expected in standard build         | Must pass for `pass`; can be `partial` with explicit waiver |
| `P2` | Nice-to-have parity enhancement                      | Non-blocking                                                |

---

## 4. Route Parity Contract

### 4.1 Core Route Set (P0)

These must exist and be functional in generated native output:

| Web Path                                 | Native Screen                 | Tier |
| ---------------------------------------- | ----------------------------- | ---- |
| `/`                                      | `Home`                        | P0   |
| `/unit/:unitId`                          | `Unit`                        | P0   |
| `/unit/:unitId/section/:sectionId`       | `Section`                     | P0   |
| `/unit/:unitId/section/:sectionId/learn` | `Lesson`                      | P0   |
| `/practice`                              | `Practice`                    | P0   |
| `/play`                                  | `Play`                        | P0   |
| `/flashcards`                            | `Flashcards`                  | P0   |
| `/wordmatch`                             | `WordMatch`                   | P0   |
| `/play/crossword`                        | `Crossword`                   | P0   |
| `/review`                                | `Review` or `PracticeSession` | P0   |
| `/library`                               | `Library`                     | P0   |
| `/dictionary`                            | `Dictionary`                  | P0   |
| `/alphabet`                              | `Alphabet`                    | P0   |
| `/decks`                                 | `Decks`                       | P0   |
| `/privacy`                               | `Privacy`                     | P0   |
| `/terms`                                 | `Terms`                       | P0   |
| `/delete-account`                        | `DeleteAccount`               | P0   |

### 4.2 Extended Route Set (P1)

| Web Path                               | Native Screen   | Tier |
| -------------------------------------- | --------------- | ---- |
| `/library/grammar`                     | `Grammar`       | P1   |
| `/library/grammar/:moduleId`           | `GrammarModule` | P1   |
| `/library/grammar/:moduleId/:lessonId` | `GrammarLesson` | P1   |
| `/cultural`                            | `Cultural`      | P1   |
| `/leaderboard`                         | `Leaderboard`   | P1   |
| `/leagues`                             | `Leagues`       | P1   |
| `/profile`                             | `Profile`       | P1   |
| `/profile/:username`                   | `PublicProfile` | P1   |
| `/tips/:skillId?`                      | `Tips`          | P1   |
| `/mastery`                             | `Mastery`       | P1   |
| `/streaks`                             | `Streaks`       | P1   |

### 4.3 Explicit Non-Parity Routes (Allowed)

These are web-only and are excluded from native parity requirements:

- `/_offline`
- SEO/document wrapper concerns (`_document`, SEO meta composition)
- other non-visual framework internals

---

## 5. Shell Parity Contract

### 5.1 Global Shell Elements

Native output must provide equivalents for:

- Top navigation region
- Bottom primary navigation
- Toast/feedback surface
- Consent/notice banner surface
- Back navigation behavior

### 5.2 Visibility Rules

Native shell visibility must mirror web intent:

- Lesson flow (`/unit/:unitId/section/:sectionId/learn`): hide top-level clutter, focus on lesson UI.
- Section intro (`/unit/:unitId/section/:sectionId`): hide bottom nav when flow intent is focused progression.
- Standard content routes: show primary shell navigation.

---

## 6. UI Primitive Parity Contract

Generated native output must include token-driven equivalents for:

- Buttons: primary, outline, ghost, small
- Cards
- Rows/list items
- Badges
- Progress bars
- Segmented tabs
- Modals
- Toasts/snackbars
- Banner blocks

Rules:

- Use `@mova/tokens` for spacing, color, type, radius, shadow.
- Avoid heavy third-party UI kits unless explicitly approved by profile changes.

---

## 7. Interaction Parity Contract

For parity routes, the following interaction classes must match in behavior:

1. Navigation actions (tap destination, back, deep link).
2. Primary CTA actions (start lesson, continue flow, retry, submit).
3. Selection/input actions (multiple-choice, sentence builder, settings toggles).
4. Completion actions (lesson done, review done, practice done).
5. Account/safety actions (logout, delete-account flow, report/block/mute where applicable).

Equivalent behavior means:

- Same user intent produces same domain result.
- Same key state transitions occur.
- Same terminal outcomes (success/fail/blocked) are reachable.

---

## 8. Data and State Parity Contract

### 8.1 Shared-State Requirement

Where shared stores exist in `@mova/core`, generated web/native must use shared store contracts for:

- User/profile core state
- Course progression
- Lesson flow state
- Mastery state
- Quest progression
- Grammar progression

### 8.2 Persistence Parity

- Web: IndexedDB adapter.
- Native: AsyncStorage adapter.
- Both must preserve compatible key semantics and migration expectations.

### 8.3 Remote Sync Parity

- Both platforms must map to equivalent Firebase domain contracts.
- Native can degrade gracefully if Firebase native config is missing.
- Degraded mode must be explicit and non-crashing.

---

## 9. Content Parity Contract

Generated output must preserve equivalent rendering support for:

- Lesson exercise content
- Intro content blocks (paragraph/list/info/tip/example/table classes)
- Grammar content blocks
- Tips content with safe formatting pipeline

Rules:

- Content may be rendered with platform-native components.
- Content meaning and instructional sequence must remain equivalent.

---

## 10. Analytics and Event Parity Contract

At minimum, generator output must keep event intent parity for:

- lesson started
- lesson completed
- practice opened
- dictionary opened
- profile opened
- streak updated

Rules:

- Event names and core semantics must remain aligned to `@mova/analytics`.
- Missing provider is acceptable only with noop adapter fallback and explicit logging.

---

## 11. Error/Empty/Loading Parity Contract

Each parity route must define and render equivalent states for:

- loading
- empty/no data
- recoverable error
- permission/config blocked

Equivalent states must include a user path forward (retry/back/settings/help).

---

## 12. Accessibility and Usability Minimums

Parity acceptance requires:

- Keyboard/screen-reader safe labels for actionable controls (where platform supports).
- Tap targets sized for mobile usability.
- Color contrast aligned with token system intent.
- No interaction dead-ends in core learning flow.

---

## 13. Parity Scoring and Acceptance

### 13.1 Scoring Model

Each route is scored:

- `pass`
- `partial`
- `fail`

Each dimension per route receives the same status.

### 13.2 Run-Level Acceptance

Run parity status is:

- `pass` if:
  - all P0 routes are `pass`
  - at least 90% of P1 routes are `pass`
  - no P0 dimension-level failures
- `partial` if:
  - all P0 routes are `pass` or `partial`
  - any P1 route `fail` remains with documented mitigation
- `fail` if:
  - any P0 route is `fail`
  - or any P0 route missing

---

## 14. Evidence Requirements

Parity validation evidence must be recorded in `reports/repo-check.report.json` under a `parity` section with:

- route coverage summary
- per-route status
- failed dimensions
- known waivers
- recommended follow-ups

Optional supporting artifacts:

- screenshot diffs
- navigation flow logs
- checklist markdown in `planning/generated`

---

## 15. Allowed Divergences (Must Be Documented)

Allowed divergence examples:

- Native-specific navigation mechanics (stack/tab implementation details).
- Platform-specific control primitives where intent is preserved.
- Web-only SEO/meta concerns omitted in native.
- Offline web route behavior represented by native fallback UX.

Not allowed:

- Silent route omissions for P0/P1 routes.
- Untracked feature behavior changes.
- Different business-rule outcomes between platforms for shared features.

---

## 16. Change Control

Any parity model change must update:

1. This file.
2. `Generator_Stack_Profile.md` (if architectural impact).
3. `Generator_Output_Contract.md` (if output artifacts change).
4. `Repo_Check_Gates.md` (if gating thresholds change).

---

## 17. Changelog

### 2026-02-17

- Initial parity contract created.
- Added route parity tiers, behavioral parity dimensions, acceptance thresholds, and evidence requirements.
