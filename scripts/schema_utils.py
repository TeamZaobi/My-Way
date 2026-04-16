from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
MYWAY_ROOT = SCRIPT_DIR.parent
RUNTIME_ROOT = MYWAY_ROOT / "runtime"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[Any]:
    records: list[Any] = []
    if not path.exists():
        return records
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def write_json(path: Path, data: Any) -> None:
    ensure_parent(path)
    path.write_text(dump_json(data), encoding="utf-8")


def append_jsonl(path: Path, record: Any) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split()).lower()


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def bucket_path(path: str) -> str:
    normalized = path.replace("\\", "/").rstrip("/")
    if normalized.endswith("/SKILL.md") or normalized.endswith("SKILL.md"):
        return "skill"
    if "/references/" in normalized:
        return "references"
    if "/runtime/schemas/" in normalized:
        return "runtime/schemas"
    if "/runtime/bridge/" in normalized:
        return "runtime/bridge"
    if "/runtime/guardrails/" in normalized:
        return "runtime/guardrails"
    parts = [part for part in normalized.split("/") if part]
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return normalized or "."


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type and not _matches_type(instance, expected_type):
        errors.append(f"{path}: expected {expected_type}, got {type(instance).__name__}")
        return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']}, got {instance!r}")

    if expected_type == "object":
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        additional_properties = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_instance(value, properties[key], f"{path}.{key}"))
            elif additional_properties is False:
                errors.append(f"{path}: unexpected property {key!r}")

    if expected_type == "array":
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, got {len(instance)}")
        if max_items is not None and len(instance) > max_items:
            errors.append(f"{path}: expected at most {max_items} items, got {len(instance)}")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                errors.extend(validate_instance(item, item_schema, f"{path}[{index}]"))

    if expected_type == "string":
        min_length = schema.get("minLength")
        if min_length is not None and len(instance) < min_length:
            errors.append(f"{path}: expected string length >= {min_length}")
        if schema.get("format") == "date-time":
            try:
                parse_datetime(instance)
            except ValueError as exc:
                errors.append(f"{path}: invalid date-time value {instance!r}: {exc}")

    return errors


def validate_path_against_schema(instance_path: Path, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    errors: list[str] = []
    if instance_path.suffix == ".jsonl":
        for index, record in enumerate(load_jsonl(instance_path), start=1):
            for error in validate_instance(record, schema):
                errors.append(f"{instance_path}:{index}: {error}")
    else:
        for error in validate_instance(load_json(instance_path), schema):
            errors.append(f"{instance_path}: {error}")
    return errors
