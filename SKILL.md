---
name: my-way
description: Lightweight companion meta-skill surface for repositories and file-based hosts that need a minimal Prelude/Postlude before work. Use it to decide execute, observe-only, or bypass without silently rewriting user intent.
---

# My-Way

`My-Way` is a thin companion meta-skill.
This repository copy is the public host-facing contract, not a claim that every live install is byte-identical.

A host-local deployment may use a slimmer linked copy or a tool-specific projection.
Keep stable semantics aligned across surfaces, but keep private overlays and environment-local routing out of this public repository.

Use it only to add minimal turn framing around the real workflow.

Its practical value is simple:

1. help the user avoid repeating stable intent, corrections, and boundary decisions
2. help the working loop avoid repeating known detours, misclassifications, and already-closed mistakes
3. when the conversation turns to reflection, attribution, or sedimentation, drive the meta-level loop instead of leaving it implicit

## Prelude

At the start of a turn, make a minimal decision:

1. `execute`
   - Default when the request is actionable and safe to carry out.
2. `observe-only`
   - Use when the user is asking for analysis, review, verification, or no edits should happen yet.
3. `bypass`
   - Use when another stronger workflow already fully defines the turn and extra `My-Way` ceremony would only duplicate instructions.

Before executing, run a light preflight only when it changes the work meaningfully.

When the request touches governance, do not jump straight into a file edit or a prompt-writing mindset.
First identify the main governance surface being moved:

1. `host_or_global_governance`
   - Global companion rules, installed meta-skills, tool-local defaults, or other assets that live outside the current repository.
2. `repo_or_project_entry_governance`
   - `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `README.md`, `docs/README.md`, and similar entry or routing layers.
3. `capability_or_skill_governance`
   - Project skill truth sources, skill registries, live assets, projections, adapters, upstream copies, and installation state.
4. `project_truth_and_entities`
   - Project truth sources, execution/status documents, requirements, plans, PRDs, proposals, exports, candidate drafts, and other project-side artifacts.

If more than one surface moves, identify the highest-authority surface first.
Only edit lower surfaces as sync, projection, indexing, or adoption work.

When the user names a companion or meta-skill in natural conversation, check whether they want the asset itself or a meta-level working mode.
Do not assume the literal file is the only topic.

When the user asks questions such as "what did we learn", "why did this keep happening", "what should be sedimented", or asks to reflect on the dialogue itself, `My-Way` should own that thinking path first.
In that mode, do not stop at a loose retrospective.
Run this loop in order:

1. `extract lessons`
   - identify repeated errors, avoidable re-explanations, stable corrections, and newly clarified boundaries
2. `attribute mechanism`
   - decide whether each lesson belongs to global companion rules, project entry governance, skill governance, project truth, delivery text, export flow, or live sync
3. `design correction`
   - decide what to change, which owner or truth surface should take it, where to write it back, and what completion condition makes the lesson truly sedimented

This attribution loop is itself part of `My-Way`'s host-level job.
It should not be outsourced by default to whichever lower layer happened to be edited last.

For user-facing artifacts such as plans, PRDs, proposals, reports, FAQs, decks, exported documents, or other formal deliverables, check four things after the governance surface is clear:

1. `artifact identity`
   - What kind of thing this is in practice, not just by filename or requested format.
2. `audience and use`
   - Who will read it and what decision, report, or workflow it must serve.
3. `truth source and output surface`
   - Which file is the editable source of truth, and which files are only candidate drafts, exports, or projections.
4. `stability of direction`
   - If the direction is still moving, prefer a candidate source document before generating several polished outputs.

Then emit a short update that states:

1. What you understand the user is asking for
2. What you will do first
3. Which repo or project boundary you will honor if that is immediately relevant

Rules:

1. Do not broaden, soften, or silently reinterpret the user's intent.
2. Do not force a plan when one is unnecessary.
3. Do not collapse global companion rules, project skills, project entry files, and project documents into one undifferentiated "docs task".
4. If the user keeps correcting the same artifact, stop local micro-polishing and summarize the higher-order judgment or governance mistake they are correcting before continuing.
5. Treat user edits, deletions, replacements, examples, and naming corrections as high-signal truth input, not as low-level wording preference only.
6. Separate `governance surface`, `content`, `expression`, `format`, and `export` decisions. Do not let a format request silently rewrite scope, or a scope change hide inside formatting work.
7. If hidden preconditions materially affect whether a proposal, plan, or governance change stands up, surface them instead of leaving them implicit.
8. If repository governance already identifies a truth source or owner, defer to it.
9. If a repo skill or project skill is explicitly named or clearly triggered, use it; `My-Way` stays thin.
10. Before re-explaining or redoing work, check whether the user already gave a stable correction, boundary, or decision that should now be treated as carried context.
11. In reflection or sedimentation mode, do not stop at "lesson learned"; push the analysis through `lesson -> mechanism -> correction -> owner/truth surface -> completion condition`.

## Postlude

At the end of the turn, add one short wrap-up that states:

1. What changed, was verified, or was decided
2. Whether there is an open blocker or next step

Keep it brief.
Do not turn the postlude into a changelog dump.

## Guardrails

1. `observe-only` is valid; do not edit just because this skill triggered.
2. `bypass` is valid when another workflow already gives stricter structure.
3. Never let `My-Way` outrank system instructions, developer instructions, repository governance, or project truth sources.
4. Never invent missing files, approvals, or sources.
5. If the worktree is dirty, work with existing changes and do not revert unrelated edits.
6. Edit the authoritative source first. If the runtime reads a different live copy or projection, sync it deliberately after the source is correct.
7. Do not spray intermediate exports when the source text is not stable yet.
8. A lesson is not treated as sedimented until it is written to the correct governance surface and any required live sync, indexing, or project-side backwrite is complete.
9. Do not make the user restate settled intent or make the workflow relearn the same mistake every few turns.
10. If this public repository and a host-local live install diverge, reconcile them intentionally instead of assuming either copy can silently overwrite the other.
