from __future__ import annotations

import argparse
import copy
import fnmatch
import json
from datetime import timedelta
from pathlib import Path
from typing import Any

from schema_utils import (
    RUNTIME_ROOT,
    append_jsonl,
    bucket_path,
    load_json,
    now_iso,
    normalize_text,
    parse_datetime,
    sha256_text,
    write_json,
)


DECISION_ORDER = {
    "pass": 0,
    "observe-only": 1,
    "review-required": 2,
    "block": 3,
}

ALLOWED_DECISIONS = set(DECISION_ORDER)
ALLOWED_IMPACTS = {"low", "medium", "high"}


def validate_contract_data(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_keys = [
        "schema_version",
        "dedupe_window_size",
        "loop_block_threshold",
        "recursion_block_threshold",
        "cooldown_turns",
        "cooldown_seconds",
        "protected_path_patterns",
        "blocked_mutation_path_patterns",
        "allowed_mutation_path_prefixes",
        "blocked_source_tags",
        "review_required_impacts",
        "review_required_action_kinds",
        "owner_precedence",
    ]
    for key in required_keys:
        if key not in contract:
            errors.append(f"contract missing {key!r}")

    for key in [
        "dedupe_window_size",
        "loop_block_threshold",
        "recursion_block_threshold",
        "cooldown_turns",
        "cooldown_seconds",
    ]:
        value = contract.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"contract {key!r} must be a non-negative integer")

    for key in [
        "protected_path_patterns",
        "blocked_mutation_path_patterns",
        "allowed_mutation_path_prefixes",
        "blocked_source_tags",
        "review_required_impacts",
        "review_required_action_kinds",
        "owner_precedence",
    ]:
        value = contract.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(f"contract {key!r} must be a list of strings")

    for impact in contract.get("review_required_impacts", []):
        if impact not in ALLOWED_IMPACTS:
            errors.append(f"contract review_required_impacts contains invalid value {impact!r}")

    return errors


