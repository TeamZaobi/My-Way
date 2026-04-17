# CLAUDE.md

Use this file as the Claude Code entry adapter for the public `My-Way` surface.

The product contract remains in `./SKILL.md`. This file should stay thin and host-specific.

## Entry Rules

- Load `./SKILL.md` as the authoritative public companion contract for this repository.
- On each turn, produce one minimal `Prelude` outcome: `rewrite-light`, `bypass`, or `observe-only`.
- Never silently rewrite the user's goal.
- Keep governance and repository-boundary decisions outside the companion layer; route them as `governance-authority`.
- Keep packaging, projection, synchronization, distribution, and install lifecycle work outside the companion layer; route them as `lifecycle-authority`.
- Emit at most one short `Postlude` carry-forward note after the main task when a note is warranted.
- If Claude Code cannot provide reliable lifecycle signals for a turn, fall back to `Prompt-only` behavior.

See `./references/migration-host-model.md` for capability tiers and adoption order.
