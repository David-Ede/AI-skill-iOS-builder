# AI Skill iOS Builder

This repository is a production-oriented skill package for generating new iOS-first Expo apps with:

- Expo Router + TypeScript scaffold
- System light/dark appearance support via `userInterfaceStyle: "automatic"` and shared semantic theme tokens
- Optional baseline feature modules (auth, push, profile, data layer, analytics/crash, localization, accessibility/privacy docs)
- Contract validation gates
- GitHub Actions + EAS/TestFlight setup baseline

## Who This Is For

- Human operators running a PRD-driven build flow
- AI agents that execute the skill from `SKILL.md`
- Teams that want deterministic scaffold + release readiness checks

## Quick Start (Human)

1. Copy and complete [Prd Template.md](Prd%20Template.md).
2. Follow [Instructions For Full Production Flow.md](Instructions%20For%20Full%20Production%20Flow.md).
3. Run scaffold, validator, CI setup, and quality gates.
4. Complete release inputs and Apple/Expo setup.
5. Build and submit to TestFlight.

## Document Order

Read in this order for a full build:

1. [README.md](README.md) (orientation and contracts)
2. [Prd Template.md](Prd%20Template.md) (product/build input contract)
3. [Instructions For Full Production Flow.md](Instructions%20For%20Full%20Production%20Flow.md) (end-to-end runbook)
4. [Human Build Checklist.md](Human%20Build%20Checklist.md) (solo quick checklist)

## Required Build Inputs

- `AppName` (project directory name)
- `BundleId` (reverse-DNS iOS bundle ID, for example `com.company.product`)
- `OutputDir` (directory where app folder will be created)
- `PrdPath` (path to completed PRD from this repo template)

If required PRD fields are missing or unsupported modules are enabled, the workflow must return `BLOCKED_INPUT` and stop.

## Required Tooling and Accounts

Tooling:
- Node.js (`>= 20.19.4`)
- npm
- npx
- Python 3
- Git

Accounts:
- GitHub
- Expo (EAS)
- Apple Developer Program + App Store Connect access

## What Humans Must Still Own

The skill scaffolds and validates project structure, but humans must provide and maintain:

- Product decisions in the PRD
- Apple account/legal setup and app record creation
- Credential and secret setup (`EXPO_TOKEN`, App Store Connect API key material)
- Final release decisions and store metadata completion

## Repo Map

- `SKILL.md`: agent-facing contract and execution workflow
- `scripts/`: scaffold, CI setup, and validator tools
- `assets/templates/`: files copied into generated app projects
- `references/`: detailed constraints, mappings, quality, and release docs
- `generator-framework/`: higher-level framework contracts used by this skill family

## Success Criteria for a Build

- Scaffold succeeds
- Validator status is `pass` (or `partial` only when explicitly accepted due to human dependencies)
- `npm run lint`, `npm run typecheck`, `npm run test` pass
- Release intake (`release/human-inputs.md`) is completed
- EAS build and TestFlight submit complete successfully
