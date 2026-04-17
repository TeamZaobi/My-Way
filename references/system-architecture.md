# My-Way System Architecture v0.2

## 1. Architecture Goal

`My-Way` must behave like one product across hosts while exposing a public surface that can be adopted without access to private overlays.

The architecture therefore optimizes for five properties:

1. one portable turn contract across hosts
2. deterministic `Prelude + Postlude` behavior when host signals allow it
3. append-only operational artifacts with low-noise human summaries
4. explicit routing to governance and lifecycle authorities
5. reviewable exchange with external reference sources without leaking private state

## 2. Product Layering

The public surface is a projection layer, not a full source mirror.

```text
Host tool
  -> Host adapter
  -> Companion core
  -> Public artifacts
  -> Authority routing
  -> Optional review exchange

Private overlays, if they exist, stay outside this public directory.
They may consume or project the same public contract, but they are not required
to understand or adopt the product from public.
```

Within a public repository, this directory is authoritative for the public contract. It is not authoritative for private implementation details that are intentionally omitted.

## 3. Runtime Components

### 3.1 Host Adapter

Purpose:

- translate host-specific lifecycle signals into a portable turn model
- report host capability level
- preserve host-specific integration details at the edge

The host adapter does not own governance, lifecycle, or review policy.

### 3.2 Companion Core

Purpose:

- derive the `Prelude` outcome
- maintain the turn state machine
- emit the short `Postlude` carry-forward note when warranted
- decide whether review triage is needed

The companion core is the public behavior center of `My-Way`.

### 3.3 Public Artifact Layer

Purpose:

- persist append-only turn facts
- persist at most one short note per turn
- expose reviewable artifacts to tooling and validators

The artifact layer is operational. It is not a personal memory subsystem.

### 3.4 Authority Routing

Purpose:

- route source-of-truth and boundary issues to `governance-authority`
- route projection, synchronization, and distribution issues to `lifecycle-authority`
- keep the companion layer focused on turn behavior

### 3.5 Review Exchange

Purpose:

- accept structured material from an external reference source
- emit `adopt`, `diverge`, or `upstream-candidate`
- keep review exchange auditable and bounded

The review exchange layer does not directly mutate private systems.

## 4. Turn State Machine

The public state machine is intentionally small:

```text
idle -> prelude -> execute -> postlude -> review -> idle
```

### 4.1 State Semantics

- `idle`
  - waiting for a new turn
- `prelude`
  - choose `rewrite-light`, `bypass`, or `observe-only`
- `execute`
  - the host performs the main task
- `postlude`
  - emit a short carry-forward note if warranted
- `review`
  - inspect durable material and produce a triage decision if needed

### 4.2 Transition Rules

- `idle -> prelude`
  - a new user turn or equivalent host trigger arrives
- `prelude -> execute`
  - the host receives the chosen pre-execution framing
- `execute -> postlude`
  - the host finishes the turn or returns a stable result
- `postlude -> review`
  - durable material surfaced and qualifies for review exchange
- `review -> idle`
  - triage is recorded and the turn is closed

## 5. Host Capability Modes

### 5.1 Prompt-only

- no stable lifecycle hooks
- best-effort companion behavior only

### 5.2 Hook-enhanced

- host emits reliable start, execute, and end signals
- `Prelude + Postlude` can be enforced consistently

### 5.3 Fusion-enabled

- host also supports structured review exchange
- external reference material becomes part of the supported lifecycle

## 6. Public Artifact Contracts

The examples below describe the public semantics. Some bundled runtime examples may still use older transport labels for compatibility.

### 6.1 Turn Event

```yaml
turn_event:
  event_id: string
  turn_id: string
  timestamp: iso-8601
  host_id: codex | claude-code | antigravity | other
  mode: prompt-only | hook-enhanced | fusion-enabled
  phase: turn_start | prelude | execute | postlude | review | handoff
  source: user | host | my-way | reference-system
  payload_summary: string
  related_paths?: [string]
  confidence?: low | medium | high
  source_tag?: string
  event_hash?: string
```

Rules:

- append-only
- minimal factual summary is preferred over full payload dumps
- `event_hash` may be used for de-duplication

### 6.2 Carry-Forward Note

```yaml
turn_note:
  note_id: string
  turn_id: string
  scope: session | project | cross-host-candidate
  goal: string
  actions: string
  result: string
  candidate_points?: [string]
  retention: short | medium | review-required
```

Rules:

- at most one short note per turn
- default scope is `session`
- promotion requires repeated value or explicit review need
- a note is a human-readable summary, not hidden user memory

Compatibility note:

- some existing examples may serialize `cross-host-candidate` as `global-candidate`
- the public meaning is "candidate for wider review", not "global memory"

### 6.3 Review Exchange Packet

```yaml
review_exchange_packet:
  packet_id: string
  source_system: reference-system | my-way
  target_system: my-way | reference-system
  material_type: note | pattern | workflow | guardrail | carry-forward-context | skill-candidate
  layer: worldview | workflow | guardrail | implementation
  summary: string
  evidence: [string]
  candidate_action: adopt | diverge | upstream-candidate
  local_decision_reason?: string
  follow_up_authority?: companion-core | governance-authority | lifecycle-authority
```

Rules:

- exchange reviewable material only
- do not ship private live state through this packet
- `v0` triage is decision support, not automatic bilateral mutation

Compatibility note:

- some bundled examples may still encode `carry-forward-context` as `memory`
- some bundled examples may still encode `follow_up_authority` with `*_owner` labels
- those labels are transport compatibility, not the preferred public vocabulary

## 7. Authority Routing

| Issue type | Primary authority | Companion behavior |
|---|---|---|
| prelude and postlude behavior | `companion-core` | primary |
| source of truth, write scope, repository boundary | `governance-authority` | observe, route, add context |
| projection, sync, distribution, live-install lifecycle | `lifecycle-authority` | observe, route, add context |
| review of external reference material | `companion-core` | primary |
| review outcome that requires public or private projection work | `lifecycle-authority` | receive proposal |
| review outcome that changes repository boundary or truth policy | `governance-authority` | receive proposal |

## 8. Guardrails

- `intent safety`
  - `Prelude` may clarify, compress, or pass through; it may not change user intent
- `noise control`
  - facts and notes stay separate; notes stay short
- `routing discipline`
  - mixed issues must resolve to one primary authority
- `review containment`
  - review exchange is bounded and auditable
- `migration discipline`
  - public adoption must not depend on reconstructing omitted private material

## 9. Evolution Path

### v0

- public turn state machine
- public artifact contracts
- authority routing
- review triage

### v1

- stronger validation across host adapters
- promotion and pruning rules for carry-forward notes
- richer review evidence handling

### v2

- optional external verification surfaces
- host capability comparison and migration tooling
