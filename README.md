# My-Way Public Surface

`My-Way` in this directory is the public projection of the same product.
It is meant to be carried by a public repository directly, but it should still express the product clearly, not just list exported files.

This public surface exists to answer four questions in public language:

- what problem `My-Way` is trying to solve
- how the product works at a high level
- what mature-project patterns it is borrowing
- what is intentionally excluded from the public contract

## What Problem It Solves

`My-Way` is not a generic agent framework.
It is a portable companion layer for AI-native hosts such as Codex, Claude Code, and AntiGravity.

Its real job is to reduce a few recurring costs that show up in long-running human and AI collaboration:

- repeated explanation of compressed intent, boundary, and default assumptions
- repeated teaching of review style, acceptance method, and problem-solving heuristics
- repeated reminders to mount common low-level helper capabilities
- repeated loss of stable context across turns and across hosts

So the public product is not “one more skill”.
It is a portable way to carry a stable collaboration method across hosts.

## How We Define The Product

In public, `My-Way` is best understood as four things at once:

- an `always-on companion`, not a one-off prompt trick
- a portable collaboration adapter, not a business-domain skill pack
- a bounded turn contract that stabilizes intent translation, method hooks, capability mounts, and low-noise carry-forward
- a public migration substrate that a host can adopt without access to any private workspace

The product goal is not to replace the host.
The goal is to make the host work more like a stable human and AI collaboration system.

## What It Borrows From Mature Projects

The project borrows from mature companion-style systems, including the kind of design patterns you pointed to in `evolve`-like work.

The point is not to copy their directory shape.
The point is to adopt the stable patterns underneath:

- boundary matrices
  - what belongs in truth, what belongs in projection, what never belongs in public
- minimal directory structure
  - contract layers versus examples versus live state
- stable `Prelude / Postlude` seams
  - a reliable pre-turn and post-turn integration surface
- layered memory flow
  - `capture -> promote -> consolidate -> retrieve`

This public surface therefore exposes the method, not the private working state.

## Public Operating Model

The public product model is now:

1. optionally recall a bounded slice of durable carry-forward context before a new turn
2. translate compressed user intent into a bounded execution framing
3. choose reusable method hooks and capability mounts for the turn
4. let the host execute the main task
5. emit one short `Postlude` note when warranted
6. derive an optional durable carry-forward candidate
7. consolidate promoted candidates into a durable store
8. feed a bounded recall plan back into the next `Prelude`

This is the main public idea:

carry-forward should not collapse into raw logs.
It should be layered, typed, and bounded.

## Public Memory Position

This public surface does not claim a hidden personal memory system.
But it does expose the portable structure of the memory pipeline.

Publicly, the layers are:

- `turn.note`
  - short human-readable turn summary
- `turn.carryforward.candidate`
  - promoted durable-context candidate
- `carryforward.store`
  - consolidated durable record layer
- `turn.carryforward.recall`
  - bounded injection plan for the next turn

That distinction matters.
Without it, a system usually drifts into one of two bad states:

- everything is written, nothing is reusable
- everything is dumped back into context, so carry-forward becomes noise

## What This Public Surface Includes

- thin root entry files with the minimal execution surface for file-based hosts
- the portable turn contract
- public terminology
- host capability model
- routing model
- schemas, examples, and validators
- host adapter notes
- ready-to-copy entry-rule examples for file-based hosts

This directory is authoritative for the public contract.

## What It Intentionally Excludes

- private owner names
- personalized memory semantics
- internal routing conventions
- secrets and environment-specific state
- live runtime state
- unpublished connectors and internal release mechanics
- any detail whose only purpose is to reconstruct a private workspace

The omissions are intentional.
They are boundary decisions, not missing documentation.

## Directory Map

```text
public-surface/
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── README.md
├── SKILL.md
├── entry-rules/
│   ├── README.md
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── GEMINI.md
│   └── GENERIC-HOST.md
├── references/
│   ├── origin-methodology-keywords.md
│   ├── migration-host-model.md
│   ├── requirements-spec.md
│   ├── system-architecture.md
│   └── turn-templates.md
├── runtime/
│   ├── README.md
│   ├── bridge/
│   ├── examples/
│   ├── guardrails/
│   ├── hosts/
│   └── schemas/
└── scripts/
```

## Read Order

1. `README.md`
2. `SKILL.md`
3. `references/requirements-spec.md`
4. `references/system-architecture.md`
5. `references/turn-templates.md`
6. `runtime/README.md`
7. `entry-rules/README.md`
8. `references/migration-host-model.md`

## Validation

```bash
python scripts/myway_validate.py bundle
python scripts/myway_smoke.py
```

Run validation after changing public documentation, schemas, runtime examples, or host adapter notes so the public projection stays coherent.
