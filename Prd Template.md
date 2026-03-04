# Universal PRD Template (Skill-Guided Build Contract)

Use this file as the primary instruction contract for any AI Skill that generates architecture, tasks, or code.

## Usage Rules
1. Fill all fields marked `REQUIRED`.
2. Leave optional modules disabled instead of deleting them.
3. Replace every `[PLACEHOLDER]`.
4. Keep requirement IDs stable once implementation starts.
5. If a required field is unknown, write `UNKNOWN` and add an open question.

## expo-ios-app-builder Preflight Rules
Use these additional rules when this PRD is used with this repository's skill:

1. Set primary platform to `iOS` or `Multi-platform` with iOS-first scope.
2. Ensure required placeholders are replaced before scaffold.
3. For modules without direct scaffold flags (`MOD-CONTENT`, `MOD-TRANSACT`, `MOD-SOCIAL`, `MOD-ADMIN`, `MOD-INTEG`, `MOD-SEARCH`, `MOD-MEDIA`), define explicit FRs and test contracts for custom implementation.

If required placeholders remain unresolved or required fields are missing, the workflow must return `BLOCKED_INPUT`.

## Skill Contract
- The Skill must treat this PRD as authoritative for product behavior.
- If any `REQUIRED` field is missing, the Skill must return `BLOCKED_INPUT` and list missing fields.
- The Skill must map each `FR-*` and `NFR-*` requirement to implementation tasks and tests.
- The Skill must not implement out-of-scope items unless the PRD changes.

## 0. Document Control
- Product name (`REQUIRED`): `[PROJECT_NAME]`
- PRD version (`REQUIRED`): `[vX.Y]`
- Date (`REQUIRED`): `[YYYY-MM-DD]`
- Owner (`REQUIRED`): `[NAME]`
- Status (`REQUIRED`): `[Draft | Approved | In Build | Released]`
- Linked plan (`REQUIRED`): `[docs/PLAN.md]`
- Linked tracker (`REQUIRED`): `[Issue board path/url]`

### 0.1 Build Inputs for Skill Execution (`REQUIRED` for this skill)
- App name (`REQUIRED`): `[npm-safe-name, e.g. weather-app]`
- iOS bundle ID (`REQUIRED`): `[com.company.product]`
- Output directory (`REQUIRED`): `[absolute/or-relative-path]`
- Release branch (`REQUIRED`): `[main or release/*]`
- Repo provider (`REQUIRED`): `[github]`

## 1. Product Definition
- Product summary (`REQUIRED`):
  - `[One clear sentence]`
- Problem statement (`REQUIRED`):
  - `[What pain is solved, for whom, and why now]`
- Target users (`REQUIRED`):
  - `[Primary persona(s)]`
- Primary platform (`REQUIRED`):
  - `[iOS | Android | Web | Desktop | Multi-platform]`
- App type (`REQUIRED`):
  - `[Consumer | B2B SaaS | Marketplace | Content | Utility | Game | Internal Tool | Other]`

## 2. Objectives, Scope, and Boundaries
### 2.1 Objectives (`REQUIRED`)
- O-001: `[User outcome + measurable target + date]`
- O-002: `[Business outcome + measurable target + date]`
- O-003: `[Technical outcome + measurable target + date]`

### 2.2 MVP In Scope (`REQUIRED`)
1. `[Capability 1]`
2. `[Capability 2]`
3. `[Capability 3]`

### 2.3 Out of Scope (`REQUIRED`)
- `[Explicit non-goal 1]`
- `[Explicit non-goal 2]`
- `[Explicit non-goal 3]`

### 2.4 Post-MVP Candidates (Optional)
- `[Candidate 1]`
- `[Candidate 2]`

## 3. Modular Architecture Selection
Set `Enabled` to `Yes` only for modules required by this product.
For `expo-ios-app-builder`, modules without direct scaffold flags require custom implementation work in the feature phase.

