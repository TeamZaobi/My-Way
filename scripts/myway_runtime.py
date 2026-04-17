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
CARRYFORWARD_SCHEMA_PATH = RUNTIME_ROOT / "schemas" / "turn-carryforward-candidate.schema.json"
CARRYFORWARD_RECORD_SCHEMA_PATH = RUNTIME_ROOT / "schemas" / "carryforward-record.schema.json"
CARRYFORWARD_RECALL_SCHEMA_PATH = RUNTIME_ROOT / "schemas" / "turn-carryforward-recall.schema.json"
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

EPHEMERAL_SIGNAL_TOKENS = (
    "this turn",
    "one-off",
    "temporary",
    "临时",
    "一次性",
    "本轮",
    "当前对话",
    "临时修补",
)

PREFERENCE_SIGNAL_TOKENS = (
    "prefer",
    "preferred",
    "default",
    "默认",
    "偏好",
    "习惯",
    "优先",
    "不要",
)

CONSTRAINT_SIGNAL_TOKENS = (
    "must",
    "must not",
    "cannot",
    "禁止",
    "必须",
    "不能",
    "guardrail",
    "constraint",
    "约束",
)

METHOD_SIGNAL_TOKENS = (
    "rubric",
    "playbook",
    "heuristic",
    "mental model",
    "acceptance pattern",
    "review pattern",
    "验收",
    "审核",
    "审查",
    "解题",
    "思维模型",
    "反模式",
)

CAPABILITY_MOUNT_SIGNAL_TOKENS = (
    "capability mount",
    "capability mounts",
    "mount rule",
    "tool mount",
    "能力挂件",
    "能力挂载",
    "默认挂载",
    "默认加载",
    "挂件",
    "能力面",
)

WORKFLOW_SIGNAL_TOKENS = (
    "workflow",
    "cutover",
    "prelude",
    "postlude",
    "流程",
    "接缝",
    "hook",
)

ROUTING_SIGNAL_TOKENS = (
    "authority",
    "owner",
    "routing",
    "route",
    "handoff",
    "boundary",
    "governance-authority",
    "lifecycle-authority",
    "governance-owner",
    "lifecycle-owner",
    "写权",
    "真源",
    "治理",
    "边界",
    "转交",
)

CONFIDENCE_RANK = {
    "low": 0,
    "medium": 1,
    "high": 2,
}

STABILITY_RANK = {
    "turn-signal": 0,
    "repeat-observed": 1,
    "durable": 2,
}

