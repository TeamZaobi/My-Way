# Generic Host Entry Rule

Use this template when a host supports project-level instructions but does not use `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`.

## Minimal Contract

- Load the repository-local `My-Way` contract from `./SKILL.md`.
- Before execution, emit one minimal `Prelude` outcome: `rewrite-light`, `bypass`, or `observe-only`.
- Do not silently rewrite user intent.
- Route governance and source-of-truth issues to `governance-authority`.
- Route packaging, projection, synchronization, distribution, and install lifecycle work to `lifecycle-authority`.
- Emit at most one short `Postlude` carry-forward note after the main task when supported.
- If the host cannot expose reliable lifecycle signals, stay in `Prompt-only` mode.

Port these rules into the host's own repository instruction mechanism and keep any host-specific details at the adapter edge.