| Module ID | Module Name | Enabled (Yes/No) | Priority (P0/P1/P2) | Notes |
| --- | --- | --- | --- | --- |
| MOD-AUTH | Authentication and authorization | `No` | `P0` | `[If accounts/roles needed]` |
| MOD-ONBOARD | Onboarding and setup | `Yes` | `P0` | `[First-run setup flow]` |
| MOD-PROFILE | User profile and preferences | `No` | `P1` | `[Settings/profile support]` |
| MOD-CONTENT | Content/catalog/feed management | `No` | `P1` | `[Lists, detail views, search]` |
| MOD-TRANSACT | Checkout/payments/subscriptions | `No` | `P0` | `[Billing flows]` |
| MOD-MSG | Notifications/messaging/reminders | `No` | `P1` | `[Push, email, in-app, SMS]` |
| MOD-SOCIAL | Sharing/community/social graph | `No` | `P2` | `[Comments, follows, likes]` |
| MOD-OFFLINE | Offline-first and sync conflict handling | `No` | `P0` | `[Local cache + sync policy]` |
| MOD-ADMIN | Admin/back-office tools | `No` | `P2` | `[Internal controls]` |
| MOD-ANALYTICS | Product analytics and telemetry | `Yes` | `P0` | `[Events, KPIs, crash metrics]` |
| MOD-INTEG | External integrations/APIs | `No` | `P1` | `[3rd party dependencies]` |
| MOD-SEARCH | Search/filter/sort/recommendations | `No` | `P1` | `[Discovery features]` |
| MOD-MEDIA | File/image/audio/video handling | `No` | `P1` | `[Upload, playback, compression]` |
| MOD-LOCALE | Localization/timezone/regional behavior | `No` | `P1` | `[I18n and locale logic]` |
| MOD-ACCESS | Accessibility requirements | `Yes` | `P0` | `[A11y baseline]` |
| MOD-COMPLY | Security/privacy/compliance controls | `Yes` | `P0` | `[Regulatory and policy controls]` |

## 4. Module Requirement Blocks
Create one block for each module with `Enabled = Yes`.

```md
### Module: [MOD-ID] [Module Name]
- Status: [Enabled]
- Owner: [Name/team]
- Goal: [What this module achieves]
- Dependencies: [Other modules or external systems]

#### Functional Requirements
| ID | Requirement | Priority | Acceptance Criteria |
| --- | --- | --- | --- |
| FR-[MOD]-001 | [Behavior] | [P0/P1/P2] | [Given/When/Then] |
| FR-[MOD]-002 | [Behavior] | [P0/P1/P2] | [Given/When/Then] |

#### Data Contracts
- Entities: [List entities and key fields]
- Validation rules: [Rules]
- Error handling: [Expected behavior]

#### UX Contracts
- Screens/routes involved: [List]
- Empty/error/loading states: [Expected behavior]
- Accessibility notes: [Focus order, labels, contrast, dynamic type]

#### Test Contracts
- Unit tests: [What must be covered]
- Integration tests: [What must be covered]
- E2E/manual tests: [Critical scenario]
```

## 5. End-to-End User Journeys (`REQUIRED`)
Define the critical paths the Skill must preserve.

| Journey ID | Name | Trigger | Success Outcome | Failure Handling |
| --- | --- | --- | --- | --- |
| J-001 | `[Primary journey]` | `[What starts it]` | `[Observable success]` | `[Fallback/retry/error]` |
| J-002 | `[Secondary journey]` | `[What starts it]` | `[Observable success]` | `[Fallback/retry/error]` |
| J-003 | `[Setup/activation journey]` | `[What starts it]` | `[Observable success]` | `[Fallback/retry/error]` |

## 6. Global Functional Requirements (`REQUIRED`)
Requirements that apply across modules.

