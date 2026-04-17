# My-Way System Architecture v0.3

## 1. Architecture Goal

`My-Way` must behave like one product across hosts while exposing a public surface that can be adopted without access to private overlays.

The architecture therefore optimizes for seven properties:

1. one portable turn contract across hosts
2. bounded intent translation so hosts can understand compressed user requests with less repetition
3. reusable method hooks that can carry acceptance and problem-solving structure across turns
4. reusable capability mounts that expose common low-level helper surfaces explicitly
5. deterministic `Prelude + Postlude` behavior when host signals allow it
6. explicit routing to governance and lifecycle authorities
7. reviewable exchange with external reference sources without leaking private state

## 2. Product Layering

The public surface is a projection layer, not a full source mirror.

```text
Host tool
  -> Carry-forward recall
  -> Host adapter
  -> Intent translation
  -> Method layer
  -> Capability mount layer
  -> Companion core
  -> Public artifacts
  -> Optional carry-forward sidecar
  -> Durable carry-forward store
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

### 3.2 Carry-Forward Recall

Purpose:

- read a bounded subset of durable carry-forward records before a new turn starts
- produce an injection-ready recall plan instead of dumping the whole store back into context

This mirrors the layered memory approach used in mature systems: retrieve only what the current turn needs.

### 3.3 Intent Translation

Purpose:

- translate compressed user wording into a bounded execution framing when needed
- preserve user intent while exposing only the constraints that execution actually needs

Intent translation is part of the companion contract, but it must remain reversible and low-noise.

### 3.4 Method Layer

Purpose:

- select reusable acceptance, review, or problem-solving hooks for the current turn
- keep those hooks explicit instead of hiding them in ad hoc prompt expansion

The method layer does not create a new task. It only chooses a reusable working lens.

### 3.5 Capability Mount Layer

Purpose:

- attach the common helper surfaces that a turn repeatedly depends on
- keep those helper choices explicit, bounded, and auditable

Capability mounts may include search, comparison, validation, or other low-level helpers, but they remain turn-scoped execution aids.

### 3.6 Companion Core

Purpose:

- derive the `Prelude` outcome
- coordinate recall, intent translation, method hooks, and capability mounts inside that outcome
- maintain the turn state machine
- emit the short `Postlude` carry-forward note when warranted
- derive an optional durable carry-forward candidate when reusable context surfaced
- decide whether review triage is needed

The companion core is the public behavior center of `My-Way`.

### 3.7 Public Artifact Layer

Purpose:

- persist append-only turn facts
- persist at most one short note per turn
- expose reviewable artifacts to tooling and validators

The artifact layer is operational. It is not a personal memory subsystem.

### 3.8 Optional Carry-Forward Sidecar

Purpose:

- extract durable, reusable context from a finished turn
- keep that context separate from the human-readable note
- provide a stable handoff seam for host hooks and optional private overlays

This sidecar is still not a hidden user-memory system. It is a bounded compatibility layer for durable carry-forward context.

### 3.9 Durable Carry-Forward Store

Purpose:

- upsert promoted carry-forward candidates into stable durable records
- preserve provenance, reinforcement count, and preferred injection slot for later recall

This separates capture from durable storage, which is a common mature-project pattern for memory systems.

### 3.10 Authority Routing

Purpose:

- route source-of-truth and boundary issues to `governance-authority`
- route projection, synchronization, and distribution issues to `lifecycle-authority`
- keep the companion layer focused on turn behavior

### 3.11 Review Exchange

Purpose:

- accept structured material from an external reference source
- emit `adopt`, `diverge`, or `upstream-candidate`
- keep review exchange auditable and bounded

The review exchange layer does not directly mutate private systems.

## 4. Turn State Machine

The public state machine is intentionally small:

```text
idle -> carry-forward-recall -> prelude(intent-translation / method-select / capability-mount) -> execute -> postlude -> carry-forward -> carry-forward-store -> review -> idle
```

### 4.1 State Semantics

- `idle`
  - waiting for a new turn
- `carry-forward-recall`
  - retrieve a bounded subset of durable records for the next turn
- `prelude`
  - choose `rewrite-light`, `bypass`, or `observe-only`, and attach any bounded method hooks or capability mounts
- `execute`
  - the host performs the main task
- `postlude`
  - emit a short carry-forward note if warranted
- `carry-forward`
  - derive an optional durable sidecar candidate when the turn produced reusable context
- `carry-forward-store`
  - consolidate promoted candidates into stable durable records
- `review`
  - inspect durable material and produce a triage decision if needed

### 4.2 Transition Rules

- `idle -> prelude`
  - a new user turn or equivalent host trigger arrives
- `idle -> carry-forward-recall`
  - the host wants to retrieve a bounded durable context slice before `Prelude`
- `prelude -> execute`
  - the host receives the chosen pre-execution framing
- `execute -> postlude`
  - the host finishes the turn or returns a stable result
- `postlude -> carry-forward`
  - reusable context surfaced and the host wants a durable sidecar artifact
- `carry-forward -> carry-forward-store`
  - the host wants promoted candidates consolidated into the durable store
- `carry-forward-store -> review`
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

### 6.3 Carry-Forward Candidate

```yaml
turn_carryforward_candidate:
  candidate_id: string
  turn_id: string
  source_note_id: string
  source_scope: session | project | global-candidate
  decision: skip | carry-forward
  candidate_type: none | preference | constraint | method-pattern | capability-mount-rule | workflow-pattern | routing-rule | external-pattern | project-context
  candidate_text: string
  rationale: string
  evidence: [string]
  confidence: low | medium | high
  stability: turn-signal | repeat-observed | durable
  write_target: none | carry-forward
```

Rules:

- optional sidecar, not required for every host
- do not treat this as personal memory or hidden user profiling
- use it when a turn produced durable context worth reusing later
- explicit method patterns and capability mount rules may be promoted directly when the turn states them clearly
- private overlays may consume it, but the public contract does not require that

### 6.4 Carry-Forward Record

```yaml
carryforward_record:
  record_id: string
  record_key: string
  candidate_type: preference | constraint | method-pattern | capability-mount-rule | workflow-pattern | routing-rule | external-pattern | project-context
  candidate_text: string
  status: active | superseded | archived
  preferred_injection_slot: method-hooks | capability-mounts | hard-constraints | carry-over
  reinforcement_count: integer
```

Rules:

- this is a durable compatibility store, not a hidden personal memory subsystem
- upsert and provenance matter more than raw append volume
- the store exists so recall can stay bounded and typed

### 6.5 Carry-Forward Recall Plan

```yaml
turn_carryforward_recall:
  query_text: string
  selected_records:
    - record_id: string
      candidate_type: string
      injection_slot: method-hooks | capability-mounts | hard-constraints | carry-over
      reason: string
  recommended_method_hooks: [string]
  recommended_capability_mounts: [string]
  recommended_hard_constraints: [string]
  carry_over_points: [string]
```

Rules:

- keep recall bounded and typed
- inject only the minimal slice the next `Prelude` needs
- do not dump the whole durable store back into context

### 6.4 Review Exchange Packet

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