RECALL_TAG_TOKENS = (
    "evolve",
    "prelude",
    "postlude",
    "cutover",
    "workflow",
    "hook",
    "验收",
    "审核",
    "审查",
    "rubric",
    "playbook",
    "思维模型",
    "反模式",
    "capability mount",
    "能力挂件",
    "能力挂载",
    "默认挂载",
    "能力面",
    "authority",
    "owner",
    "routing",
    "handoff",
    "boundary",
    "边界",
    "治理",
    "真源",
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
    text = _note_signal_text(note)
    return any(token in text for token in GLOBAL_SIGNAL_TOKENS)


def _note_signal_text(note: dict[str, Any]) -> str:
    return normalize_text(
        " ".join(
            [
                note.get("goal", ""),
                note.get("actions", ""),
                note.get("result", ""),
                *note.get("candidate_points", []),
            ]
        )
    )


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


def _carryforward_evidence(note: dict[str, Any]) -> list[str]:
    evidence: list[str] = []
    for point in note.get("candidate_points", []):
        if isinstance(point, str) and point.strip():
            evidence.append(point.strip())
    for field in ("goal", "result"):
        value = note.get(field)
        if isinstance(value, str) and value.strip():
            evidence.append(value.strip())

    deduped: list[str] = []
    for item in evidence:
        if item not in deduped:
            deduped.append(item)
    return deduped[:3]


def _dedupe_strings(items: list[str], limit: int | None = None) -> list[str]:
    deduped: list[str] = []
    for item in items:
        if not isinstance(item, str):
            continue
        normalized = item.strip()
        if not normalized or normalized in deduped:
            continue
        deduped.append(normalized)
        if limit is not None and len(deduped) >= limit:
            break
    return deduped


def _ranked_max(values: list[str], rank_map: dict[str, int], default: str) -> str:
    best = default
    best_rank = rank_map.get(default, -1)
    for value in values:
        rank = rank_map.get(value, -1)
        if rank > best_rank:
            best = value
            best_rank = rank
    return best


def _carryforward_category_tag(candidate_type: str) -> str:
    return {
        "preference": "preference",
        "constraint": "constraint",
        "method-pattern": "method",
        "capability-mount-rule": "mount",
        "workflow-pattern": "workflow",
        "routing-rule": "routing",
        "external-pattern": "external",
        "project-context": "project",
    }.get(candidate_type, "general")


def _preferred_injection_slot(candidate_type: str) -> str:
    return {
        "method-pattern": "method-hooks",
        "capability-mount-rule": "capability-mounts",
        "constraint": "hard-constraints",
        "routing-rule": "hard-constraints",
        "preference": "carry-over",
        "workflow-pattern": "carry-over",
        "external-pattern": "carry-over",
        "project-context": "carry-over",
    }.get(candidate_type, "carry-over")


def _carryforward_recall_tags(candidate_type: str, candidate_text: str, evidence: list[str]) -> list[str]:
    text = normalize_text(" ".join([candidate_text, *evidence]))
    tags = [_carryforward_category_tag(candidate_type), _preferred_injection_slot(candidate_type)]
    for token in RECALL_TAG_TOKENS:
        if token in text and token not in tags:
            tags.append(token)
    return _dedupe_strings(tags, limit=8)


def _carryforward_key(candidate_type: str, candidate_text: str) -> str:
    candidate_hash = sha256_text(
        canonical_json(
            {
                "candidate_type": candidate_type,
                "candidate_text": normalize_text(candidate_text),
            }
        )
    )
    return f"ckey_{candidate_hash[:12]}"


def _contains_external_pattern_signal(text: str) -> bool:
    if "evolve" in text or "inspired by" in text or "成熟项目" in text or "前车" in text:
        return True
    if "参考" in text and ("经验" in text or "模式" in text or "项目" in text):
        return True
    if "边界矩阵" in text or "最小目录结构" in text or "cutover" in text:
        return True
    return False


def _contains_method_signal(text: str) -> bool:
    if any(token in text for token in METHOD_SIGNAL_TOKENS):
        return True
    review_tokens = ("验收", "审核", "review")
    method_tokens = ("rubric", "playbook", "思维模型", "反模式", "方法")
    return any(token in text for token in review_tokens) and any(token in text for token in method_tokens)


def _contains_capability_mount_signal(text: str) -> bool:
    if any(token in text for token in CAPABILITY_MOUNT_SIGNAL_TOKENS):
        return True
    mount_tokens = ("挂载", "mount")
    capability_tokens = ("能力", "capability", "工具", "tool", "挂件")
    return any(token in text for token in mount_tokens) and any(token in text for token in capability_tokens)


def _classify_carryforward_type(note: dict[str, Any], repeat_hits: int) -> str:
    text = _note_signal_text(note)
    if _contains_external_pattern_signal(text):
        return "external-pattern"
    if _contains_capability_mount_signal(text):
        return "capability-mount-rule"
    if any(token in text for token in ROUTING_SIGNAL_TOKENS):
        return "routing-rule"
    if _contains_method_signal(text):
        return "method-pattern"
    if any(token in text for token in CONSTRAINT_SIGNAL_TOKENS):
        return "constraint"
    if any(token in text for token in PREFERENCE_SIGNAL_TOKENS):
        return "preference"
    if any(token in text for token in WORKFLOW_SIGNAL_TOKENS):
        return "workflow-pattern"
    if note.get("scope") in {"project", "global-candidate"} or repeat_hits >= 2:
        return "project-context"
    return "none"


def _carryforward_stability(note: dict[str, Any], repeat_hits: int) -> str:
    if note.get("scope") == "global-candidate" or note.get("retention") == "review-required":
        return "durable"
    if note.get("scope") == "project" or note.get("retention") == "medium" or repeat_hits >= 1:
        return "repeat-observed"
    return "turn-signal"


def _carryforward_confidence(decision: str, candidate_type: str, stability: str, repeat_hits: int) -> str:
    if decision != "carry-forward":
        return "low"
    if candidate_type in {"routing-rule", "external-pattern", "method-pattern", "capability-mount-rule"}:
        return "high"
    if stability == "durable" or repeat_hits >= 2:
        return "high"
    if stability == "repeat-observed":
        return "medium"
    return "medium"


def _carryforward_text(note: dict[str, Any], decision: str) -> str:
    evidence = _carryforward_evidence(note)
    if evidence:
        return evidence[0]
    if decision == "carry-forward":
        return note.get("goal") or note.get("result") or "Promote durable carry-forward context."
    return "No durable carry-forward candidate promoted from this turn."


def _carryforward_rationale(
    note: dict[str, Any],
    decision: str,
    candidate_type: str,
    stability: str,
    is_ephemeral: bool,
) -> str:
    if decision == "skip":
        if is_ephemeral:
            return "Signals in this note look turn-local or temporary, so they should remain in Postlude only."
        return "This note does not yet show a durable, reusable pattern worth promoting as carry-forward context."

    type_labels = {
        "preference": "stable preference",
        "constraint": "durable constraint",
        "method-pattern": "reusable method pattern",
        "capability-mount-rule": "reusable capability mount rule",
        "workflow-pattern": "reusable workflow pattern",
        "routing-rule": "reusable authority routing rule",
        "external-pattern": "reusable external project pattern",
        "project-context": "durable project context",
    }
    return (
        f"This note contains a {type_labels.get(candidate_type, 'durable signal')} "
        f"with {stability} strength, so it should be promoted as carry-forward context."
    )


def build_carryforward_candidate(
    note: dict[str, Any],
    history_path: Path | None = None,
) -> dict[str, Any]:
    history = [
        prior
        for prior in _load_note_history(history_path)
        if prior.get("turn_id") != note.get("turn_id")
    ]
    repeat_hits = _count_prior_note_hits(note, history)
    candidate_type = _classify_carryforward_type(note, repeat_hits)
    stability = _carryforward_stability(note, repeat_hits)
    text = _note_signal_text(note)
    is_ephemeral = any(token in text for token in EPHEMERAL_SIGNAL_TOKENS)

    if candidate_type == "none" or is_ephemeral:
        decision = "skip"
    elif candidate_type in {
        "preference",
        "constraint",
        "method-pattern",
        "capability-mount-rule",
        "routing-rule",
        "external-pattern",
    }:
        decision = "carry-forward"
    elif candidate_type in {"workflow-pattern", "project-context"} and stability != "turn-signal":
        decision = "carry-forward"
    else:
        decision = "skip"

    candidate_text = _carryforward_text(note, decision)
    candidate_hash = sha256_text(
        canonical_json(
            {
                "turn_id": note.get("turn_id", ""),
                "candidate_type": candidate_type,
                "candidate_text": normalize_text(candidate_text),
            }
        )
    )
    record = {
        "schema_version": "v0.1",
        "candidate_id": f"carry_{candidate_hash[:12]}",
        "turn_id": note["turn_id"],
        "source_note_id": note["note_id"],
        "source_scope": note["scope"],
        "decision": decision,
        "candidate_type": candidate_type,
        "candidate_text": candidate_text,
        "rationale": _carryforward_rationale(note, decision, candidate_type, stability, is_ephemeral),
        "evidence": _carryforward_evidence(note),
        "confidence": _carryforward_confidence(decision, candidate_type, stability, repeat_hits),
        "stability": stability,
        "write_target": "carry-forward" if decision == "carry-forward" else "none",
    }
    _validate_or_raise(record, CARRYFORWARD_SCHEMA_PATH, "turn carry-forward candidate")
    return record


def _append_carryforward_log(record: dict[str, Any], carryforward_log_path: Path) -> bool:
    for existing in load_jsonl(carryforward_log_path):
        if existing.get("candidate_id") == record["candidate_id"] or existing.get("turn_id") == record["turn_id"]:
            return False
    append_jsonl(carryforward_log_path, record)
    return True


def _load_carryforward_records(store_path: Path) -> list[dict[str, Any]]:
    if not store_path.exists():
        return []
    if store_path.suffix == ".json":
        payload = load_json(store_path)
        if isinstance(payload, list):
            return [record for record in payload if isinstance(record, dict)]
        return []
    return [record for record in load_jsonl(store_path) if isinstance(record, dict)]


def _write_carryforward_records(store_path: Path, records: list[dict[str, Any]]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    lines = "\n".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":")) for record in records
    )
    if lines:
        lines += "\n"
    store_path.write_text(lines, encoding="utf-8")