| ID | Requirement | Priority | Acceptance Criteria |
| --- | --- | --- | --- |
| FR-GLOB-001 | `[App initializes to usable state]` | `P0` | `[Defined startup criteria]` |
| FR-GLOB-002 | `[State consistency rules]` | `P0` | `[No conflicting states]` |
| FR-GLOB-003 | `[Settings/config edits apply safely]` | `P0` | `[Changes persist and rehydrate correctly]` |
| FR-GLOB-004 | `[Error surfaces are user-actionable]` | `P1` | `[Clear messages + recovery path]` |

## 7. Data, State, and Integration Contracts (`REQUIRED`)
### 7.1 Data Strategy
- Source of truth (`REQUIRED`): `[Local | Remote | Hybrid]`
- Persistence (`REQUIRED`): `[AsyncStorage | SQLite | API DB | etc.]`
- Schema versioning (`REQUIRED`): `[Version key + migration policy]`
- Time handling (`REQUIRED`): `[Local timezone | UTC | mixed rules]`
- Retention/deletion (`REQUIRED`): `[Policy]`

### 7.2 External Dependencies
| Dependency | Purpose | Owner | SLA/Rate Limit | Failure Behavior |
| --- | --- | --- | --- | --- |
| `[Service/API/SDK]` | `[Why needed]` | `[Owner]` | `[Constraint]` | `[Fallback behavior]` |
| `[Service/API/SDK]` | `[Why needed]` | `[Owner]` | `[Constraint]` | `[Fallback behavior]` |

## 8. Non-Functional Requirements (`REQUIRED`)

| ID | Category | Requirement | Target |
| --- | --- | --- | --- |
| NFR-001 | Performance | `[Startup time]` | `[e.g., <2.0s on target device]` |
| NFR-002 | Reliability | `[Crash-free sessions]` | `[e.g., >=99.5%]` |
| NFR-003 | Availability | `[Service availability if backend exists]` | `[e.g., 99.9%]` |
| NFR-004 | Security | `[Baseline controls]` | `[Policy or measurable target]` |
| NFR-005 | Accessibility | `[A11y compliance level]` | `[e.g., WCAG AA baseline]` |
| NFR-006 | Observability | `[Logs/metrics/traces coverage]` | `[Coverage target]` |

## 9. Security, Privacy, and Compliance (`REQUIRED`)
- Auth model: `[None | Email | OAuth | SSO | etc.]`
- Authorization model: `[Roles or N/A]`
- Sensitive data classes: `[PII, health, payment, etc.]`
- Storage and encryption policy: `[At rest/in transit rules]`
- Secret handling policy: `[CI secret names only, never raw values in repo]`
- Compliance scope: `[None | GDPR | HIPAA | SOC2 | PCI-DSS | etc.]`
- Abuse/threat considerations: `[Rate limits, brute force protections, moderation, etc.]`

## 10. Analytics and Observability
### 10.1 Product Metrics (`REQUIRED`)
- North star metric: `[Metric + target + date]`
- Supporting metrics:
  - `[Metric + target + date]`
  - `[Metric + target + date]`

### 10.2 Event Contract
| Event Name | Trigger | Required Properties | PII Allowed (Yes/No) |
| --- | --- | --- | --- |
| `[event_name]` | `[when fired]` | `[prop_a, prop_b]` | `No` |
| `[event_name]` | `[when fired]` | `[prop_a, prop_b]` | `No` |

### 10.3 Operational Telemetry
- Crash reporting: `[Tool + owner]`
- Logs: `[Tool + retention policy]`
- Alerts: `[Condition + channel + owner]`

## 11. Release and Environment Contract (`REQUIRED`)
### 11.1 Environment Matrix
| Env | Purpose | Config Source | Data Policy | Approval Gate |
| --- | --- | --- | --- | --- |
| `dev` | `[Local dev and feature work]` | `[env file/secret manager]` | `[Synthetic/test data]` | `[none/team lead]` |
| `staging` | `[Pre-release validation]` | `[secret manager/CI]` | `[Masked production-like]` | `[QA signoff]` |
| `prod` | `[End users]` | `[secret manager/CI]` | `[Production policy]` | `[Release owner]` |

