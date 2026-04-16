from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from enforce_guardrails import check_guardrails, persist_guardrail_check, validate_guardrail_events
from myway_runtime import (
    EVENT_SCHEMA_PATH,
    NOTE_SCHEMA_PATH,
    PACKET_SCHEMA_PATH,
    TRIAGE_AUDIT_SCHEMA_PATH,
    append_event_artifact,
    append_triage_audit,
    write_note_artifact,
    write_packet_artifact,
)
from myway_validate import collect_bundle_errors
from schema_utils import MYWAY_ROOT, append_jsonl, load_json, load_jsonl, validate_path_against_schema, write_json


def main() -> int:
    bundle_errors = collect_bundle_errors(MYWAY_ROOT)
    if bundle_errors:
        raise RuntimeError("checked-in bundle is invalid:\n" + "\n".join(bundle_errors))

    runtime_root = MYWAY_ROOT / "runtime"
    example_events = load_jsonl(runtime_root / "examples" / "turn.events.jsonl")
    example_note = load_json(runtime_root / "examples" / "turn.note.json")
    example_packet = load_json(runtime_root / "examples" / "reflection.exchange.packet.json")
    guardrail_contract = load_json(runtime_root / "guardrails" / "guardrails.contract.json")
    guardrail_state = load_json(runtime_root / "guardrails" / "guardrails.state.json")

    with TemporaryDirectory(prefix="myway-smoke-") as tmpdir:
        tmp_root = Path(tmpdir)
        events_path = tmp_root / "turn.events.jsonl"
        note_path = tmp_root / "turn.note.json"
        note_history_path = tmp_root / "turn.notes.history.jsonl"
        packet_path = tmp_root / "reflection.exchange.packet.json"
        audit_path = tmp_root / "reflection-triage-audit.jsonl"
        guardrails_state_path = tmp_root / "guardrails.state.json"
        guardrails_events_path = tmp_root / "guardrails.events.jsonl"

        for event in example_events:
            result = append_event_artifact(event, events_path)
            if result["status"] != "written":
                raise RuntimeError(f"unexpected event append result: {result}")
        duplicate_result = append_event_artifact(example_events[0], events_path)
        if duplicate_result["status"] != "deduped":
            raise RuntimeError("event hash dedupe did not trigger")

        note_result = write_note_artifact(example_note, note_path, history_path=note_history_path)
        if note_result["scope"] != "session":
            raise RuntimeError(f"unexpected base note scope: {note_result}")

        prior_note_one = deepcopy(example_note)
        prior_note_one["note_id"] = "note_project_001"
        prior_note_one["turn_id"] = "turn_project_001"
        prior_note_one["candidate_points"] = ["跨宿主稳定 companion 规则"]
        append_jsonl(note_history_path, prior_note_one)

        prior_note_two = deepcopy(example_note)
        prior_note_two["note_id"] = "note_project_002"
        prior_note_two["turn_id"] = "turn_project_002"
        prior_note_two["candidate_points"] = ["跨宿主稳定 companion 规则"]
        append_jsonl(note_history_path, prior_note_two)

        promoted_note = deepcopy(example_note)
        promoted_note["note_id"] = "note_project_003"
        promoted_note["turn_id"] = "turn_project_003"
        promoted_note["scope"] = "project"
        promoted_note["retention"] = "medium"
        promoted_note["candidate_points"] = ["跨宿主稳定 companion 规则"]
        promoted_result = write_note_artifact(
            promoted_note,
            tmp_root / "turn.project.note.json",
            history_path=note_history_path,
        )
        if promoted_result["scope"] != "project":
            raise RuntimeError(f"project promotion failed: {promoted_result}")

        invalid_note = deepcopy(example_note)
        invalid_note["note_id"] = "note_invalid_001"
        invalid_note["turn_id"] = "turn_invalid_001"
        invalid_note["scope"] = "global-candidate"
        invalid_note["candidate_points"] = ["一次性本地修补"]
        invalid_note["retention"] = "short"
        try:
            write_note_artifact(invalid_note, tmp_root / "turn.invalid.note.json")
        except ValueError:
            pass
        else:
            raise RuntimeError("invalid global promotion was accepted")

        packet_result = write_packet_artifact(example_packet, packet_path)
        if packet_result["status"] != "written":
            raise RuntimeError(f"unexpected packet write result: {packet_result}")

        triage_result = append_triage_audit(
            packet_path,
            audit_path,
            turn_id=example_note["turn_id"],
            events_path=events_path,
            note_path=note_path,
        )
        if triage_result["status"] != "written":
            raise RuntimeError(f"unexpected triage result: {triage_result}")

        if validate_path_against_schema(events_path, EVENT_SCHEMA_PATH):
            raise RuntimeError("generated events artifact failed schema validation")
        if validate_path_against_schema(note_path, NOTE_SCHEMA_PATH):
            raise RuntimeError("generated note artifact failed schema validation")
        if validate_path_against_schema(packet_path, PACKET_SCHEMA_PATH):
            raise RuntimeError("generated packet artifact failed schema validation")
        if validate_path_against_schema(audit_path, TRIAGE_AUDIT_SCHEMA_PATH):
            raise RuntimeError("generated triage audit failed schema validation")

        mutation_candidate = {
            "turn_id": "turn_guard_001",
            "turn_index": 100,
            "timestamp": "2026-04-16T12:20:00+08:00",
            "host_id": "codex",
            "owner": "my-way",
            "source_tag": "my-way-postlude",
            "action_kind": "mutation",
            "intent_summary": "touch protected skill asset",
            "path_targets": [str(MYWAY_ROOT / "SKILL.md")],
            "impact": "high",
            "mutation_requested": True,
            "review_requested": False,
        }
        mutation_result, updated_state, mutation_event = check_guardrails(
            mutation_candidate,
            guardrail_contract,
            guardrail_state,
        )
        if mutation_result["decision"] != "review-required":
            raise RuntimeError(f"protected mutation should require review: {mutation_result}")

        duplicate_candidate_one = {
            "turn_id": "turn_guard_010",
            "turn_index": 200,
            "timestamp": "2026-04-16T12:30:00+08:00",
            "host_id": "codex",
            "owner": "my-way",
            "source_tag": "user-message",
            "action_kind": "note",
            "intent_summary": "keep a lightweight postlude note",
            "path_targets": [],
            "impact": "low",
            "mutation_requested": False,
            "review_requested": False,
        }
        duplicate_candidate_two = {
            **duplicate_candidate_one,
            "turn_id": "turn_guard_011",
            "turn_index": 201,
            "timestamp": "2026-04-16T12:30:30+08:00",
        }
        duplicate_first, duplicate_state_one, duplicate_event_one = check_guardrails(
            duplicate_candidate_one,
            guardrail_contract,
            guardrail_state,
        )
        if duplicate_first["decision"] != "pass":
            raise RuntimeError(f"first lightweight candidate should pass: {duplicate_first}")
        duplicate_second, duplicate_state_two, duplicate_event_two = check_guardrails(
            duplicate_candidate_two,
            guardrail_contract,
            duplicate_state_one,
        )
        if duplicate_second["decision"] == "pass":
            raise RuntimeError("duplicate lightweight candidate should not pass twice")

        write_json(guardrails_state_path, guardrail_state)
        persist_guardrail_check(guardrails_state_path, guardrails_events_path, updated_state, mutation_event)
        persist_guardrail_check(guardrails_state_path, guardrails_events_path, duplicate_state_one, duplicate_event_one)
        persist_guardrail_check(guardrails_state_path, guardrails_events_path, duplicate_state_two, duplicate_event_two)

        guardrail_event_errors = validate_guardrail_events(load_jsonl(guardrails_events_path))
        if guardrail_event_errors:
            raise RuntimeError("generated guardrail events are invalid:\n" + "\n".join(guardrail_event_errors))

        summary = {
            "status": "ok",
            "events_written": len(load_jsonl(events_path)),
            "audit_records": len(load_jsonl(audit_path)),
            "guardrail_events": len(load_jsonl(guardrails_events_path)),
            "mutation_guardrail_decision": mutation_result["decision"],
            "duplicate_guardrail_decision": duplicate_second["decision"],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
