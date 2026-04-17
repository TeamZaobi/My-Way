# My-Way Origin, Methodology, and Keywords

## 1. Why This Exists

`My-Way` started from a practical wish: keep one companion close to the work across different AI-native hosts, while keeping private working state separate from the public contract.

The public surface exists because the product needed two things at once:

- a private place for the full working system and its evolving state
- a public place for the portable method, contract, and adoption path

The early design questions were straightforward:

- should this be two products or one product with two exposure layers
- should the public side be a branch, a scaffold, or a projection
- how do we make the public part useful without letting it claim private state

The answer adopted here is one product, one private truth, one public projection, and a thin export path between them.

## 2. Methodology

The public method is deliberately small:

1. define the portable contract first
2. keep host entry rules thin
3. separate companion behavior from governance and lifecycle authority
4. keep append-only operational facts separate from human-readable carry-forward notes
5. use projection and export rather than duplicate editable truth
6. let private overlays remain private unless a portable contract truly depends on them

This is not a runtime invention. It is a boundary method for making an always-on companion portable across hosts.

## 3. Keyword Index

### Product Terms

- `My-Way`
  - the same product across private and public exposure layers
- `public projection`
  - the portable contract published in this repository
- `private overlay`
  - internal workflows, state stores, and release mechanics kept outside the public repository
- `public migration substrate`
  - the public side that helps a host adopt the portable contract

### Runtime Terms

- `Prelude`
  - the minimal pre-execution framing decision
- `Postlude`
  - the short carry-forward note after execution
- `Prompt-only`
  - best-effort mode when no stable hooks exist
- `Hook-enhanced`
  - mode with reliable start, execute, and end signals
- `Fusion-enabled`
  - mode that can exchange structured review material

### Routing Terms

- `companion-core`
  - per-turn shaping and review triage
- `governance-authority`
  - source-of-truth and write-boundary decisions
- `lifecycle-authority`
  - packaging, projection, synchronization, and distribution work

### Migration Terms

- `entry-rules`
  - thin host bootstrap files such as `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`
- `cross-host-candidate`
  - a note or artifact worth wider review across hosts
- `reference-system`
  - the generic external reference source used for review exchange

## 4. How To Read The Repo

- Start with `README.md` for the overall story and boundaries
- Read `SKILL.md` for the public companion contract
- Read this file for origin, methodology, and keyword lookup
- Read `references/migration-host-model.md` for adoption paths
- Read `references/requirements-spec.md` and `references/system-architecture.md` for the operating contract