def validate_state_data(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_keys = [
        "schema_version",
        "updated_at",
        "next_allowed_turn",
        "next_allowed_at",
        "last_review_result",
        "recent_fingerprints",
    ]
    for key in required_keys:
        if key not in state:
            errors.append(f"state missing {key!r}")

    if state.get("updated_at"):
        try:
            parse_datetime(state["updated_at"])
        except ValueError as exc:
            errors.append(f"state.updated_at invalid: {exc}")

    next_allowed_at = state.get("next_allowed_at")
    if next_allowed_at is not None:
        try:
            parse_datetime(next_allowed_at)
        except ValueError as exc:
            errors.append(f"state.next_allowed_at invalid: {exc}")

    next_allowed_turn = state.get("next_allowed_turn")
    if next_allowed_turn is not None and not isinstance(next_allowed_turn, int):
        errors.append("state.next_allowed_turn must be null or integer")

    review = state.get("last_review_result")
    if not isinstance(review, dict):
        errors.append("state.last_review_result must be an object")
    else:
        for key in ["turn_id", "status", "timestamp"]:
            if key not in review:
                errors.append(f"state.last_review_result missing {key!r}")

    recent = state.get("recent_fingerprints")
    if not isinstance(recent, list):
        errors.append("state.recent_fingerprints must be a list")
    else:
        for index, item in enumerate(recent):
            if not isinstance(item, dict):
                errors.append(f"state.recent_fingerprints[{index}] must be an object")
                continue
            for key in [
                "fingerprint",
                "count",
                "last_seen_at",
                "last_turn_id",
                "owner",
                "source_tag",
                "action_kind",
            ]:
                if key not in item:
                    errors.append(f"state.recent_fingerprints[{index}] missing {key!r}")
    return errors


def validate_guardrail_events(events: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    required_keys = [
        "schema_version",
        "timestamp",
        "turn_id",
        "fingerprint",
        "decision",
        "reasons",
        "owner",
        "source_tag",
        "action_kind",
        "path_buckets",
        "duplicate_count",
    ]
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"guardrail event {index} must be an object")
            continue
        for key in required_keys:
            if key not in event:
                errors.append(f"guardrail event {index} missing {key!r}")
        if event.get("decision") not in ALLOWED_DECISIONS:
            errors.append(f"guardrail event {index} has invalid decision {event.get('decision')!r}")
        if not isinstance(event.get("reasons"), list) or not all(
            isinstance(item, str) for item in event.get("reasons", [])
        ):
            errors.append(f"guardrail event {index} reasons must be a list of strings")
        if not isinstance(event.get("path_buckets"), list) or not all(
            isinstance(item, str) for item in event.get("path_buckets", [])
        ):
            errors.append(f"guardrail event {index} path_buckets must be a list of strings")
    return errors


def _validate_candidate(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ["turn_id", "host_id", "owner", "source_tag", "action_kind", "intent_summary"]:
        if not candidate.get(key):
            errors.append(f"candidate missing {key!r}")
    if candidate.get("impact") and candidate["impact"] not in ALLOWED_IMPACTS:
        errors.append(f"candidate impact must be one of {sorted(ALLOWED_IMPACTS)}")
    if "path_targets" in candidate and (
        not isinstance(candidate["path_targets"], list)
        or not all(isinstance(item, str) for item in candidate["path_targets"])
    ):
        errors.append("candidate path_targets must be a list of strings")
    return errors


def _normalize_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(candidate)
    normalized.setdefault("path_targets", [])
    normalized.setdefault("impact", "low")
    normalized.setdefault("mutation_requested", normalized.get("action_kind") in {"mutation", "sync", "upstream-sync"})
    normalized.setdefault("review_requested", False)
    normalized.setdefault("timestamp", now_iso())
    return normalized


def build_fingerprint(candidate: dict[str, Any]) -> str:
    signature = "||".join(
        [
            normalize_text(candidate.get("intent_summary", "")),
            candidate.get("host_id", ""),
            candidate.get("owner", ""),
            candidate.get("source_tag", ""),
            candidate.get("action_kind", ""),
            "|".join(sorted(bucket_path(path) for path in candidate.get("path_targets", []))),
        ]
    )
    return sha256_text(signature)


def _escalate(current: str, candidate: str) -> str:
    if DECISION_ORDER[candidate] > DECISION_ORDER[current]:
        return candidate
    return current


def _match_patterns(path: str, patterns: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def _cooldown_reasons(candidate: dict[str, Any], state: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    next_allowed_at = state.get("next_allowed_at")
    if next_allowed_at:
        current_time = parse_datetime(candidate["timestamp"])
        if current_time < parse_datetime(next_allowed_at):
            reasons.append(f"cooldown active until {next_allowed_at}")

    next_allowed_turn = state.get("next_allowed_turn")
    if next_allowed_turn is not None and candidate.get("turn_index") is not None:
        if candidate["turn_index"] < next_allowed_turn:
            reasons.append(f"turn cooldown active until turn_index {next_allowed_turn}")
    return reasons


def _bump_recent_fingerprints(
    state: dict[str, Any],
    fingerprint: str,
    candidate: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[int, list[dict[str, Any]]]:
    prior_count = 0
    recent: list[dict[str, Any]] = []
    for item in state.get("recent_fingerprints", []):
        if item.get("fingerprint") == fingerprint:
            prior_count = int(item.get("count", 0))
            continue
        recent.append(item)

    entry = {
        "fingerprint": fingerprint,
        "count": prior_count + 1,
        "last_seen_at": candidate["timestamp"],
        "last_turn_id": candidate["turn_id"],
        "owner": candidate["owner"],
        "source_tag": candidate["source_tag"],
        "action_kind": candidate["action_kind"],
    }
    recent.append(entry)
    window_size = contract["dedupe_window_size"]
    if window_size >= 0:
        recent = recent[-window_size:] if window_size else []
    return entry["count"], recent


def check_guardrails(
    candidate: dict[str, Any],
    contract: dict[str, Any],
    state: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    errors = validate_contract_data(contract) + validate_state_data(state) + _validate_candidate(candidate)
    if errors:
        raise ValueError("; ".join(errors))

    normalized = _normalize_candidate(candidate)
    decision = "pass"
    reasons: list[str] = []
    fingerprint = build_fingerprint(normalized)
    duplicate_count, recent_fingerprints = _bump_recent_fingerprints(state, fingerprint, normalized, contract)

    if normalized["source_tag"] in contract["blocked_source_tags"]:
        decision = _escalate(decision, "block")
        reasons.append(f"source_tag {normalized['source_tag']!r} is blocked")

    for reason in _cooldown_reasons(normalized, state):
        decision = _escalate(decision, "block" if normalized["mutation_requested"] else "observe-only")
        reasons.append(reason)

    if duplicate_count > 1:
        decision = _escalate(decision, "observe-only")
        reasons.append(f"duplicate fingerprint seen {duplicate_count} times in the dedupe window")

    if duplicate_count >= contract["recursion_block_threshold"] and normalized["source_tag"].startswith("my-way"):
        decision = _escalate(decision, "block")
        reasons.append("anti-recursion threshold reached for my-way generated output")

    if duplicate_count >= contract["loop_block_threshold"]:
        decision = _escalate(decision, "block")
        reasons.append("anti-loop threshold reached")

    if normalized["mutation_requested"]:
        blocked_hits = [
            path
            for path in normalized["path_targets"]
            if _match_patterns(path, contract["blocked_mutation_path_patterns"])
        ]
        if blocked_hits:
            decision = _escalate(decision, "block")
            reasons.append(f"mutation matches blocked paths: {blocked_hits}")

        protected_hits = [
            path
            for path in normalized["path_targets"]
            if _match_patterns(path, contract["protected_path_patterns"])
        ]
        if protected_hits and not normalized["review_requested"]:
            decision = _escalate(decision, "review-required")
            reasons.append(f"mutation touches protected asset path: {protected_hits}")

        allowlist = contract["allowed_mutation_path_prefixes"]
        if allowlist:
            off_allowlist = [
                path for path in normalized["path_targets"] if not any(path.startswith(prefix) for prefix in allowlist)
            ]
            if off_allowlist:
                decision = _escalate(decision, "review-required")
                reasons.append(f"mutation is outside the allowlist: {off_allowlist}")

    if normalized["impact"] in contract["review_required_impacts"] and not normalized["review_requested"]:
        decision = _escalate(decision, "review-required")
        reasons.append(f"impact {normalized['impact']!r} requires review")

    if normalized["action_kind"] in contract["review_required_action_kinds"] and not normalized["review_requested"]:
        decision = _escalate(decision, "review-required")
        reasons.append(f"action_kind {normalized['action_kind']!r} requires review")

    if normalized["mutation_requested"] and normalized["owner"] != "my-way" and not normalized["review_requested"]:
        decision = _escalate(decision, "review-required")
        reasons.append(f"cross-owner mutation requires review for owner {normalized['owner']!r}")

    if not reasons:
        reasons.append("passed all guardrail checks")

    now_dt = parse_datetime(normalized["timestamp"])
    new_state = copy.deepcopy(state)
    new_state["updated_at"] = normalized["timestamp"]
    new_state["next_allowed_at"] = (now_dt + timedelta(seconds=contract["cooldown_seconds"])).isoformat(
        timespec="seconds"
    )
    if normalized.get("turn_index") is not None:
        new_state["next_allowed_turn"] = normalized["turn_index"] + contract["cooldown_turns"]
    new_state["recent_fingerprints"] = recent_fingerprints

    if decision == "review-required":
        new_state["last_review_result"] = {
            "turn_id": normalized["turn_id"],
            "status": "pending",
            "timestamp": normalized["timestamp"],
        }
    elif normalized["review_requested"] and decision == "pass":
        new_state["last_review_result"] = {
            "turn_id": normalized["turn_id"],
            "status": "approved",
            "timestamp": normalized["timestamp"],
        }

    event_record = {
        "schema_version": "v0.1",
        "timestamp": normalized["timestamp"],
        "turn_id": normalized["turn_id"],
        "fingerprint": fingerprint,
        "decision": decision,
        "reasons": reasons,
        "owner": normalized["owner"],
        "source_tag": normalized["source_tag"],
        "action_kind": normalized["action_kind"],
        "path_buckets": [bucket_path(path) for path in normalized["path_targets"]],
        "duplicate_count": duplicate_count,
    }
    result = {
        "decision": decision,
        "fingerprint": fingerprint,
        "duplicate_count": duplicate_count,
        "reasons": reasons,
        "next_allowed_at": new_state.get("next_allowed_at"),
        "next_allowed_turn": new_state.get("next_allowed_turn"),
    }
    return result, new_state, event_record


def persist_guardrail_check(state_path: Path, events_path: Path, new_state: dict[str, Any], event_record: dict[str, Any]) -> None:
    write_json(state_path, new_state)
    append_jsonl(events_path, event_record)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="My-Way guardrail enforcement")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="evaluate one candidate action against guardrails")
    check_parser.add_argument("--input-json", required=True)
    check_parser.add_argument(
        "--contract-path",
        default=str(RUNTIME_ROOT / "guardrails" / "guardrails.contract.json"),
    )
    check_parser.add_argument(
        "--state-path",
        default=str(RUNTIME_ROOT / "guardrails" / "guardrails.state.json"),
    )
    check_parser.add_argument(
        "--events-path",
        default=str(RUNTIME_ROOT / "guardrails" / "guardrails.events.jsonl"),
    )
    check_parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command != "check":
        parser.error(f"unsupported command: {args.command}")

    candidate = load_json(Path(args.input_json))
    contract = load_json(Path(args.contract_path))
    state = load_json(Path(args.state_path))
    result, new_state, event_record = check_guardrails(candidate, contract, state)
    if not args.no_write:
        persist_guardrail_check(Path(args.state_path), Path(args.events_path), new_state, event_record)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
