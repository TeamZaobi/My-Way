---
name: my-way
description: Portable companion meta-skill surface for Codex, Claude Code, AntiGravity, and similar AI-native hosts. Defines a minimal Prelude/Postlude contract, explicit method hooks and capability mounts, public routing rules, and migration guidance without exposing private overlays.
---

# My-Way

`My-Way` is a portable companion meta-skill surface for Codex, Claude Code, AntiGravity, and similar AI-native hosts. This file describes the host-facing contract of the same product in a form that a public repository can carry directly.

It is not a private source mirror. It does not expose personalized carry-forward state, private operator naming, unpublished connectors, or internal release workflows.
It defines the public contract for this repository; a host-local live install may use a linked copy or another projection.
Stable semantics should align across surfaces, but this file does not claim that every live install is byte-identical to the public repository copy.

## When To Use It

- Enable `My-Way` when a host wants lightweight per-turn companion behavior around an existing execution loop
- Use this public surface when documenting, integrating, validating, or migrating the product in public
- Start in `Prompt-only` mode if the host has no stable hooks, then migrate upward only when the host can support richer lifecycle signals

## Public Contract

`My-Way` does eleven things in public:

- translates compressed user intent into a bounded execution framing when needed
- selects bounded method hooks and capability mounts when the turn needs them
- may run one bounded probe-edit cycle when live tool behavior matters more than further speculation
- derives one minimal `Prelude` decision before execution
- leaves at most one short `Postlude` carry-forward note after execution
- may derive one optional durable carry-forward candidate from that note
- may consolidate promoted carry-forward candidates into a durable carry-forward store
- may build one bounded recall plan from that store before the next `Prelude`
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

1. Optionally recall a bounded set of durable carry-forward records relevant to the new turn.
2. Identify the user goal, hard constraints, and active authority boundary.
3. Select any bounded method hooks or capability mounts the turn actually needs.
4. Produce one minimal `Prelude` outcome.
5. Let the host execute the main task.
6. Append one short `Postlude` note if a note is warranted.
7. Optionally derive one durable carry-forward candidate if reusable context surfaced.
8. Optionally consolidate promoted candidates into a durable carry-forward store.
9. Optionally run review triage if durable material surfaced.

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

When present, method hooks and capability mounts stay explicit and bounded:

- a method hook is a reusable acceptance, review, or problem-solving lens for the current turn
- a capability mount is a bounded instruction to attach a common low-level helper surface for the current turn
- neither one changes the user's goal; they only shape how the host executes it

## Bounded Socratic Questioning

`Socratic questioning` is an optional method hook, not a mandatory interrogation loop.

Use it when:

- hidden assumptions, success criteria, or authority boundaries are still unstable
- the current plan may be optimizing the wrong problem
- one short challenge pass is likely to reduce rework or decision risk

Execution rules:

- prefer one short challenge pass with only a few high-value questions
- if the answer can be derived from repository context or stable constraints, keep the challenge internal and proceed
- ask the user directly only when a real decision is blocked

Do not let this become ritual, philosophy theater, or avoidable latency.

## Bounded Probe-Edit Loop

`Bounded probe-edit` is another optional method hook.

Use it when:

- live tool or model behavior can change the right answer materially
- a small probe is cheaper than guessing which rewrite will work
- the turn needs empirical signal before committing to a broader rewrite or route

Execution rules:

- start with the smallest useful probe
- classify the failure mode before editing instructions
- change one primary layer at a time when possible
- keep one representative failure and one current best result for comparison
- if the same failure repeats twice, consider rerouting or rewriting the structure instead of adding more local clauses

Do not let this become blind batch running, endless polishing, or fake certainty from noisy samples.

## Visual Routing Guardrail

When the turn becomes a multi-pass visual-production task, `My-Way` should not absorb the full image workflow into the companion layer.

Its public role is only to:

- identify that the task belongs to a dedicated visual or image skill
- route toward that specialized skill, defaulting to `visual-prompt-router` when the host has it installed
- keep a few high-level guardrails active

Public guardrails for visual turns:

- do not overwrite approved outputs before acceptance
- keep browser-based image runs serialized by default
- only run `Web + CLI` in parallel when the user explicitly permits parallel lanes
- for structure-heavy outputs such as mechanism pages or triptychs, prefer structural correctness over mood if both cannot be preserved at once
- for structure-heavy or text-heavy outputs, prefer one small probe cycle before scaling into a larger batch

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

A carry-forward candidate is a bounded durable-context sidecar. It can feed later review or a private overlay, but it is still not a claim of hidden user memory.

Some bundled examples may still use older transport labels such as `global-candidate`, `memory`, or `*_owner`. Interpret them as compatibility encodings for wider review scope, carry-forward context material, and routing labels rather than literal public product language.

## References

- Runtime bundle: [runtime/README.md](./runtime/README.md)
- Origin and keywords: [references/origin-methodology-keywords.md](./references/origin-methodology-keywords.md)
- Host entry rules: [entry-rules/README.md](./entry-rules/README.md)
- Migration model: [references/migration-host-model.md](./references/migration-host-model.md)
- Requirements: [references/requirements-spec.md](./references/requirements-spec.md)
- Architecture: [references/system-architecture.md](./references/system-architecture.md)
- Turn templates: [references/turn-templates.md](./references/turn-templates.md)
