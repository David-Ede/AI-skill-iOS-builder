# AI Skill iOS Builder

This repository contains the documentation framework for an iOS-focused skill generator workflow.

## Contents

- `generator-framework/skill_skeleton.md`: Baseline skill structure.
- `generator-framework/Generator_Input_Contracts.md`: Required input schemas and assumptions.
- `generator-framework/Generator_Output_Contract.md`: Expected generated artifacts and format.
- `generator-framework/Generator_Prompt_Protocol.md`: Prompting conventions and generation rules.
- `generator-framework/Generator_Stack_Profile.md`: Technology/profile constraints.
- `generator-framework/Generator_Compatibility_Matrix.md`: Supported combinations and constraints.
- `generator-framework/Generator_Parity_Contract.md`: Parity requirements across outputs.
- `generator-framework/Generator_Data_Adapter_Contract.md`: Data adapter boundaries and interfaces.
- `generator-framework/Generator_Human_Gates.yaml`: Human-review checkpoints.
- `generator-framework/Repo_Check_Gates.md`: Repository-level quality gates.
- `generator-framework/Generator_Failure_Playbook.md`: Failure handling and recovery expectations.
- `generator-framework/Exec_Plan.md`: Execution plan for running the workflow.

## Scope

The committed files in this repo are focused on skill and framework documentation. Generated app artifacts and local smoke outputs are intentionally excluded from the primary documentation commit history.

The Expo iOS skill templates include release intake scaffolding for human-owned deployment data (`release/human-inputs.md`) using simple `KEY = value` fill-in format.

## PRD Contract

`PRD_TEMPLATE.md` is the primary planning contract for skill-driven builds.

- Provide a completed PRD file and pass its path as `PrdPath`.
- Preflight validation and module-flag derivation are defined in `references/prd-mapping.md`.
- If required PRD fields are missing or unsupported modules are enabled, the workflow must return `BLOCKED_INPUT` before scaffolding.
