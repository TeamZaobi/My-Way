# My-Way Requirements Spec v0.2

## 1. Product Statement

`My-Way` is a host-integrated companion product. The public surface in this directory is the public projection of the same product and the public migration substrate for moving hosts onto its portable contract.

This public surface is meant to stand on its own inside a public repository. It defines what public adopters may implement and validate. It does not attempt to restore or disclose private overlays.

## 2. Public Objectives

- keep one stable per-turn contract across supported hosts
- let public adopters start in `Prompt-only` mode and migrate toward stronger host integration
- expose append-only operational artifacts that are reviewable and portable
- separate companion behavior from governance and lifecycle authority
- accept structured review input from an external reference source without requiring private system coupling

## 3. Public Boundary

The public surface must be safe to publish and safe to adopt.

It must include:

- public terminology
- host-facing behavior
- host entry-rule examples for file-based hosts
- artifact shapes and schemas
- examples and validation entrypoints
- migration guidance

It must exclude:

- private operator names
- personalized memory semantics
- secrets, live runtime state, and internal connectors
- unpublished implementation details whose only purpose is to recreate a private environment

If a detail is required only to reconstruct a private source tree, it is out of scope for the public surface.

## 4. Core Operating Model

Each turn follows a portable five-step sequence:

1. determine the user goal, hard constraints, and active authority boundary
2. produce one minimal `Prelude` outcome
3. let the host execute the main task
4. emit at most one short `Postlude` carry-forward note
5. run review triage only when durable material surfaced

### 4.1 Prelude Outcomes

- `rewrite-light`
  - clarify or compress wording without changing user intent
- `bypass`
  - pass through unchanged when direct execution is safer
- `observe-only`
  - do not rewrite; only observe and optionally note

### 4.2 Non-Negotiable Constraints

- no silent intent drift
- proposal before high-impact mutation
- one active authority boundary per mixed issue
- compact carry-forward notes by default
- graceful fallback when hosts lack strong hooks

## 5. Authority Model

The public surface uses three generic authority classes:

- `companion-core`
  - per-turn shaping, short notes, and review triage
- `governance-authority`
  - source of truth, write scope, repository boundary, and governance decisions
- `lifecycle-authority`
  - packaging, projection, synchronization, distribution, and live-install lifecycle work

`My-Way` may route work to these authorities, but the companion layer must not absorb their responsibilities.

## 6. Host Capability Model

### 6.1 Prompt-only

- no stable lifecycle hooks
- best-effort front and back processing only

### 6.2 Hook-enhanced

- the host emits reliable start, execute, and end signals
- `Prelude + Postlude` can run deterministically

### 6.3 Fusion-enabled

- the host can also receive or emit structured review material
- external reference input becomes part of the supported lifecycle

## 7. Public Artifacts

The public surface recognizes three artifact classes:

- `turn event`
  - append-only operational facts about a turn
- `carry-forward note`
  - one short human-readable summary meant to help later review
- `review exchange packet`
  - structured material passed between `My-Way` and an external reference source

These artifacts are operational and review-oriented. They are not a claim of personal memory storage.

### 7.1 Compatibility Note

Some bundled runtime examples may still serialize older transport labels such as:

- `global-candidate`
- `memory`
- `*_owner`

In the public contract, interpret them as:

- wider review candidate scope
- carry-forward context material
- routing labels

They are compatibility encodings, not public product semantics.

## 8. External Reference Sources

The public surface allows optional review exchange with an external reference source.

Requirements:

- the external source is a generic role, not a named private system
- exchange units must be reviewable material, not private live state
- triage output is limited to `adopt`, `diverge`, or `upstream-candidate`
- `v0` requires review and auditability, not automatic bilateral mutation

## 9. Migration Requirements

The public surface must support three migration directions:

- new public adoption
  - a public repository can adopt `My-Way` directly from this directory
- host capability migration
  - an existing host can move from `Prompt-only` to `Hook-enhanced` to `Fusion-enabled`
- private-to-public projection
  - an internal or private deployment can project its stable host contract into this directory without publishing private overlays

Migration must preserve these rules:

- public docs stay authoritative for the public contract
- private overlays remain optional and out-of-tree
- migration adds public capability; it does not reconstruct private implementation details
- host bootstrap may begin from `entry-rules/`, but those files stay thin and defer to `SKILL.md`

## 10. Non-Goals

- publishing a full private source mirror
- exporting personalized memory or identity semantics
- turning `My-Way` into a new general-purpose agent runtime
- collapsing governance, lifecycle, and companion concerns into one authority
- requiring private hooks or private directories to understand the public product
