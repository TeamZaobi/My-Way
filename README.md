# My-Way Public Surface

`My-Way` in this directory is the public projection of the same product and the public migration substrate used to adopt it in host tools.

It is designed to be carried by a public repository directly. The directory exposes the portable contract of the product: the turn model, host capability model, routing rules, schemas, examples, and validation entrypoints that a host integration can rely on without access to any private workspace.

It is intentionally not a full source restore. It does not attempt to reconstruct private operators, internal state stores, personalized carry-forward context, unpublished integrations, or internal release mechanics.

## Origin Snapshot

- This project began as a practical wish: keep one companion across AI-native hosts without turning private working state into the public contract.
- The public repo exists to explain the method, the boundary, and the portable contract, not to reconstruct the private working state behind it.
- Early design questions were about branches versus scaffolding, private source versus public projection, and how to keep the public side useful without leaking the private side.

## Keywords

- `always-on companion`
- `public projection`
- `private overlay`
- `public migration substrate`
- `Prelude`
- `Postlude`
- `Prompt-only`
- `Hook-enhanced`
- `Fusion-enabled`
- `governance-authority`
- `lifecycle-authority`
- `entry-rules`
- `cross-host-candidate`

## Product Position

- `Same product`
  - This public surface is not a fork, demo, or alternate edition. It is the public-facing projection of the same companion product.
- `Public projection`
  - Only the portable contract is published: host-facing behavior, artifact shapes, validation, and migration guidance.
- `Public migration substrate`
  - Public adopters can start from this directory and move a host from prompt-only use toward deeper lifecycle integration without learning any private naming system.

## Boundary Guarantees

- Included: portable protocol, public terminology, schemas, examples, validation scripts, and host adapter guidance
- Included: ready-to-copy host entry-rule examples for `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`
- Excluded: private owner names, personalized memory semantics, internal routing conventions, secrets, live runtime state, and private source-only implementation details
- The documents in this directory are authoritative for the public contract inside a public repository
- Missing private pieces are intentionally omitted, not invitations to reverse-engineer the private source

## Directory Map

```text
public-surface/
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
3. `references/origin-methodology-keywords.md`
4. `entry-rules/README.md`
5. `references/migration-host-model.md`
6. `references/requirements-spec.md`
7. `references/system-architecture.md`
8. `runtime/README.md`

## Validation

```bash
python scripts/myway_validate.py bundle
python scripts/myway_smoke.py
```

Run validation after changing public documentation, schemas, or host adapters so the public projection stays coherent.
