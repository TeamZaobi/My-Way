from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from schema_utils import (
    MYWAY_ROOT,
    RUNTIME_ROOT,
    append_jsonl,
    bucket_path,
    canonical_json,
    load_json,
    load_jsonl,
    normalize_text,
    now_iso,
    sha256_text,
    validate_instance,
    write_json,
)


EVENT_SCHEMA_PATH = RUNTIME_ROOT / "schemas" / "turn-event.schema.json"
NOTE_SCHEMA_PATH = RUNTIME_ROOT / "schemas" / "turn-note.schema.json"
PACKET_SCHEMA_PATH = RUNTIME_ROOT / "schemas" / "reflection-exchange-packet.schema.json"
TRIAGE_AUDIT_SCHEMA_PATH = RUNTIME_ROOT / "bridge" / "reflection-triage-audit.schema.json"

SCOPE_ORDER = {
    "session": 0,
    "project": 1,
    "global-candidate": 2,
}

GLOBAL_SIGNAL_TOKENS = (
    "reference-system",
    "codex",
    "claude-code",
    "antigravity",
    "cross-host",
    "跨宿主",
)


def _load_schema(path: Path) -> dict[str, Any]:
    return load_json(path)


def _validate_or_raise(instance: dict[str, Any], schema_path: Path, label: str) -> None:
    errors = validate_instance(instance, _load_schema(schema_path))
    if errors:
        raise ValueError(f"{label} validation failed: {'; '.join(errors)}")


def build_event_hash(event: dict[str, Any]) -> str:
    signature = {
        "turn_id": event.get("turn_id", ""),
        "phase": event.get("phase", ""),
        "source": event.get("source", ""),
        "source_tag": event.get("source_tag", ""),
        "payload_summary": normalize_text(event.get("payload_summary", "")),
        "related_paths": sorted(bucket_path(path) for path in event.get("related_paths", [])),
    }
    return sha256_text(canonical_json(signature))


def append_event_artifact(event: dict[str, Any], events_path: Path) -> dict[str, Any]:
    record = dict(event)
    record.setdefault("schema_version", "v0.1")
    record.setdefault("event_hash", build_event_hash(record))
    record.setdefault("event_id", f"evt_{record['event_hash'][:12]}")
    _validate_or_raise(record, EVENT_SCHEMA_PATH, "turn event")

    for existing in load_jsonl(events_path):
        if existing.get("event_hash") == record["event_hash"]:
            return {
                "status": "deduped",
                "event_id": existing.get("event_id"),
                "event_hash": record["event_hash"],
                "events_path": str(events_path),
            }

    append_jsonl(events_path, record)
    return {
        "status": "written",
        "event_id": record["event_id"],
        "event_hash": record["event_hash"],
        "events_path": str(events_path),
    }


def _load_note_history(history_path: Path | None) -> list[dict[str, Any]]:
    if history_path is None or not history_path.exists():
        return []
    if history_path.suffix == ".jsonl":
        return [record for record in load_jsonl(history_path) if isinstance(record, dict)]
    payload = load_json(history_path)
    if isinstance(payload, list):
        return [record for record in payload if isinstance(record, dict)]
    if isinstance(payload, dict):
        return [payload]
    return []


def _stable_note_points(note: dict[str, Any]) -> set[str]:
    points = {
        normalize_text(point)
        for point in note.get("candidate_points", [])
        if isinstance(point, str) and point.strip()
    }
    if not points and note.get("goal"):
        points.add(normalize_text(note["goal"]))
    return points


def _count_prior_note_hits(note: dict[str, Any], history: list[dict[str, Any]]) -> int:
    current_points = _stable_note_points(note)
    if not current_points:
        return 0
    hits = 0
    for prior in history:
        if current_points & _stable_note_points(prior):
            hits += 1
    return hits


def _note_has_global_signal(note: dict[str, Any]) -> bool:
    text = normalize_text(
        " ".join(
            [
                note.get("goal", ""),
                note.get("actions", ""),
                note.get("result", ""),
                *note.get("candidate_points", []),
            ]
        )
    )
    return any(token in text for token in GLOBAL_SIGNAL_TOKENS)


def _max_allowed_scope(note: dict[str, Any], repeat_hits: int) -> str:
    if repeat_hits >= 3 and note.get("candidate_points") and (
        note.get("retention") == "review-required" or _note_has_global_signal(note)
    ):
        return "global-candidate"
    if repeat_hits >= 2 or note.get("retention") in {"medium", "review-required"}:
        return "project"
    return "session"


