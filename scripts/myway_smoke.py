from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from enforce_guardrails import check_guardrails, persist_guardrail_check, validate_guardrail_events
from myway_runtime import (
    CARRYFORWARD_RECORD_SCHEMA_PATH,
    CARRYFORWARD_RECALL_SCHEMA_PATH,
    CARRYFORWARD_SCHEMA_PATH,
    EVENT_SCHEMA_PATH,
    NOTE_SCHEMA_PATH,
    PACKET_SCHEMA_PATH,
    TRIAGE_AUDIT_SCHEMA_PATH,
    append_event_artifact,
    append_triage_audit,
    build_carryforward_recall_plan,
    consolidate_carryforward_candidate_artifact,
    finalize_turn_artifacts,
    write_note_artifact,
    write_carryforward_candidate_artifact,
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
    example_carryforward_candidate = load_json(runtime_root / "examples" / "turn.carryforward.candidate.json")
    example_carryforward_record = load_jsonl(runtime_root / "examples" / "carryforward.store.jsonl")[0]
    example_carryforward_recall = load_json(runtime_root / "examples" / "turn.carryforward.recall.json")
    example_packet = load_json(runtime_root / "examples" / "reflection.exchange.packet.json")
    guardrail_contract = load_json(runtime_root / "guardrails" / "guardrails.contract.json")
    guardrail_state = load_json(runtime_root / "guardrails" / "guardrails.state.json")

    with TemporaryDirectory(prefix="myway-smoke-") as tmpdir:
        tmp_root = Path(tmpdir)
        events_path = tmp_root / "turn.events.jsonl"
        note_path = tmp_root / "turn.note.json"
        note_history_path = tmp_root / "turn.notes.history.jsonl"
        carryforward_path = tmp_root / "turn.carryforward.candidate.json"
        carryforward_log_path = tmp_root / "turn.carryforward.log.jsonl"
        carryforward_store_path = tmp_root / "turn.carryforward.store.jsonl"
        carryforward_recall_path = tmp_root / "turn.carryforward.recall.json"
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
        carryforward_result = write_carryforward_candidate_artifact(
            note_path,
            carryforward_path,
            history_path=note_history_path,
            carryforward_log_path=carryforward_log_path,
        )
        if carryforward_result["decision"] != "skip":
            raise RuntimeError(f"base note should not be promoted into carry-forward context: {carryforward_result}")

        finalized_note = deepcopy(example_note)
        finalized_note["note_id"] = "note_finalize_001"
        finalized_note["turn_id"] = "turn_finalize_001"
        finalized_note["scope"] = "project"
        finalized_note["retention"] = "medium"
        finalized_note["goal"] = "standardize the turn-end hook contract"
        finalized_note["actions"] = "write one note and one carry-forward candidate from a single finalize-turn command"
        finalized_note["result"] = "host adapters now have a stable end-of-turn command surface"
        finalized_note["candidate_points"] = [
            "reference mature companion projects for boundary matrix and minimal directory layout",
            "treat finalize-turn as the stable seam for turn-end integration",
        ]
        finalized_result = finalize_turn_artifacts(
            finalized_note,
            tmp_root / "turn.finalize.note.json",
            tmp_root / "turn.finalize.carryforward.json",
            history_path=note_history_path,
            carryforward_log_path=carryforward_log_path,
            carryforward_store_path=carryforward_store_path,
        )
        if finalized_result["note"]["scope"] != "project":
            raise RuntimeError(f"finalize-turn should preserve note promotion: {finalized_result}")
        if finalized_result["carry_forward_candidate"]["decision"] != "carry-forward":
            raise RuntimeError(f"finalize-turn should derive durable carry-forward context: {finalized_result}")
        if finalized_result["carry_forward_record"]["status"] != "created":
            raise RuntimeError(f"finalize-turn should create a durable carry-forward record: {finalized_result}")

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

        method_note = deepcopy(example_note)
        method_note["note_id"] = "note_method_001"
        method_note["turn_id"] = "turn_method_001"
        method_note["scope"] = "project"
        method_note["retention"] = "medium"
        method_note["goal"] = "把成熟的验收和解题经验沉淀成公开 method hooks"
        method_note["actions"] = "整理验收 rubric、review pattern 和 problem-solving playbook"
        method_note["result"] = "后续同类任务先复用这套 method pattern"
        method_note["candidate_points"] = [
            "把成熟的验收 rubric 和解题 playbook 固化成 method hooks",
            "遇到类似问题先挂这套 review pattern 和思维模型",
        ]
        method_note_path = tmp_root / "turn.method.note.json"
        write_note_artifact(
            method_note,
            method_note_path,
            history_path=note_history_path,
        )
        method_carryforward_result = write_carryforward_candidate_artifact(
            method_note_path,
            tmp_root / "turn.method.carryforward.json",
            history_path=note_history_path,
            carryforward_log_path=carryforward_log_path,
        )
        if method_carryforward_result["decision"] != "carry-forward":
            raise RuntimeError(f"method pattern note should enter carry-forward context: {method_carryforward_result}")
        if method_carryforward_result["candidate_type"] != "method-pattern":
            raise RuntimeError(f"unexpected carry-forward type for method pattern: {method_carryforward_result}")
        method_record_result = consolidate_carryforward_candidate_artifact(
            tmp_root / "turn.method.carryforward.json",
            carryforward_store_path,
        )
        if method_record_result["status"] != "created":
            raise RuntimeError(f"method pattern should create a durable carry-forward record: {method_record_result}")

        method_note_repeat = deepcopy(method_note)
        method_note_repeat["note_id"] = "note_method_002"
        method_note_repeat["turn_id"] = "turn_method_002"
        method_repeat_note_path = tmp_root / "turn.method.repeat.note.json"
        write_note_artifact(
            method_note_repeat,
            method_repeat_note_path,
            history_path=note_history_path,
        )
        write_carryforward_candidate_artifact(
            method_repeat_note_path,
            tmp_root / "turn.method.repeat.carryforward.json",
            history_path=note_history_path,
            carryforward_log_path=carryforward_log_path,
        )
        method_record_update = consolidate_carryforward_candidate_artifact(
            tmp_root / "turn.method.repeat.carryforward.json",
            carryforward_store_path,
        )
        if method_record_update["status"] != "updated":
            raise RuntimeError(f"repeated method record should update the durable store: {method_record_update}")
        if method_record_update["reinforcement_count"] < 2:
            raise RuntimeError(f"method carry-forward record should reinforce after a second turn: {method_record_update}")

        mount_note = deepcopy(example_note)
        mount_note["note_id"] = "note_mount_001"
        mount_note["turn_id"] = "turn_mount_001"
        mount_note["scope"] = "project"
        mount_note["retention"] = "medium"
        mount_note["goal"] = "把常用底层能力挂件收束成公开 capability mounts"
        mount_note["actions"] = "约定 search、compare 和 validate helper surfaces 作为默认挂载"
        mount_note["result"] = "同类任务开始时先挂这套 capability mount rule"
        mount_note["candidate_points"] = [
            "常用底层能力挂件应作为默认 capability mount 自动挂载",
            "进入同类任务先挂 search、compare 和 validate 能力面",
        ]
        mount_note_path = tmp_root / "turn.mount.note.json"
        write_note_artifact(
            mount_note,
            mount_note_path,
            history_path=note_history_path,
        )
        mount_carryforward_result = write_carryforward_candidate_artifact(
            mount_note_path,
            tmp_root / "turn.mount.carryforward.json",
            history_path=note_history_path,
            carryforward_log_path=carryforward_log_path,
        )
        if mount_carryforward_result["decision"] != "carry-forward":
            raise RuntimeError(f"capability mount note should enter carry-forward context: {mount_carryforward_result}")
        if mount_carryforward_result["candidate_type"] != "capability-mount-rule":
            raise RuntimeError(f"unexpected carry-forward type for capability mount rule: {mount_carryforward_result}")
        mount_record_result = consolidate_carryforward_candidate_artifact(
            tmp_root / "turn.mount.carryforward.json",
            carryforward_store_path,
        )
        if mount_record_result["status"] != "created":
            raise RuntimeError(f"capability mount should create a durable carry-forward record: {mount_record_result}")

        recall_query = {
            "turn_id": "turn_recall_001",
            "user_goal": "shape a new companion design and attach default helper surfaces",
            "action_focus": "pick the review method first, then attach default search, validate, and compare helpers",
            "hard_constraints": ["keep boundaries and review criteria explicit"],
        }
        write_json(tmp_root / "turn.carryforward.recall.input.json", recall_query)
        recall_plan = build_carryforward_recall_plan(recall_query, carryforward_store_path)
        write_json(carryforward_recall_path, recall_plan)
        selected_types = {item["candidate_type"] for item in recall_plan["selected_records"]}
        if "method-pattern" not in selected_types:
            raise RuntimeError(f"recall plan should surface method-pattern records: {recall_plan}")
        if "capability-mount-rule" not in selected_types:
            raise RuntimeError(f"recall plan should surface capability-mount-rule records: {recall_plan}")
        if not recall_plan["recommended_method_hooks"]:
            raise RuntimeError(f"recall plan should recommend method hooks: {recall_plan}")
        if not recall_plan["recommended_capability_mounts"]:
            raise RuntimeError(f"recall plan should recommend capability mounts: {recall_plan}")

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
        if validate_path_against_schema(carryforward_path, CARRYFORWARD_SCHEMA_PATH):
            raise RuntimeError("generated carry-forward candidate failed schema validation")
        if validate_path_against_schema(carryforward_store_path, CARRYFORWARD_RECORD_SCHEMA_PATH):
            raise RuntimeError("generated carry-forward store failed schema validation")
        if validate_path_against_schema(carryforward_recall_path, CARRYFORWARD_RECALL_SCHEMA_PATH):
            raise RuntimeError("generated carry-forward recall plan failed schema validation")
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
            "carryforward_log_records": len(load_jsonl(carryforward_log_path)),
            "carryforward_store_records": len(load_jsonl(carryforward_store_path)),
            "guardrail_events": len(load_jsonl(guardrails_events_path)),
            "mutation_guardrail_decision": mutation_result["decision"],
            "duplicate_guardrail_decision": duplicate_second["decision"],
            "carryforward_example_type": example_carryforward_candidate["candidate_type"],
            "carryforward_record_example_type": example_carryforward_record["candidate_type"],
            "carryforward_recall_selected": len(example_carryforward_recall["selected_records"]),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
