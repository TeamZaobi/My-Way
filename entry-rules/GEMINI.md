# GEMINI.md

Use this file as the Gemini CLI entry adapter for the public `My-Way` surface.

Keep this file small. The public product contract remains in `./SKILL.md`.

## Entry Rules

- Treat `./SKILL.md` as the canonical public contract for repository-local `My-Way` behavior.
- Before the main task, choose one minimal `Prelude` outcome: `rewrite-light`, `bypass`, or `observe-only`.
- Do not silently change the user's intent, task boundary, or success target.
- Keep governance and write-boundary decisions outside the companion layer; route them as `governance-authority`.
- Keep projection, packaging, synchronization, distribution, and install lifecycle work outside the companion layer; route them as `lifecycle-authority`.
- After the main task, emit at most one short `Postlude` carry-forward note when the host can persist one safely.
- If Gemini integration is running without stable project hooks, remain in `Prompt-only` mode instead of simulating richer lifecycle support.

Use `./references/migration-host-model.md` when promoting the host from `Prompt-only` toward stronger integration tiers.
