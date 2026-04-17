---
name: my-way
description: Portable companion meta-skill surface for Codex, Claude Code, AntiGravity, and similar AI-native hosts. Defines a minimal Prelude/Postlude contract, public routing rules, and migration guidance without exposing private overlays.
---

# My-Way

`My-Way` is a portable companion meta-skill surface for Codex, Claude Code, AntiGravity, and similar AI-native hosts. This file describes the host-facing contract of the same product in a form that a public repository can carry directly.

It is not a private source mirror. It does not expose personalized carry-forward state, private operator naming, unpublished connectors, or internal release workflows.

## When To Use It

- Enable `My-Way` when a host wants lightweight per-turn companion behavior around an existing execution loop
- Use this public surface when documenting, integrating, validating, or migrating the product in public
- Start in `Prompt-only` mode if the host has no stable hooks, then migrate upward only when the host can support richer lifecycle signals

## Public Contract

`My-Way` does five things in public:

- derives one minimal `Prelude` decision before execution
- leaves at most one short `Postlude` carry-forward note after execution
- records append-only turn facts separately from human-readable notes
- routes governance and lifecycle issues to the correct authority instead of absorbing them into the companion layer
- accepts optional review material from an external reference source without assuming private system access

## What It Does Not Do

- mirror a private repository or recover omitted private files
- claim personal memory, identity storage, or hidden user profile semantics
- own project governance, source-of-truth decisions, or packaging and distribution policy
- require unpublished host hooks or internal control planes

## Turn Contract

Every turn follows the same public sequence:

1. Identify the user goal, hard constraints, and active authority boundary.
2. Produce one minimal `Prelude` outcome.
3. Let the host execute the main task.
4. Append one short `Postlude` note if a note is warranted.
5. Optionally run review triage if durable material surfaced.

`Prelude` allows only three outcomes:

- `rewrite-light`
  - compress wording or expose execution constraints without changing the user's intent
- `bypass`
  - pass the request through unchanged when direct execution is safer
- `observe-only`
  - do not rewrite; only observe and optionally leave a short note

`rewrite-light` must never:

- expand the task into a different task
- change user intent
- pre-empt governance or lifecycle decisions that belong elsewhere
- add visible ritual that distracts from the host's main job

## Routing Model

The public surface uses three generic authority classes:

- `companion-core`
  - turn shaping, short notes, and review triage
- `governance-authority`
  - source of truth, write scope, boundary, and repository governance
- `lifecycle-authority`
  - packaging, projection, synchronization, distribution, and live-install lifecycle work

`My-Way` may identify and hand off to the right authority, but it does not absorb their responsibilities.

## Host Capability Modes

- `Prompt-only`
  - best-effort front and back processing with no stable lifecycle hooks
- `Hook-enhanced`
  - the host provides start, execute, and end signals so `Prelude + Postlude` becomes reliable
- `Fusion-enabled`
  - the host can also accept structured review material from an external reference source

## Terminology Guardrail

In this public surface, a note is a short carry-forward summary for later review. It is not a claim of personal memory or a hidden user model.

Some bundled examples may still use older transport labels such as `global-candidate`, `memory`, or `*_owner`. Interpret them as compatibility encodings for wider review scope, carry-forward context material, and routing labels rather than literal public product language.

## References

- Runtime bundle: [runtime/README.md](./runtime/README.md)
- Origin and keywords: [references/origin-methodology-keywords.md](./references/origin-methodology-keywords.md)
- Host entry rules: [entry-rules/README.md](./entry-rules/README.md)
- Migration model: [references/migration-host-model.md](./references/migration-host-model.md)
- Requirements: [references/requirements-spec.md](./references/requirements-spec.md)
- Architecture: [references/system-architecture.md](./references/system-architecture.md)
- Turn templates: [references/turn-templates.md](./references/turn-templates.md)