def write_note_artifact(
    note: dict[str, Any],
    note_path: Path,
    history_path: Path | None = None,
    strict_scope: bool = True,
) -> dict[str, Any]:
    record = dict(note)
    record.setdefault("schema_version", "v0.1")
    if not record.get("note_id"):
        note_hash = sha256_text(
            canonical_json(
                {
                    "turn_id": record.get("turn_id", ""),
                    "goal": normalize_text(record.get("goal", "")),
                    "actions": normalize_text(record.get("actions", "")),
                    "result": normalize_text(record.get("result", "")),
                }
            )
        )
        record["note_id"] = f"note_{note_hash[:12]}"

    history = _load_note_history(history_path)
    if history_path is not None and any(prior.get("turn_id") == record.get("turn_id") for prior in history):
        raise ValueError(f"note history already contains turn_id={record.get('turn_id')!r}")

    repeat_hits = _count_prior_note_hits(record, history)
    allowed_scope = _max_allowed_scope(record, repeat_hits)
    requested_scope = record.get("scope")
    if requested_scope not in SCOPE_ORDER:
        raise ValueError(f"unknown note scope: {requested_scope!r}")
    if SCOPE_ORDER[requested_scope] > SCOPE_ORDER[allowed_scope]:
        message = f"scope promotion {requested_scope!r} exceeds allowed {allowed_scope!r}"
        if strict_scope:
            raise ValueError(message)
        record["scope"] = allowed_scope

    _validate_or_raise(record, NOTE_SCHEMA_PATH, "turn note")
    write_json(note_path, record)
    history_appended = False
    if history_path is not None:
        append_jsonl(history_path, record)
        history_appended = True

    return {
        "status": "written",
        "note_id": record["note_id"],
        "scope": record["scope"],
        "allowed_scope": allowed_scope,
        "repeat_hits": repeat_hits,
        "note_path": str(note_path),
        "history_appended": history_appended,
    }


def default_follow_up_owner(packet: dict[str, Any]) -> str:
    if packet.get("candidate_action") != "upstream-candidate":
        return "my-way"
    if packet.get("material_type") == "skill_candidate" or packet.get("layer") == "implementation":
        return "lifecycle-owner"

    text = normalize_text(
        " ".join(
            [
                packet.get("summary", ""),
                packet.get("local_decision_reason", ""),
                *packet.get("evidence", []),
            ]
        )
    )
    governance_tokens = (
        "governance",
        "true source",
        "write boundary",
        "scope drift",
        "boundary",
        "治理",
        "真源",
        "写权",
        "install",
        "register",
        "repair",
        "audit",
    )
    if any(token in text for token in governance_tokens):
        return "governance-owner"
    return "my-way"


def write_packet_artifact(packet: dict[str, Any], packet_path: Path) -> dict[str, Any]:
    record = dict(packet)
    record.setdefault("schema_version", "v0.1")
    if not record.get("packet_id"):
        packet_hash = sha256_text(
            canonical_json(
                {
                    "summary": normalize_text(record.get("summary", "")),
                    "layer": record.get("layer", ""),
                    "candidate_action": record.get("candidate_action", ""),
                }
            )
        )
        record["packet_id"] = f"packet_{packet_hash[:12]}"
    record.setdefault("follow_up_owner", default_follow_up_owner(record))
    _validate_or_raise(record, PACKET_SCHEMA_PATH, "reflection exchange packet")
    write_json(packet_path, record)
    return {
        "status": "written",
        "packet_id": record["packet_id"],
        "follow_up_owner": record.get("follow_up_owner"),
        "packet_path": str(packet_path),
    }


def _resolve_turn_id(
    turn_id: str | None,
    events_path: Path | None,
    note_path: Path | None,
) -> str:
    if turn_id:
        return turn_id
    if note_path and note_path.exists():
        note = load_json(note_path)
        if isinstance(note, dict) and note.get("turn_id"):
            return note["turn_id"]
    if events_path and events_path.exists():
        events = load_jsonl(events_path)
        if events and events[-1].get("turn_id"):
            return events[-1]["turn_id"]
    raise ValueError("turn_id is required when no note or events artifact can provide it")


def _build_replay_refs(packet_path: Path, events_path: Path | None, note_path: Path | None) -> list[str]:
    refs = [str(packet_path)]
    if events_path and events_path.exists():
        refs.append(str(events_path))
    if note_path and note_path.exists():
        refs.append(str(note_path))
    return refs


