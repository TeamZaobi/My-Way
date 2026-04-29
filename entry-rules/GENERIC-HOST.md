# Generic Host Entry Rule

Default load `./SKILL.md` as the local operating instructions for this repository.

Execution rules:
- Before execution, choose one minimal mode: `rewrite-light`, `bypass`, or `observe-only`.
- Use `rewrite-light` only to compress wording, expose execution constraints, and identify the active authority or needed method and capability layers without changing the user's goal.
- Before hardening a new constraint, decide whether it belongs as a thin entry guardrail, a skill-level method rule, a project boundary rule, or an executable contract. Keep entry files thin by default.
- Do not silently rewrite the user's intent.
- Route governance, write-boundary, and source-of-truth issues to `governance-authority`.
- Route packaging, projection, synchronization, distribution, and install lifecycle issues to `lifecycle-authority`.
- Keep post-task notes short and low-noise; if hooks are weak, fall back to `Prompt-only` behavior.