def _build_carryforward_record(candidate: dict[str, Any]) -> dict[str, Any]:
    timestamp = now_iso()
    record_key = _carryforward_key(candidate["candidate_type"], candidate["candidate_text"])
    record = {
        "schema_version": "v0.1",
        "record_id": f"carryrec_{record_key.split('_', 1)[1]}",
        "record_key": record_key,
        "candidate_type": candidate["candidate_type"],
        "candidate_text": candidate["candidate_text"],
        "status": "active",
        "preferred_injection_slot": _preferred_injection_slot(candidate["candidate_type"]),
        "recall_tags": _carryforward_recall_tags(
            candidate["candidate_type"],
            candidate["candidate_text"],
            candidate["evidence"],
        ),
        "source_scopes": [candidate["source_scope"]],
        "source_turn_ids": [candidate["turn_id"]],
        "source_note_ids": [candidate["source_note_id"]],
        "evidence": _dedupe_strings(candidate["evidence"], limit=5),
        "confidence": candidate["confidence"],
        "stability": candidate["stability"],
        "reinforcement_count": 1,
        "first_seen_at": timestamp,
        "last_seen_at": timestamp,
    }
    _validate_or_raise(record, CARRYFORWARD_RECORD_SCHEMA_PATH, "carry-forward record")
    return record


