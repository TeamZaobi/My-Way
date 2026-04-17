# My-Way Migration Host Model

## 1. Purpose

This document explains how the public surface represents the same product in a form that public hosts can adopt and public repositories can carry.

The core rule is simple: migrate hosts toward the public contract, not toward private implementation details.

## 2. Same-Product Model

`My-Way` has one product identity and two exposure layers:

- `public surface`
  - the portable contract published in this directory
- `private overlay`
  - optional internal workflows, connectors, state stores, or release mechanics that remain outside the public repository

The public surface is a projection of the same product, not a mock implementation. The private overlay is optional for public adopters and intentionally out of scope here.

## 3. Host Responsibilities

Any host that integrates `My-Way` through the public surface is responsible for:

- exposing a turn boundary that `My-Way` can observe
- honoring the three `Prelude` outcomes
- allowing a short `Postlude` note to be emitted or persisted
- keeping public artifacts append-only and reviewable
- routing governance and lifecycle questions to the proper authority rather than hiding them in the companion layer

## 4. Capability Tiers

### 4.1 Prompt-only

Use when:

- the host has no stable lifecycle hooks
- integration must start with the lightest possible contract

Requirements:

- accept a best-effort `Prelude`
- allow a short `Postlude` note
- keep the integration stateless or minimally stateful

### 4.2 Hook-enhanced

Use when:

- the host can emit stable start, execute, and end events

Requirements:

- map host events to the public turn model
- make `Prelude + Postlude` deterministic
- emit public artifacts in a validator-friendly form

### 4.3 Fusion-enabled

Use when:

- the host can exchange structured review material with an external reference source

Requirements:

- keep review exchange auditable
- keep private live state out of exchange packets
- treat triage as decision support, not automatic bilateral mutation

## 5. Migration Paths

### 5.1 New Public Adoption

1. Choose the matching bootstrap file from `entry-rules/` if the host supports repository-level entry files.
2. Adopt the terminology and turn contract from `SKILL.md`.
3. Use this document and the requirements spec to choose the initial host tier.
4. Validate the bundle with the public scripts.
5. Add host-specific details only at the adapter edge.

### 5.2 Existing Host Upgrade

1. Inventory the host's current turn signals and write boundary.
2. Start from the lightest supported tier.
3. Promote only when the host can satisfy the stronger contract reliably.
4. Keep transport compatibility labels only where needed for migration.

### 5.3 Private-To-Public Projection

1. Identify the stable public contract already present in the private deployment.
2. Project only host-facing behavior, artifact contracts, and migration guidance into this directory.
3. Remove private names, personalized carry-forward semantics, internal release details, and environment-specific state.
4. Treat omitted private material as intentionally non-public, not as a future reconstruction task.

## 6. Compatibility Language

During migration, you may encounter older transport labels in examples or validators.

Preferred public language:

- `governance-authority` instead of `governance-owner`
- `lifecycle-authority` instead of `lifecycle-owner`
- `carry-forward context` instead of `memory`
- `cross-host-candidate` instead of `global-candidate`

Compatibility rule:

- keep older labels only when an existing artifact, validator, or host adapter still depends on them
- document the public meaning in words even if compatibility labels remain in serialized examples
- keep host entry files thin; do not fork product semantics across `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`

## 7. Extension Rules

- extend the public surface only when the new concept is portable across hosts
- keep host-specific mechanics in host adapter documentation or code, not in the product contract
- do not publish a detail whose only value is to recreate a private operating environment
- if a new capability changes write boundary or packaging lifecycle, update routing language before adding more implementation detail

## 8. Success Criteria

A migration is successful when all of the following are true:

- a public repository can adopt the surface without access to private directories
- the host behavior matches the public turn contract
- validation passes against the public bundle
- readers can understand what is intentionally omitted and why
- no public document implies that the directory is a full private source restore
