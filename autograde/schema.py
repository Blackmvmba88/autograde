from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "exam.schema.json"
with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
    EXAM_SCHEMA: dict[str, Any] = json.load(fh)


def load_exam(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_exam(exam: dict[str, Any], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as fh:
        json.dump(exam, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def validate_exam_structure(exam: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _validate_object(exam, EXAM_SCHEMA, errors, path="exam")
    return errors


def normalize_exam(exam: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(exam))
    scoring = normalized.get("scoring")
    questions = normalized.get("questions", [])

    if scoring is None:
        total_points = sum(float(question.get("points", 1)) for question in questions)
        normalized["scoring"] = {
            "mode": "points_per_question",
            "max_points": round(total_points, 2),
        }
    elif "max_points" not in scoring:
        total_points = sum(float(question.get("points", 1)) for question in questions)
        scoring["max_points"] = round(total_points, 2)

    if "format" not in normalized:
        normalized["format"] = "quiz"

    return normalized


def _validate_object(instance: Any, schema: dict[str, Any], errors: list[str], path: str) -> None:
    schema_type = schema.get("type")
    if schema_type == "object":
        if not isinstance(instance, dict):
            errors.append(f"{path}: must be an object")
            return
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required field '{key}'")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key not in properties:
                if schema.get("additionalProperties", True) is False:
                    errors.append(f"{path}.{key}: additional property not allowed")
                continue
            _validate_object(value, properties[key], errors, f"{path}.{key}")

        if "allOf" in schema:
            for rule in schema["allOf"]:
                _validate_condition(instance, rule, errors, path)
        return

    if schema_type == "array":
        if not isinstance(instance, list):
            errors.append(f"{path}: must be an array")
            return
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: must contain at least {min_items} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                _validate_object(item, item_schema, errors, f"{path}[{index}]")
        return

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']}")

    if schema_type == "string":
        if not isinstance(instance, str):
            errors.append(f"{path}: must be a string")
            return
        min_length = schema.get("minLength")
        if min_length and len(instance) < min_length:
            errors.append(f"{path}: must have length at least {min_length}")
    elif schema_type == "number":
        if not isinstance(instance, (int, float)) or isinstance(instance, bool):
            errors.append(f"{path}: must be a number")
            return
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            errors.append(f"{path}: must be >= {minimum}")
    elif schema_type == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            errors.append(f"{path}: must be an integer")
            return
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            errors.append(f"{path}: must be >= {minimum}")
    elif isinstance(schema_type, list):
        if not any(_type_matches(instance, item_type) for item_type in schema_type):
            errors.append(f"{path}: has unsupported type")
    elif schema_type == "boolean":
        if not isinstance(instance, bool):
            errors.append(f"{path}: must be a boolean")


def _type_matches(instance: Any, schema_type: str) -> bool:
    return (
        (schema_type == "string" and isinstance(instance, str))
        or (schema_type == "number" and isinstance(instance, (int, float)) and not isinstance(instance, bool))
        or (schema_type == "integer" and isinstance(instance, int) and not isinstance(instance, bool))
        or (schema_type == "boolean" and isinstance(instance, bool))
        or (schema_type == "object" and isinstance(instance, dict))
        or (schema_type == "array" and isinstance(instance, list))
        or (schema_type == "null" and instance is None)
    )


def _validate_condition(instance: dict[str, Any], rule: dict[str, Any], errors: list[str], path: str) -> None:
    condition = rule.get("if", {})
    then = rule.get("then", {})
    if _matches_condition(instance, condition):
        required = then.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required field '{key}'")


def _matches_condition(instance: dict[str, Any], condition: dict[str, Any]) -> bool:
    properties = condition.get("properties", {})
    for key, expected_schema in properties.items():
        if key not in instance:
            return False
        value = instance[key]
        if "const" in expected_schema and value != expected_schema["const"]:
            return False
        if "enum" in expected_schema and value not in expected_schema["enum"]:
            return False
    return True