def consolidate_carryforward_candidate_artifact(
    candidate_path: Path,
    store_path: Path,
) -> dict[str, Any]:
    candidate = load_json(candidate_path)
    if not isinstance(candidate, dict):
        raise ValueError("carry-forward candidate artifact must be a JSON object")
    _validate_or_raise(candidate, CARRYFORWARD_SCHEMA_PATH, "turn carry-forward candidate")

    if candidate["decision"] != "carry-forward":
        return {
            "status": "skipped",
            "decision": candidate["decision"],
            "candidate_type": candidate["candidate_type"],
            "store_path": str(store_path),
        }

    records = _load_carryforward_records(store_path)
    for record in records:
        _validate_or_raise(record, CARRYFORWARD_RECORD_SCHEMA_PATH, "carry-forward record")

    record_key = _carryforward_key(candidate["candidate_type"], candidate["candidate_text"])
    for record in records:
        if record.get("record_key") != record_key or record.get("status") != "active":
            continue
        if candidate["turn_id"] in record.get("source_turn_ids", []):
            return {
                "status": "deduped",
                "record_id": record["record_id"],
                "record_key": record["record_key"],
                "candidate_type": record["candidate_type"],
                "reinforcement_count": record["reinforcement_count"],
                "store_path": str(store_path),
            }

        if len(candidate["candidate_text"]) >= len(record.get("candidate_text", "")):
            record["candidate_text"] = candidate["candidate_text"]
        record["source_scopes"] = _dedupe_strings(
            [*record.get("source_scopes", []), candidate["source_scope"]],
            limit=3,
        )
        record["source_turn_ids"] = _dedupe_strings(
            [*record.get("source_turn_ids", []), candidate["turn_id"]],
        )
        record["source_note_ids"] = _dedupe_strings(
            [*record.get("source_note_ids", []), candidate["source_note_id"]],
        )
        record["evidence"] = _dedupe_strings(
            [*record.get("evidence", []), *candidate["evidence"]],
            limit=5,
        )
        record["confidence"] = _ranked_max(
            [record.get("confidence", "low"), candidate["confidence"]],
            CONFIDENCE_RANK,
            default="low",
        )
        record["stability"] = _ranked_max(
            [record.get("stability", "turn-signal"), candidate["stability"]],
            STABILITY_RANK,
            default="turn-signal",
        )
        record["reinforcement_count"] = max(
            int(record.get("reinforcement_count", 1)) + 1,
            len(record["source_turn_ids"]),
        )
        record["last_seen_at"] = now_iso()
        record["preferred_injection_slot"] = _preferred_injection_slot(record["candidate_type"])
        record["recall_tags"] = _carryforward_recall_tags(
            record["candidate_type"],
            record["candidate_text"],
            record["evidence"],
        )
        _validate_or_raise(record, CARRYFORWARD_RECORD_SCHEMA_PATH, "carry-forward record")
        _write_carryforward_records(store_path, records)
        return {
            "status": "updated",
            "record_id": record["record_id"],
            "record_key": record["record_key"],
            "candidate_type": record["candidate_type"],
            "reinforcement_count": record["reinforcement_count"],
            "store_path": str(store_path),
        }

    record = _build_carryforward_record(candidate)
    records.append(record)
    _write_carryforward_records(store_path, records)
    return {
        "status": "created",
        "record_id": record["record_id"],
        "record_key": record["record_key"],
        "candidate_type": record["candidate_type"],
        "reinforcement_count": record["reinforcement_count"],
        "store_path": str(store_path),
    }


