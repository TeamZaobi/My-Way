from __future__ import annotations

import argparse
from pathlib import Path

from enforce_guardrails import validate_contract_data, validate_guardrail_events, validate_state_data
from schema_utils import MYWAY_ROOT, load_json, load_jsonl, validate_path_against_schema


def collect_bundle_errors(root: Path) -> list[str]:
    runtime_root = root / "runtime"
    pairs = [
        (
            runtime_root / "examples" / "turn.events.jsonl",
            runtime_root / "schemas" / "turn-event.schema.json",
        ),
        (
            runtime_root / "examples" / "turn.note.json",
            runtime_root / "schemas" / "turn-note.schema.json",
        ),
        (
            runtime_root / "examples" / "reflection.exchange.packet.json",
            runtime_root / "schemas" / "reflection-exchange-packet.schema.json",
        ),
        (
            runtime_root / "bridge" / "examples" / "reflection-triage-audit.jsonl",
            runtime_root / "bridge" / "reflection-triage-audit.schema.json",
        ),
    ]

    errors: list[str] = []
    for instance_path, schema_path in pairs:
        errors.extend(validate_path_against_schema(instance_path, schema_path))

    contract_path = runtime_root / "guardrails" / "guardrails.contract.json"
    state_path = runtime_root / "guardrails" / "guardrails.state.json"
    events_path = runtime_root / "guardrails" / "guardrails.events.jsonl"

    for error in validate_contract_data(load_json(contract_path)):
        errors.append(f"{contract_path}: {error}")
    for error in validate_state_data(load_json(state_path)):
        errors.append(f"{state_path}: {error}")
    for error in validate_guardrail_events(load_jsonl(events_path)):
        errors.append(f"{events_path}: {error}")
    return errors


def _print_result(errors: list[str]) -> int:
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print("OK My-Way runtime bundle validation passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate My-Way runtime artifacts")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bundle_parser = subparsers.add_parser("bundle", help="validate the checked-in My-Way runtime bundle")
    bundle_parser.add_argument("--root", default=str(MYWAY_ROOT))

    instance_parser = subparsers.add_parser("instance", help="validate one JSON or JSONL file against one schema")
    instance_parser.add_argument("--instance-path", required=True)
    instance_parser.add_argument("--schema-path", required=True)

    guardrails_parser = subparsers.add_parser("guardrails", help="validate guardrail contract, state, and events")
    guardrails_parser.add_argument("--root", default=str(MYWAY_ROOT))
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "bundle":
        return _print_result(collect_bundle_errors(Path(args.root)))

    if args.command == "instance":
        return _print_result(
            validate_path_against_schema(Path(args.instance_path), Path(args.schema_path))
        )

    if args.command == "guardrails":
        root = Path(args.root)
        contract_path = root / "runtime" / "guardrails" / "guardrails.contract.json"
        state_path = root / "runtime" / "guardrails" / "guardrails.state.json"
        events_path = root / "runtime" / "guardrails" / "guardrails.events.jsonl"
        errors: list[str] = []
        for error in validate_contract_data(load_json(contract_path)):
            errors.append(f"{contract_path}: {error}")
        for error in validate_state_data(load_json(state_path)):
            errors.append(f"{state_path}: {error}")
        for error in validate_guardrail_events(load_jsonl(events_path)):
            errors.append(f"{events_path}: {error}")
        return _print_result(errors)

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