def append_triage_audit(
    packet_path: Path,
    audit_path: Path,
    turn_id: str | None = None,
    events_path: Path | None = None,
    note_path: Path | None = None,
    reason: str | None = None,
    follow_up_owner: str | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    packet = load_json(packet_path)
    if not isinstance(packet, dict):
        raise ValueError("packet artifact must be a JSON object")
    _validate_or_raise(packet, PACKET_SCHEMA_PATH, "reflection exchange packet")

    resolved_turn_id = _resolve_turn_id(turn_id, events_path, note_path)
    replay_refs = _build_replay_refs(packet_path, events_path, note_path)
    resolved_decision = decision or packet.get("candidate_action")
    resolved_owner = follow_up_owner or packet.get("follow_up_owner") or default_follow_up_owner(packet)
    resolved_reason = reason or packet.get("local_decision_reason") or "Triage recorded from exchange packet."

    if len(replay_refs) < 3:
        resolved_decision = "bypass"
        resolved_owner = "my-way"
        resolved_reason = "Replay references are incomplete; keep the packet recorded but do not promote it."

    review_required = resolved_decision == "upstream-candidate" or resolved_owner != "my-way"
    review_status = "pending" if review_required else "not-needed"
    audit_hash = sha256_text(
        canonical_json(
            {
                "turn_id": resolved_turn_id,
                "packet_id": packet["packet_id"],
                "decision": resolved_decision,
            }
        )
    )
    audit_record = {
        "schema_version": "v0.1",
        "audit_id": f"audit_{audit_hash[:12]}",
        "turn_id": resolved_turn_id,
        "packet_id": packet["packet_id"],
        "timestamp": now_iso(),
        "material_source": packet["source_system"],
        "layer": packet["layer"],
        "decision": resolved_decision,
        "reason": resolved_reason,
        "follow_up_owner": resolved_owner,
        "evidence_refs": packet["evidence"],
        "replay_refs": replay_refs,
        "review_required": review_required,
        "review_status": review_status,
    }
    _validate_or_raise(audit_record, TRIAGE_AUDIT_SCHEMA_PATH, "reflection triage audit")

    for existing in load_jsonl(audit_path):
        if existing.get("packet_id") == audit_record["packet_id"]:
            return {
                "status": "deduped",
                "audit_id": existing.get("audit_id"),
                "packet_id": audit_record["packet_id"],
                "audit_path": str(audit_path),
            }

    append_jsonl(audit_path, audit_record)
    return {
        "status": "written",
        "audit_id": audit_record["audit_id"],
        "decision": audit_record["decision"],
        "follow_up_owner": audit_record["follow_up_owner"],
        "audit_path": str(audit_path),
    }


def _load_input_json(path: str) -> dict[str, Any]:
    payload = load_json(Path(path))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="My-Way runtime artifact helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    event_parser = subparsers.add_parser("append-event", help="append a turn event with event_hash dedupe")
    event_parser.add_argument("--input-json", required=True)
    event_parser.add_argument(
        "--events-path",
        default=str(RUNTIME_ROOT / "examples" / "turn.events.jsonl"),
    )

    note_parser = subparsers.add_parser("write-note", help="write turn.note.json with scope checks")
    note_parser.add_argument("--input-json", required=True)
    note_parser.add_argument(
        "--note-path",
        default=str(RUNTIME_ROOT / "examples" / "turn.note.json"),
    )
    note_parser.add_argument("--history-path")
    note_parser.add_argument("--no-strict-scope", action="store_true")

    packet_parser = subparsers.add_parser("write-packet", help="write reflection exchange packet")
    packet_parser.add_argument("--input-json", required=True)
    packet_parser.add_argument(
        "--packet-path",
        default=str(RUNTIME_ROOT / "examples" / "reflection.exchange.packet.json"),
    )

    triage_parser = subparsers.add_parser("triage-packet", help="record a reflection triage audit line")
    triage_parser.add_argument(
        "--packet-path",
        default=str(RUNTIME_ROOT / "examples" / "reflection.exchange.packet.json"),
    )
    triage_parser.add_argument(
        "--audit-path",
        default=str(RUNTIME_ROOT / "bridge" / "examples" / "reflection-triage-audit.jsonl"),
    )
    triage_parser.add_argument("--turn-id")
    triage_parser.add_argument("--events-path")
    triage_parser.add_argument("--note-path")
    triage_parser.add_argument("--reason")
    triage_parser.add_argument("--follow-up-owner")
    triage_parser.add_argument("--decision")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "append-event":
        result = append_event_artifact(_load_input_json(args.input_json), Path(args.events_path))
        _print_json(result)
        return 0

    if args.command == "write-note":
        result = write_note_artifact(
            _load_input_json(args.input_json),
            Path(args.note_path),
            history_path=Path(args.history_path) if args.history_path else None,
            strict_scope=not args.no_strict_scope,
        )
        _print_json(result)
        return 0

    if args.command == "write-packet":
        result = write_packet_artifact(_load_input_json(args.input_json), Path(args.packet_path))
        _print_json(result)
        return 0

    if args.command == "triage-packet":
        result = append_triage_audit(
            Path(args.packet_path),
            Path(args.audit_path),
            turn_id=args.turn_id,
            events_path=Path(args.events_path) if args.events_path else None,
            note_path=Path(args.note_path) if args.note_path else None,
            reason=args.reason,
            follow_up_owner=args.follow_up_owner,
            decision=args.decision,
        )
        _print_json(result)
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
