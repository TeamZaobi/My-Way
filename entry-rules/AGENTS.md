# AGENTS.md

Scope: repository root unless you intentionally place it deeper.

This repository uses `SKILL.md` as the public `My-Way` contract.

## Entry Rules

- Default to the local `My-Way` companion contract in `./SKILL.md`.
- Before execution, make one minimal `Prelude` decision: `rewrite-light`, `bypass`, or `observe-only`.
- Do not silently change the user's intent.
- Keep governance, write-boundary, and source-of-truth issues outside the companion layer; treat them as `governance-authority`.
- Keep packaging, projection, synchronization, distribution, and live-install issues outside the companion layer; treat them as `lifecycle-authority`.
- After the main task, emit at most one short `Postlude` carry-forward note when the host supports it.
- If hooks are weak or missing, degrade to `Prompt-only` behavior rather than pretending stronger integration exists.

For migration and host capability guidance, read `./references/migration-host-model.md`.
