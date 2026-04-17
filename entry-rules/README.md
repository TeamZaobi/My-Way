# Host Entry Rules

This directory provides ready-to-copy repository entry files for file-based AI-native hosts.

Use these files as bootstrap adapters, not as alternate product truth. Keep them short and stable. The full product contract still lives in `../SKILL.md`, `../references/requirements-spec.md`, and `../references/migration-host-model.md`.

## File Matrix

- `AGENTS.md`
  - for Codex and other hosts that read `AGENTS.md` from the repository root or subtree
- `CLAUDE.md`
  - for Claude Code repositories
- `GEMINI.md`
  - for Gemini CLI repositories
- `GENERIC-HOST.md`
  - for hosts that support a repository instruction file but use a different filename or settings surface

## Usage Rules

1. Copy the matching file to the repository root used by the target host.
2. Keep the entry file minimal: host activation, `Prelude` guardrails, routing boundary, and `Postlude` rule only.
3. Point any deeper semantics back to `SKILL.md` and the reference docs instead of duplicating them inline.
4. If multiple tools share the same repository, it is acceptable to keep more than one entry file at the root as long as they carry the same public contract.
5. If a host has no file-based repository entrypoint, port `GENERIC-HOST.md` into its host-native project instruction mechanism.