def _carryforward_query_text(payload: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("user_goal", "action_focus", "result"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            values.append(value)
    for key in ("method_hooks", "capability_mounts", "hard_constraints", "context_points"):
        values.extend(
            item
            for item in payload.get(key, [])
            if isinstance(item, str) and item.strip()
        )
    return normalize_text(" ".join(values))


def _query_recall_tags(query_text: str) -> list[str]:
    tags: list[str] = []
    if _contains_method_signal(query_text) or any(
        token in query_text for token in ("方案", "审核", "验收", "问题", "解决", "review", "design", "plan")
    ):
        tags.append("method")
    if _contains_capability_mount_signal(query_text) or any(
        token in query_text
        for token in ("能力", "工具", "挂载", "mount", "搜索", "校验", "对比", "debug", "validate", "compare")
    ):
        tags.append("mount")
    if any(token in query_text for token in CONSTRAINT_SIGNAL_TOKENS) or "边界" in query_text:
        tags.append("constraint")
    if any(token in query_text for token in ROUTING_SIGNAL_TOKENS):
        tags.append("routing")
    if _contains_external_pattern_signal(query_text) or "参考" in query_text:
        tags.append("external")
    if any(token in query_text for token in WORKFLOW_SIGNAL_TOKENS):
        tags.append("workflow")
    if "项目" in query_text or "project" in query_text or "上下文" in query_text:
        tags.append("project")
    if any(token in query_text for token in PREFERENCE_SIGNAL_TOKENS):
        tags.append("preference")
    return _dedupe_strings(tags)


def _score_carryforward_record(record: dict[str, Any], query_text: str, query_tags: list[str]) -> tuple[int, str | None]:
    if record.get("status") != "active":
        return 0, None

    score = 0
    reasons: list[str] = []
    matched = False
    record_tags = [tag for tag in record.get("recall_tags", []) if isinstance(tag, str)]

    tag_hits = [tag for tag in record_tags if tag in query_tags or tag in query_text]
    if tag_hits:
        score += 2 * len(tag_hits)
        reasons.append(f"matched recall tags: {', '.join(tag_hits[:3])}")
        matched = True

    candidate_text = normalize_text(record.get("candidate_text", ""))
    if candidate_text and candidate_text in query_text:
        score += 4
        reasons.append("candidate text overlaps with the current turn")
        matched = True

    evidence_hits = 0
    for evidence in record.get("evidence", []):
        evidence_text = normalize_text(evidence)
        if evidence_text and evidence_text in query_text:
            evidence_hits += 1
    if evidence_hits:
        score += 2 * evidence_hits
        reasons.append("evidence from prior turns overlaps with the current turn")
        matched = True

    if record.get("candidate_type") in {"constraint", "routing-rule"}:
        score += 1
        reasons.append("guardrail-like carry-forward records stay slightly hot by default")

    if not matched and record.get("candidate_type") not in {"constraint", "routing-rule"}:
        return 0, None

    score += CONFIDENCE_RANK.get(record.get("confidence", "low"), 0)
    score += STABILITY_RANK.get(record.get("stability", "turn-signal"), 0)
    score += min(int(record.get("reinforcement_count", 1)), 3)
    return score, "; ".join(reasons) if reasons else "Matched durable carry-forward context."


def build_carryforward_recall_plan(
    query: dict[str, Any],
    store_path: Path,
) -> dict[str, Any]:
    records = _load_carryforward_records(store_path)
    active_records: list[dict[str, Any]] = []
    for record in records:
        _validate_or_raise(record, CARRYFORWARD_RECORD_SCHEMA_PATH, "carry-forward record")
        if record.get("status") == "active":
            active_records.append(record)

    query_text = _carryforward_query_text(query)
    if not query_text:
        raise ValueError("carry-forward recall query must include at least one non-empty text field")
    query_tags = _query_recall_tags(query_text)

    ranked: list[tuple[int, dict[str, Any], str]] = []
    for record in active_records:
        score, reason = _score_carryforward_record(record, query_text, query_tags)
        if score > 0 and reason:
            ranked.append((score, record, reason))
    ranked.sort(
        key=lambda item: (
            item[0],
            int(item[1].get("reinforcement_count", 1)),
            CONFIDENCE_RANK.get(item[1].get("confidence", "low"), 0),
        ),
        reverse=True,
    )

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()

    def add_record(record: dict[str, Any], score: int, reason: str) -> None:
        if record["record_id"] in selected_ids or len(selected) >= 5:
            return
        selected.append(
            {
                "record_id": record["record_id"],
                "candidate_type": record["candidate_type"],
                "candidate_text": record["candidate_text"],
                "injection_slot": record["preferred_injection_slot"],
                "reason": reason,
                "score": score,
            }
        )
        selected_ids.add(record["record_id"])

    for score, record, reason in ranked:
        add_record(record, score, reason)

    fallback_types = (
        "method-pattern",
        "capability-mount-rule",
        "constraint",
        "routing-rule",
    )
    for candidate_type in fallback_types:
        if len(selected) >= 5 or any(item["candidate_type"] == candidate_type for item in selected):
            continue
        candidates = [record for record in active_records if record["candidate_type"] == candidate_type]
        if not candidates:
            continue
        candidates.sort(
            key=lambda record: (
                int(record.get("reinforcement_count", 1)),
                CONFIDENCE_RANK.get(record.get("confidence", "low"), 0),
                STABILITY_RANK.get(record.get("stability", "turn-signal"), 0),
            ),
            reverse=True,
        )
        add_record(candidates[0], 1, "Fallback recall for a stable default carry-forward type.")

    plan_hash = sha256_text(
        canonical_json(
            {
                "query_text": query_text,
                "record_ids": [item["record_id"] for item in selected],
            }
        )
    )
    plan = {
        "schema_version": "v0.1",
        "plan_id": f"carryrecall_{plan_hash[:12]}",
        "query_turn_id": query.get("turn_id", f"turn_{plan_hash[:12]}"),
        "query_text": query_text,
        "store_record_count": len(active_records),
        "selected_records": selected,
        "recommended_method_hooks": _dedupe_strings(
            [item["candidate_text"] for item in selected if item["injection_slot"] == "method-hooks"],
            limit=3,
        ),
        "recommended_capability_mounts": _dedupe_strings(
            [item["candidate_text"] for item in selected if item["injection_slot"] == "capability-mounts"],
            limit=3,
        ),
        "recommended_hard_constraints": _dedupe_strings(
            [item["candidate_text"] for item in selected if item["injection_slot"] == "hard-constraints"],
            limit=3,
        ),
        "carry_over_points": _dedupe_strings(
            [item["candidate_text"] for item in selected if item["injection_slot"] == "carry-over"],
            limit=3,
        ),
    }
    _validate_or_raise(plan, CARRYFORWARD_RECALL_SCHEMA_PATH, "turn carry-forward recall")
    return plan


def write_carryforward_recall_artifact(
    input_json_path: Path,
    store_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    query = load_json(input_json_path)
    if not isinstance(query, dict):
        raise ValueError("carry-forward recall input must be a JSON object")
    plan = build_carryforward_recall_plan(query, store_path)
    write_json(output_path, plan)
    return {
        "status": "written",
        "plan_id": plan["plan_id"],
        "selected_count": len(plan["selected_records"]),
        "output_path": str(output_path),
    }


def write_carryforward_candidate_artifact(
    note_path: Path,
    candidate_path: Path,
    history_path: Path | None = None,
    carryforward_log_path: Path | None = None,
) -> dict[str, Any]:
    note = load_json(note_path)
    if not isinstance(note, dict):
        raise ValueError("note artifact must be a JSON object")
    _validate_or_raise(note, NOTE_SCHEMA_PATH, "turn note")

    record = build_carryforward_candidate(note, history_path=history_path)
    write_json(candidate_path, record)

    log_appended = False
    if carryforward_log_path is not None and record["decision"] == "carry-forward":
        log_appended = _append_carryforward_log(record, carryforward_log_path)

    return {
        "status": "written",
        "candidate_id": record["candidate_id"],
        "decision": record["decision"],
        "candidate_type": record["candidate_type"],
        "write_target": record["write_target"],
        "candidate_path": str(candidate_path),
        "log_appended": log_appended,
    }


def finalize_turn_artifacts(
    note: dict[str, Any],
    note_path: Path,
    candidate_path: Path,
    history_path: Path | None = None,
    carryforward_log_path: Path | None = None,
    carryforward_store_path: Path | None = None,
    strict_scope: bool = True,
) -> dict[str, Any]:
    note_result = write_note_artifact(
        note,
        note_path,
        history_path=history_path,
        strict_scope=strict_scope,
    )
    carryforward_result = write_carryforward_candidate_artifact(
        note_path,
        candidate_path,
        history_path=history_path,
        carryforward_log_path=carryforward_log_path,
    )
    carryforward_record_result = (
        consolidate_carryforward_candidate_artifact(candidate_path, carryforward_store_path)
        if carryforward_store_path is not None
        else {"status": "not-requested"}
    )
    return {
        "status": "written",
        "turn_id": note.get("turn_id"),
        "note": note_result,
        "carry_forward_candidate": carryforward_result,
        "carry_forward_record": carryforward_record_result,
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

    carryforward_parser = subparsers.add_parser(
        "write-carryforward-candidate",
        help="derive a durable carry-forward candidate from one turn note",
    )
    carryforward_parser.add_argument(
        "--note-path",
        default=str(RUNTIME_ROOT / "examples" / "turn.note.json"),
    )
    carryforward_parser.add_argument(
        "--candidate-path",
        default=str(RUNTIME_ROOT / "examples" / "turn.carryforward.candidate.json"),
    )
    carryforward_parser.add_argument("--history-path")
    carryforward_parser.add_argument("--carryforward-log-path")

    consolidate_parser = subparsers.add_parser(
        "consolidate-carryforward",
        help="upsert a promoted carry-forward candidate into the durable carry-forward store",
    )
    consolidate_parser.add_argument(
        "--candidate-path",
        default=str(RUNTIME_ROOT / "examples" / "turn.carryforward.candidate.json"),
    )
    consolidate_parser.add_argument(
        "--carryforward-store-path",
        default=str(RUNTIME_ROOT / "examples" / "carryforward.store.jsonl"),
    )

    recall_parser = subparsers.add_parser(
        "recall-carryforward",
        help="build a bounded recall plan from the durable carry-forward store",
    )
    recall_parser.add_argument("--input-json", required=True)
    recall_parser.add_argument(
        "--carryforward-store-path",
        default=str(RUNTIME_ROOT / "examples" / "carryforward.store.jsonl"),
    )
    recall_parser.add_argument(
        "--output-path",
        default=str(RUNTIME_ROOT / "examples" / "turn.carryforward.recall.json"),
    )

    finalize_parser = subparsers.add_parser(
        "finalize-turn",
        help="write turn.note.json and derive the durable carry-forward candidate sidecar",
    )
    finalize_parser.add_argument("--input-json", required=True)
    finalize_parser.add_argument(
        "--note-path",
        default=str(RUNTIME_ROOT / "examples" / "turn.note.json"),
    )
    finalize_parser.add_argument(
        "--candidate-path",
        default=str(RUNTIME_ROOT / "examples" / "turn.carryforward.candidate.json"),
    )
    finalize_parser.add_argument("--history-path")
    finalize_parser.add_argument("--carryforward-log-path")
    finalize_parser.add_argument("--carryforward-store-path")
    finalize_parser.add_argument("--no-strict-scope", action="store_true")

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

    if args.command == "write-carryforward-candidate":
        result = write_carryforward_candidate_artifact(
            Path(args.note_path),
            Path(args.candidate_path),
            history_path=Path(args.history_path) if args.history_path else None,
            carryforward_log_path=Path(args.carryforward_log_path) if args.carryforward_log_path else None,
        )
        _print_json(result)
        return 0

    if args.command == "consolidate-carryforward":
        result = consolidate_carryforward_candidate_artifact(
            Path(args.candidate_path),
            Path(args.carryforward_store_path),
        )
        _print_json(result)
        return 0

    if args.command == "recall-carryforward":
        result = write_carryforward_recall_artifact(
            Path(args.input_json),
            Path(args.carryforward_store_path),
            Path(args.output_path),
        )
        _print_json(result)
        return 0

    if args.command == "finalize-turn":
        result = finalize_turn_artifacts(
            _load_input_json(args.input_json),
            Path(args.note_path),
            Path(args.candidate_path),
            history_path=Path(args.history_path) if args.history_path else None,
            carryforward_log_path=Path(args.carryforward_log_path) if args.carryforward_log_path else None,
            carryforward_store_path=Path(args.carryforward_store_path) if args.carryforward_store_path else None,
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
