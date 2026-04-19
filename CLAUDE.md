# CLAUDE.md

Default load `./SKILL.md` as the local operating instructions for this repository.

Execution rules:
- Before execution, choose one minimal mode: `execute`, `bypass`, or `observe-only`.
- Use `execute` when the request is actionable and safe to carry out.
- Run light preflight only when it changes the work meaningfully.
- Do not silently rewrite the user's intent.
- Route governance, write-boundary, and source-of-truth issues to `governance-authority`.
- Route packaging, projection, synchronization, distribution, and install lifecycle issues to `lifecycle-authority`.
- Keep post-task notes short and low-noise; if hooks are weak, fall back to `Prompt-only` behavior.