### 11.2 Release Path
- Build pipeline: `[Toolchain and command path]`
- Distribution path: `[App store/web deploy/internal distro]`
- Required accounts: `[Provider + owner]`
- CI secrets (names only): `[SECRET_1], [SECRET_2]`

### 11.3 Release Gates
1. `[Lint/typecheck/test pass]`
2. `[Build pass on target platforms]`
3. `[Security checks pass]`
4. `[Performance baseline pass]`
5. `[Submission/deploy pass]`
6. `[Post-release smoke test pass]`

## 12. QA and Test Strategy (`REQUIRED`)
- Test levels:
  - Unit: `[Scope]`
  - Integration: `[Scope]`
  - E2E: `[Scope]`
  - Manual: `[Scope]`
- Core regression suite:
| Test ID | Covers Requirement IDs | Test Type | Pass Criteria |
| --- | --- | --- | --- |
| T-001 | `[FR-... IDs]` | `[Unit/Int/E2E/Manual]` | `[Expected result]` |
| T-002 | `[FR-... IDs]` | `[Unit/Int/E2E/Manual]` | `[Expected result]` |

## 13. Delivery Mapping for the Skill
This section enables deterministic execution planning.

| Requirement ID | Ticket/Epic ID | Owner | Milestone | Verification Artifact |
| --- | --- | --- | --- | --- |
| `[FR-... or NFR-...]` | `[tracker ID]` | `[owner]` | `[M1/M2/etc.]` | `[test report, screenshot, URL]` |
| `[FR-... or NFR-...]` | `[tracker ID]` | `[owner]` | `[M1/M2/etc.]` | `[test report, screenshot, URL]` |

## 14. Risks, Assumptions, and Open Questions (`REQUIRED`)
### 14.1 Risks
- `[Risk] -> [Mitigation] -> [Owner]`
- `[Risk] -> [Mitigation] -> [Owner]`

### 14.2 Assumptions
- `[Assumption 1]`
- `[Assumption 2]`

### 14.3 Open Questions
1. `[Question 1]`
2. `[Question 2]`
3. `[Question 3]`

## 15. Definition of Ready and Definition of Done (`REQUIRED`)
### 15.1 Definition of Ready
- All `REQUIRED` fields filled or explicitly marked `UNKNOWN`.
- All enabled modules have at least one `FR-*` requirement.
- Environment and release owners assigned.
- Acceptance criteria exist for all P0 requirements.

### 15.2 Definition of Done
- All P0 `FR-*` and `NFR-*` requirements implemented and validated.
- All release gates pass in target environments.
- No unresolved blocker risks.
- PRD version updated with final change log entry.

## 16. Change Log
- `[YYYY-MM-DD] [Version] [Change summary] [Owner]`
- `[YYYY-MM-DD] [Version] [Change summary] [Owner]`

## Appendix A: Optional Module Blueprints
Use these only if relevant. Copy into Section 4 as enabled modules.

### A1 Authentication Blueprint
- Signup/signin methods: `[Email/OAuth/SSO/etc.]`
- Session model: `[Token/cookie/refresh strategy]`
- Account recovery: `[Flow and constraints]`

### A2 Payments Blueprint
- Billing model: `[One-time/subscription/usage]`
- Providers: `[Stripe/App Store/Play/etc.]`
- Failure behavior: `[Retry, grace period, downgrade]`

### A3 Notifications Blueprint
- Channels: `[Push/email/SMS/in-app]`
- Opt-in/permission behavior: `[Flow]`
- Delivery guarantees/fallbacks: `[Policy]`

### A4 Offline Sync Blueprint
- Cache strategy: `[Read/write policy]`
- Sync trigger policy: `[Foreground/background/manual]`
- Conflict resolution: `[Last-write-wins/merge/manual]`

### A5 AI Feature Blueprint
- Model provider(s): `[Provider/model names]`
- Prompt/policy constraints: `[Safety, tone, refusals]`
- Latency and cost budgets: `[Targets]`
